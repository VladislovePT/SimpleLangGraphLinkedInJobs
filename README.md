# LinkedIn Job Search and Analysis Agent

This project implements a sophisticated agent based on LangGraph that automates the process of searching for jobs on LinkedIn, analyzing their fit against a predefined user profile, and documenting the findings.

## Features

- **Automated Job Searching**: Connects to a LinkedIn MCP (Multi-Channel Proxy) server to perform job searches using a variety of queries.
- **Dynamic Queries**: Automatically runs with a randomly selected, high-value job query if no specific query is provided.
- **AI-Powered Analysis**: Uses a GPT model (`gpt-4o-mini`) to analyze job descriptions against a detailed user profile (`profile.json`).
- **Markdown Newsletter Generation**: Produces a weekly-style newsletter in Markdown format, including a table that summarizes the job fit, required skills, and consultancy status.
- **Azure DevOps Integration**: Automatically appends the generated analysis to a specified page in an Azure DevOps wiki.
- **Configuration-Driven**: All sensitive keys, URLs, and configuration parameters are managed via a `.env` file for security and flexibility.

## Project Structure

The project follows the standard application structure recommended by the LangChain documentation.

```
AI/
├── linkedin_agent/         # Main application package
│   ├── mcp-client-agent.py # The main LangGraph agent implementation
│   ├── model/              # Contains the user profile and tool configurations
│   ├── prompts/            # Contains the prompt templates for the agent
│   └── tools/              # Houses custom tools (e.g., for DevOps wiki interaction)
├── .env                    # Your local environment variables (credentials, URLs)
├── .env.example            # Template for the .env file
├── .gitignore              # Standard Python gitignore
├── requirements.txt        # Project dependencies
└── ...
```

## Setup and Installation

1.  **Clone the Repository**: Clone this project to your local machine.

2.  **Create a Virtual Environment**: It is highly recommended to use a Python virtual environment.

    ```bash
    python -m venv .ai-venv
    source .ai-venv/bin/activate
    ```

3.  **Install Dependencies**: Install all the required packages from the `requirements.txt` file.

    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1.  **Create `.env` file**: Create a `.env` file in the project root by copying the template.

    ```bash
    cp .env.example .env
    ```

2.  **Edit `.env` file**: Open the newly created `.env` file and fill in the placeholder values. You will need:
    - Your **OpenAI API Key**.
    - Your **Tavily API Key** for search functions.
    - Your **Azure DevOps Personal Access Token (PAT)** with Wiki read/write permissions.
    - The URL of your running **LinkedIn MCP server**.
    - Your Azure DevOps `ORGANIZATION`, `PROJECT`, `WIKI_ID`, and the `PAGE_PATH` you want to write to.
    - *(Optional)* Your LangSmith API keys if you wish to use LangSmith for tracing.

## Usage

To run the agent, execute the main script from the project's root directory:

```bash
python linkedin_agent/mcp-client-agent.py
```

-   **Interactive Mode**: The script will prompt you to enter a job query. You can type any job search string you like.
-   **Automated Mode**: If you simply press `Enter` at the prompt without typing a query, the agent will automatically select a random, high-value query from the list defined in `linkedin_agent/prompts/prompts.py` and run with it.

Upon completion, the agent will print the final analysis to the console and append it to the configured Azure DevOps wiki page.
