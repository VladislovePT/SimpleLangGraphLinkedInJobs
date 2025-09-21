# LinkedIn Job Analysis RSS Feed Agent

This project is a sophisticated Python agent that automates searching for LinkedIn jobs, analyzes them against a detailed user profile, and generates a local RSS feed with the findings. The agent runs on a schedule and logs its activities to a MySQL database.

## Features

- **Automated & Scheduled Job Searches**: Runs daily to find the latest job postings based on predefined queries.
- **AI-Powered Job Analysis**: Leverages a Large Language Model (via LangGraph) to compare job descriptions against a JSON-defined user profile.
- **Rich HTML Summaries**: Generates a visually appealing HTML card for each job, detailing the fit, matching skills, and missing skills.
- **Local RSS Feed**: Serves the analysis results as an Atom RSS feed, accessible locally via a Flask web server.
- **Database Logging**: Logs all agent activities, including job searches, analysis results, and errors, to a MySQL database for robust monitoring.
- **Log Maintenance**: Automatically clears the logs table weekly to manage database size.
- **Containerized**: Includes a `Dockerfile` for easy setup and deployment.

## Tech Stack

- **Backend**: Python
- **AI Agent Framework**: LangChain / LangGraph
- **Web Server**: Flask
- **Scheduling**: APScheduler
- **Database**: MySQL
- **Containerization**: Docker

## How It Works

The application is orchestrated by `rss_feed.py`, which serves as the main entry point.

1.  **Scheduler**: `APScheduler` is configured to run two main tasks:
    - **Daily Job Analysis**: The `update_rss_feed` function is triggered once every 48 hours. This function invokes the LangGraph agent (`mcp_client_agent.py`).
    - **Weekly Log Cleanup**: The `clear_logs` function runs once a week (Sunday at midnight) to truncate the `logs` table in the database.

2.  **LangGraph Agent**: The agent (`mcp_client_agent.py`) executes a series of steps:
    - It picks a random job query from a predefined list.
    - It calls an external LinkedIn service (MCP) to search for jobs.
    - For each job found, it invokes an LLM to perform a detailed analysis against the user's `profile.json`.
    - The analysis is formatted into a rich HTML block.

3.  **RSS Feed Generation**: The collected HTML analyses are compiled into an `rss.xml` file.

4.  **Flask Server**: A lightweight Flask server runs continuously to serve the generated `rss.xml` file at `http://localhost:5000/rss`.

## Setup and Installation

### Prerequisites

- Python 3.11+
- Docker (optional, for containerized deployment)
- A running MySQL server

### Local Setup

1.  **Clone the Repository**:
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Create and Activate a Virtual Environment**:
    ```bash
    python -m venv .ai-venv
    source .ai-venv/bin/activate
    # On Windows, use: .\ai-venv\Scripts\activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**:
    - Create a `.env` file by copying the example file:
      ```bash
      cp .env.example .env
      ```
    - Edit the `.env` file with your specific credentials and configurations.

## Environment Variables

Your `.env` file must contain the following variables:

- `DB_HOST`: The hostname or IP address of your MySQL server.
- `DB_USER`: The username for your MySQL database.
- `DB_PASSWORD`: The password for your MySQL database.
- `DB_NAME`: The name of the database to use.
- `MODEL_NAME`: The identifier for the language model to use (e.g., `gpt-4o-mini`).
- `TOOL_CONFIG_PATH`: Path to the tool configuration file (e.g., `linkedin_agent/model/mcp-tool-names.json`).
- `PROFILE_JSON_PATH`: Path to the user profile for job matching (e.g., `linkedin_agent/model/profile.json`).
- `LINKEDIN_MCP_URL`: The URL of your running LinkedIn MCP server.
- `OPENAI_API_KEY`: Your API key for OpenAI.

## Running the Application

You can run the application either directly with Python or using Docker.

### 1. Running Directly

Ensure your virtual environment is activated and your `.env` file is configured. Then, run the Flask application:

```bash
python rss_feed.py
```

The server will start, and the first job analysis will run immediately. Subsequent runs will follow the defined schedule.

### 2. Running with Docker

1.  **Build the Docker Image**:
    ```bash
    docker build -t linkedin-rss-agent .
    ```

2.  **Run the Docker Container**:
    You can pass your environment variables to the container using the `--env-file` flag.
    ```bash
    docker run -p 5000:5000 --env-file .env --name rss-agent-container linkedin-rss-agent
    ```

## Accessing the RSS Feed

Once the application is running, the RSS feed will be available at:

[http://localhost:5000/rss](http://localhost:5000/rss)

You can add this URL to your favorite RSS reader to get updates.