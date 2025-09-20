import json
import random
import time
from langgraph.graph import MessagesState
from linkedin_agent.tools.tavily_search_tools import search_company
from linkedin_agent.tools.linkedin_requests import retrieve_job_details

# A method to iterate and append a property
def process_jobs(objects):
    if isinstance(objects, list):
        for obj in objects:
            if isinstance(obj, dict):
                delay = random.randint(3, 10)
                print(f"Waiting for {delay} seconds before processing next job...")
                time.sleep(delay)
                company_name:str = obj['company']
                obj['company_description'] = search_company(company_name)
                linkedin_url:str = obj['linkedin_url']
                obj['job_description'] = retrieve_job_details(linkedin_url)
    return objects

def handle_close_session(state: MessagesState):
    print("Handling close_session output")
    # Add your specific logic here
    # The last message is the tool output, you can process it here
    # For example, print the content of the tool output
    print(state["messages"][-1].content)
    return {"messages": state["messages"]}

def handle_get_company_profile(state: MessagesState):
    print("Handling get_company_profile output")
    # Add your specific logic here
    print(state["messages"][-1].content)
    return {"messages": state["messages"]}

def handle_get_job_details(state: MessagesState):
    print("Handling get_job_details output")
    # Add your specific logic here
    print(state["messages"][-1].content)
    return {"messages": state["messages"]}

def handle_get_person_profile(state: MessagesState):
    print("Handling get_person_profile output")
    # Add your specific logic here
    print(state["messages"][-1].content)
    return {"messages": state["messages"]}

def handle_get_recommended_jobs(state: MessagesState):
    print("Handling get_recommended_jobs output")
    # Add your specific logic here
    print(state["messages"][-1].content)
    return {"messages": state["messages"]}

def handle_search_jobs(state: MessagesState):
    print("Handling search_jobs output")
    last_message = state["messages"][-1]
    try:
        # The content is expected to be a JSON string of a list of objects.
        job_list = json.loads(str(last_message.content))
    except (json.JSONDecodeError, TypeError):
        print(f"Tool output for search_jobs is not valid JSON: {last_message.content}")
        return {"messages": state["messages"]}

    detailed_jobs = process_jobs(job_list)

    # Update the message content with the modified list.
    last_message.content = json.dumps(detailed_jobs, indent=2)

    print("Appended property to each job object:")
    print(last_message.content)
    return {"messages": state["messages"]}
