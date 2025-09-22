from flask import Flask, Response, send_from_directory
from feedgen.feed import FeedGenerator
import asyncio
import sys
import os
import random
import uuid
import json
from datetime import datetime
import pytz
from apscheduler.schedulers.background import BackgroundScheduler

from linkedin_agent.mcp_client_agent import run_agent, create_mcp_client
from linkedin_agent.utils.mysql_logger import init_db, log, clear_logs

app = Flask(__name__)
RSS_FILE = "rss.xml"


async def pre_run_checks():
    """
    Performs pre-run checks for essential services like the database and MCP server.
    Exits the application if a check fails.
    """
    print("--- Performing pre-run connectivity checks ---")
    
    # 1. Check SQL DB connection
    try:
        print("Checking database connection...")
        init_db()  # This will implicitly check the connection by initializing
        print("Database connection successful.")
        log('INFO', 'PreRunCheck', 'Database connection successful.')
    except Exception as e:
        print(f"FATAL: Database connection failed: {e}", file=sys.stderr)
        # We can't log to DB if it's down, so we just print and exit.
        sys.exit(1)

    # 2. Check MCP Server connection
    try:
        print("Checking MCP server connection...")
        client = create_mcp_client()
        await client.get_tools()  # This will fail if the server is unreachable
        print("MCP server connection successful.")
        log('INFO', 'PreRunCheck', 'MCP server connection successful.')
    except Exception as e:
        print(f"FATAL: MCP server connection failed: {e}", file=sys.stderr)
        log('CRITICAL', 'PreRunCheck', 'MCP server connection failed.', {'error': str(e)})
        sys.exit(1)
        
    print("--- All connectivity checks passed ---")


def update_rss_feed():
    """
    Runs the agent, generates a new RSS feed, and saves it to a file.
    """
    print("--- Updating RSS Feed ---")
    log('INFO', 'RSS_Feed', 'Starting RSS feed update.')
    try:
        # Run the agent to get the latest analysis
        # We need to run the async function in a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        analysis_content = loop.run_until_complete(run_agent())
        loop.close()
        log('INFO', 'RSS_Feed', 'Agent run completed.', {'content_length': len(analysis_content)})

        # Create a new feed
        fg = FeedGenerator()
        fg.id('urn:uuid:' + str(uuid.uuid4()))
        fg.title('LinkedIn Job Analysis RSS Feed')
        fg.link(href='http://localhost:5000/rss', rel='self')
        fg.description('An RSS feed of job analysis from the LinkedIn agent.')
        fg.logo('http://localhost:5000/fluff/logo.png')

        # Parse the JSON output from the agent and add an entry for each job
        try:
            jobs = json.loads(analysis_content)
            
            if not isinstance(jobs, list):
                raise TypeError("Expected a list of jobs from agent")

            for job in jobs:
                fe = fg.add_entry()
                fe.id('urn:uuid:' + str(uuid.uuid4()))
                # Use .get() for safer dictionary access
                job_title = job.get('job_title', 'Unknown Job Title')
                job_html = job.get('job_html', '<p>No content available.</p>')
                
                fe.title(f"{job_title}")
                fe.link(href='http://localhost:5000/rss')
                fe.description(job_html)
                fe.pubDate(datetime.now().replace(tzinfo=pytz.UTC))
            log('INFO', 'RSS_Feed', 'Successfully parsed agent output and generated feed entries.')

        except (json.JSONDecodeError, TypeError) as e:
            log('ERROR', 'RSS_Feed', 'Error processing job analysis.', {'error': str(e), 'raw_output': analysis_content})
            # If parsing fails or the structure is wrong, add a single error entry
            fe = fg.add_entry()
            fe.id('urn:uuid:' + str(uuid.uuid4()))
            fe.title(f'Error Processing Job Analysis: {type(e).__name__}')
            fe.link(href='http://localhost:5000/rss')
            fe.description(f"Could not process agent output. Error: {e}\n\nRaw output:\n{analysis_content}")
            fe.pubDate(datetime.now().replace(tzinfo=pytz.UTC))

        # Save the feed to a file
        fg.atom_file(RSS_FILE, pretty=True)
        print(f"--- RSS Feed updated and saved to {RSS_FILE} ---")
        log('INFO', 'RSS_Feed', f'RSS Feed updated and saved to {RSS_FILE}.')

    except Exception as e:
        print(f"Error updating RSS feed: {e}")
        log('ERROR', 'RSS_Feed', 'Error updating RSS feed.', {'error': str(e)})


@app.route('/fluff/<path:filename>')
def serve_fluff(filename):
    return send_from_directory('fluff', filename)


@app.route('/rss')
def rss_feed():
    """Serves the static RSS feed file."""
    if not os.path.exists(RSS_FILE):
        return "The RSS feed has not been generated yet. Please wait for the scheduled job to run.", 503
    return send_from_directory('.', RSS_FILE, mimetype='application/atom+xml')


if __name__ == '__main__':
    # --- Perform pre-run checks first ---
    # We need an event loop to run the async check function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(pre_run_checks())
    loop.close()
    
    # init_db() is now called inside pre_run_checks()

    # --- Scheduler Setup ---
    scheduler = BackgroundScheduler()
    # Schedule the RSS feed update to run every 72 hours
    scheduler.add_job(
        update_rss_feed,
        'interval',
        hours=72,
        jitter=36000
    )
    # Schedule the log cleanup to run once a week (e.g., every Sunday at midnight)
    scheduler.add_job(
        clear_logs,
        'cron',
        day_of_week='sun',
        hour=0
    )
    scheduler.start()
    clear_logs()
    update_rss_feed()  # Initial run to generate the feed immediately
    # --- Start Flask App ---
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False) # use_reloader=False is important for scheduler
