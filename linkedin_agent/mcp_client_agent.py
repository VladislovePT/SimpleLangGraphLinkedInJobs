import asyncio
import json
import sys
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import ToolMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage
from datetime import datetime
import random

from linkedin_agent.prompts import prompts
from linkedin_agent.tools.tavily_search_tools import search_company
from linkedin_agent.tools.handlers.tool_handlers import (
    handle_close_session,
    handle_get_company_profile,
    handle_get_job_details,
    handle_get_person_profile,
    handle_get_recommended_jobs,
    handle_search_jobs,
)
from linkedin_agent.tools import append_to_wiki_page
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
TOOL_CONFIG_PATH = os.getenv("TOOL_CONFIG_PATH")
PROFILE_JSON_PATH = os.getenv("PROFILE_JSON_PATH")
LINKEDIN_MCP_URL = os.getenv("LINKEDIN_MCP_URL")

# Azure DevOps Wiki Configuration
ORGANIZATION = os.getenv("ORGANIZATION")
PROJECT = os.getenv("PROJECT")
WIKI_ID = os.getenv("WIKI_ID")
PAGE_PATH = os.getenv("PAGE_PATH")

def create_mcp_client():
    """Initializes and returns the MultiServerMCPClient."""
    return MultiServerMCPClient({
        "linkedinmcp": {
            "url": LINKEDIN_MCP_URL,
            "transport": "streamable_http",
        }
    })


async def setup_tools_and_model(client, model):
    """Fetches tool configurations, sets up tools, and binds them to the model."""
    with open(TOOL_CONFIG_PATH, 'r') as f:
        tool_config = json.load(f)

    unrestricted_tool_names = {
        tool['name']
        for tool_group in tool_config.values()
        for tool in tool_group
        if not tool.get('restricted', False)
    }

    client_tools = await client.get_tools()
    tools = [tool for tool in client_tools if tool.name in unrestricted_tool_names]

    if search_company.name in unrestricted_tool_names:
        tools.append(search_company)

    model_with_tools = model.bind_tools(tools)
    tool_node = ToolNode(tools)
    return model_with_tools, tool_node


def should_continue(state: MessagesState):
    """Determines whether to continue the graph execution or end."""
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END


def route_tool_call(state: MessagesState):
    """Routes tool calls to the appropriate handler node."""
    last_message = state["messages"][-1]
    if not isinstance(last_message, ToolMessage):
        return END

    tool_map = {
        "close_session": "handle_close_session",
        "get_company_profile": "handle_get_company_profile",
        "get_job_details": "handle_get_job_details",
        "get_person_profile": "handle_get_person_profile",
        "get_recommended_jobs": "handle_get_recommended_jobs",
        "search_jobs": "handle_search_jobs",
    }
    return tool_map.get(last_message.name, END)


async def analyze_job_matches(state: MessagesState):
    """
    Analyzes job search results against a user profile by iterating through each job,
    invoking the analysis model for each one concurrently to get an HTML block,
    and compiling the results into a single JSON array for the RSS feed.
    """
    print("\n--- Analyzing Job Matches ---")
    last_message = state["messages"][-1]

    if not hasattr(last_message, 'content') or not isinstance(last_message.content, str):
        return {"messages": [AIMessage(content="I couldn't find any job results to analyze.")]}

    jobs_json_str = last_message.content
    try:
        jobs_data = json.loads(jobs_json_str)
        if not isinstance(jobs_data, list):
            jobs_data = [jobs_data] if isinstance(jobs_data, dict) else []
    except (json.JSONDecodeError, TypeError):
        error_content = "I couldn't analyze the job results because I received invalid data from the search tool."
        return {"messages": [AIMessage(content=error_content)]}

    if not jobs_data:
        return {"messages": [AIMessage(content="No valid jobs found to analyze.")]}

    # Load user profile
    try:
        with open(PROFILE_JSON_PATH, 'r') as f:
            profile_data = json.load(f)
    except FileNotFoundError:
        return {"messages": [AIMessage(content=f"Error: Your profile file was not found at {PROFILE_JSON_PATH}.")]}
    except json.JSONDecodeError:
        return {"messages": [AIMessage(content=f"Error: I couldn't read your profile file at {PROFILE_JSON_PATH}.")]}

    today = datetime.today().strftime("%B %d, %Y")
    analysis_model = init_chat_model(MODEL_NAME)
    compiled_responses = []
    
    analysis_tasks = []
    for job in jobs_data:
        formatted_prompt = prompts.job_match_prompt.format(
            profile=json.dumps(profile_data, indent=2),
            job=json.dumps(job, indent=2),
            date=today
        )
        analysis_tasks.append(analysis_model.ainvoke(formatted_prompt))

    print(f"--- Starting analysis of {len(analysis_tasks)} jobs concurrently ---")
    analysis_results = await asyncio.gather(*analysis_tasks, return_exceptions=True)

    for i, result in enumerate(analysis_results):
        job = jobs_data[i]
        company_name = job.get('company', 'Unknown Company')
        job_title = job.get('job_title', 'N/A')
        job_identifier = f"{job_title} at {company_name}"
        
        html_content = ""
        
        if isinstance(result, Exception):
            print(f"--- Error analyzing job: {job_identifier} ---")
            print(f"Exception: {result}")
            html_content = f"<h2>Error analyzing job: {job_title}</h2><p>An exception occurred during analysis: {result}</p>"
        else:
            print(f"--- Successfully processed analysis for job: {job_identifier} ---")
            html_content = result.content

        compiled_responses.append({
            "job_title": f"{job_title}",
            "job_html": html_content
        })

    final_content = json.dumps(compiled_responses, indent=2)
    analysis_result_message = AIMessage(content=final_content)
    return {"messages": [analysis_result_message]}


def build_graph(call_model_node, tool_node):
    """Builds and compiles the LangGraph StateGraph."""
    builder = StateGraph(MessagesState)
    builder.add_node("call_model", call_model_node)
    builder.add_node("tools", tool_node)

    # Add tool handler nodes
    handler_nodes = {
        "handle_close_session": handle_close_session,
        "handle_get_company_profile": handle_get_company_profile,
        "handle_get_job_details": handle_get_job_details,
        "handle_get_person_profile": handle_get_person_profile,
        "handle_get_recommended_jobs": handle_get_recommended_jobs,
        "handle_search_jobs": handle_search_jobs,
    }
    for name, node in handler_nodes.items():
        builder.add_node(name, node)

    # Add the new analysis node
    builder.add_node("analyze_job_matches", analyze_job_matches)

    # Define edges
    builder.add_edge(START, "call_model")
    builder.add_conditional_edges("call_model", should_continue)

    # The tools node routes to the conditional function
    conditional_mapping = {name: name for name in handler_nodes}
    conditional_mapping[END] = END
    builder.add_conditional_edges("tools", route_tool_call, conditional_mapping)

    # Connect handler nodes
    for name in handler_nodes:
        if name == "handle_search_jobs":
            # After searching jobs, analyze the matches
            builder.add_edge(name, "analyze_job_matches")
        else:
            # Other handlers go back to the main model
            builder.add_edge(name, "call_model")

    # The analysis node ends the graph execution
    builder.add_edge("analyze_job_matches", END)

    return builder.compile()


async def run_agent():
    """Runs the agent to get job analysis and returns the content."""
    # 1. Initialize model and client
    model = init_chat_model(MODEL_NAME)
    client = create_mcp_client()

    # 2. Setup tools and bind to model
    model_with_tools, tool_node = await setup_tools_and_model(client, model)

    # 3. Define the model calling node (closure to capture model_with_tools)
    async def call_model(state: MessagesState):
        """Invokes the model with the current state."""
        messages = state["messages"]
        response = await model_with_tools.ainvoke(messages)
        return {"messages": [response]}

    # 4. Build the graph
    graph = build_graph(call_model, tool_node)

    # 5. Use a default or random query
    if isinstance(prompts.jobs_query, list) and prompts.jobs_query:
        user_query = random.choice(prompts.jobs_query)
    else:
        user_query = "AI Engineer" # Fallback

    final_state = await graph.ainvoke(
        {"messages": [{"role": "user", "content": f"search for jobs using the following query: {user_query}"}]}
    )

    response = final_state['messages'][-1].content
    return response