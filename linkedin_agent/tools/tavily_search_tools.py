import os
import requests
from langchain_core.tools import tool

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# --- Tool definition ---
@tool
def search_company(query: str) -> str:
    """Search Tavily for information about a company."""
    resp = requests.post(
        "https://api.tavily.com/search",
        headers={"Authorization": f"Bearer {TAVILY_API_KEY}"},
        json={"query": f"who are {query} as a company", "max_results": 1, "include_answer": "advanced"}
    )
    resp.raise_for_status()
    data = resp.json()
    return data['answer']
    # return "\n".join([r["content"] for r in data.get("results", [])])
