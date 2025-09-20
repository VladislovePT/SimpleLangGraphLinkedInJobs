import requests
import base64
import os
import json
from langchain_core.tools import tool

def _get_page_details(org: str, proj: str, wiki_id: str, path: str, pat: str) -> dict:
    """Fetches the current content and ETag of a specific wiki page."""
    url = f"https://dev.azure.com/{org}/{proj}/_apis/wiki/wikis/{wiki_id}/pages?path={path}&includeContent=true&api-version=6.0"
    b64_pat = base64.b64encode(f':{pat}'.encode('ascii')).decode('ascii')
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Basic {b64_pat}'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        page_data = response.json()
        etag = response.headers["ETag"]
        return {
            "success": True,
            "content": page_data.get("content", ""),
            "etag": etag,
            "message": f"Successfully fetched page '{path}'."
        }
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return {
                "success": True, # Success in the sense that we can proceed to create a page
                "content": "",
                "etag": None,
                "message": f"Page '{path}' not found. A new page will be created."
            }
        else:
            return {
                "success": False,
                "content": None,
                "etag": None,
                "message": f"Error fetching page: {e}. Response: {e.response.text}"
            }
    except Exception as e:
        return {
            "success": False,
            "content": None,
            "etag": None,
            "message": f"An unexpected error occurred while fetching the page: {e}"
        }

def _update_page(org: str, proj: str, wiki_id: str, path: str, new_content: str, etag: str | None, pat: str) -> str:
    """Updates or creates a wiki page with the new content."""
    url = f"https://dev.azure.com/{org}/{proj}/_apis/wiki/wikis/{wiki_id}/pages?path={path}&api-version=6.0"
    b64_pat = base64.b64encode(f':{pat}'.encode('ascii')).decode('ascii')
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Basic {b64_pat}'
    }
    if etag:
        headers['If-Match'] = etag

    body = {"content": new_content}

    try:
        response = requests.put(url, headers=headers, data=json.dumps(body))
        response.raise_for_status()
        if etag:
            return f"Successfully appended text to page '{path}'."
        else:
            return f"Successfully created and wrote content to new page '{path}'."
    except requests.exceptions.RequestException as e:
        return f"Error updating page: {e}. Response: {e.response.text}"


# @tool
def append_to_wiki_page(
    content_to_append: str,
    page_path: str,
    organization: str,
    project: str,
    wiki_identifier: str
) -> str:
    """
    Appends content to a specified Azure DevOps wiki page.
    Requires the AZURE_DEVOPS_PAT environment variable to be set.

    Args:
        content_to_append: The text content to add to the end of the page.
        page_path: The path of the page to edit (e.g., '/My-Page' or '/Folder/Sub-Page').
        organization: The Azure DevOps organization name.
        project: The Azure DevOps project name.
        wiki_identifier: The name or ID of the wiki.
    """
    pat = os.getenv("AZURE_DEVOPS_PAT")
    if not pat:
        return "Error: AZURE_DEVOPS_PAT environment variable not set."

    details = _get_page_details(organization, project, wiki_identifier, page_path, pat)

    if not details["success"]:
        return f"Failed to get page details: {details['message']}"

    current_content = details["content"]
    etag = details["etag"]
    new_content = current_content + content_to_append

    result = _update_page(organization, project, wiki_identifier, page_path, new_content, etag, pat)
    return result
