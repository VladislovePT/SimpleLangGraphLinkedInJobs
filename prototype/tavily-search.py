import os
import requests
from langchain_core.tools import tool

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

resp = requests.post(
    "https://api.tavily.com/search",
    headers={"Authorization": f"Bearer {TAVILY_API_KEY}"},
    json={"query": 'Sysmatch', "max_results": 1}
)
resp.raise_for_status()

data = resp.json()
print("\n".join([r["content"] for r in data.get("results", [])]))