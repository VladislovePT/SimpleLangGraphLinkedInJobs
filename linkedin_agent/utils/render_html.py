import json

# STEP 2: The HTML structure is now a separate template string.
# It uses standard Python .format() placeholders.
JOB_CARD_TEMPLATE = '''
<div style="border: 1px solid #ddd; border-radius: 8px; margin: 16px 0; padding: 16px; font-family: sans-serif; line-height: 1.6;">
    
    <!-- HEADER: Company and Job Title -->
    <h2 style="margin-top: 0; margin-bottom: 8px; font-size: 1.4em;">
        🏢 {companyName} — {jobTitle}
    </h2>
    
    <!-- FIT ASSESSMENT: Colored box for emphasis -->
    <div style="border-radius: 4px; padding: 12px; margin-bottom: 16px; background-color: {fit_bg_color}; color: {fit_text_color};">
        <strong style="font-size: 1.1em;">{fit_emoji} Fit: {fit_word} ({fit_score}%)</strong>
        <p style="margin: 8px 0 0 0;"><strong>Justification:</strong> {fitReasoning}</p>
    </div>

    <!-- METADATA: Location, Work Type, Salary -->
    <div style="font-size: 0.9em; color: #555; margin-bottom: 16px;">
        <span>📍 {location}</span> |
        <span>{workTypeEmoji} {workType}</span> |
        <span>💰 {salary}</span>
    </div>



    <!-- DETAILS: Skills analysis -->
    <div>
        <p><strong>✅ Matching Skills:</strong></p>
        <ul style="margin-top: 4px; padding-left: 20px; margin-bottom: 12px;">
            {matching_skills_list}
        </ul>

        <p><strong>❌ Missing Skills:</strong></p>
        <ul style="margin-top: 4px; padding-left: 20px; margin-bottom: 12px;">
            {missing_skills_list}
        </ul>
        <p><strong>📝 Notes:</strong> {notes}</p>
    </div>

    <!-- FOOTER: Consultancy, Company Info, Profile Link -->
    <div style="border-top: 1px solid #eee; padding-top: 12px; margin-top: 16px; font-size: 0.9em; color: #555;">
        <p style="margin: 0;"><strong>About {companyName}:</strong> {companyDescription}</p>
        <p style="margin: 8px 0 0 0;"><strong>Profile:</strong> <a href="{linkedinUrl}">LinkedIn</a></p>
    </div>
</div>
'''

# STEP 3: A helper function to perform the rendering logic that was offloaded from the LLM.
def render_job_card(analysis_json: str) -> str:
    """
    Renders the final HTML card by taking the JSON output from the LLM,
    handling deterministic logic, and formatting it into the HTML template.

    Args:
        analysis_json: A string containing the JSON data from the LLM.

    Returns:
        A string containing the final, rendered HTML card.
    """
    try:
        data = json.loads(analysis_json)
    except json.JSONDecodeError:
        return f"<div style='color: red;'>Error: Invalid JSON received from model.</div><pre>{analysis_json}</pre>"

    # --- Handle deterministic logic ---
    fit_score = data.get("fitScore", 0)
    fit_details = {}
    if fit_score >= 90:
        fit_details = {"emoji": "🌟", "word": "Excellent", "bg_color": "#e8eaf6", "text_color": "#3f51b5"}
    elif 75 <= fit_score < 90:
        fit_details = {"emoji": "✅", "word": "Strong", "bg_color": "#e8f5e9", "text_color": "#2e7d32"}
    elif 60 <= fit_score < 75:
        fit_details = {"emoji": "👍", "word": "Good", "bg_color": "#fff3e0", "text_color": "#f57c00"}
    elif 40 <= fit_score < 60:
        fit_details = {"emoji": "⚠️", "word": "Weak", "bg_color": "#ffecb3", "text_color": "#ff6f00"}
    else:
        fit_details = {"emoji": "❌", "word": "Poor", "bg_color": "#ffebee", "text_color": "#c62828"}

    # --- Build HTML lists ---
    matching_skills_html = ""
    for item in data.get("matchingSkills", []):
        matching_skills_html += f"<li><strong>{item.get('skill', '')}:</strong> ({item.get('proficiency', '')}) {item.get('reason', '')}</li>"
    if not matching_skills_html:
        matching_skills_html = "<li>None specified.</li>"

    missing_skills_html = ""
    for item in data.get("missingSkills", []):
        missing_skills_html += f"<li><strong>{item.get('skill', '')}:</strong> {item.get('reason', '')}</li>"
    if not missing_skills_html:
        missing_skills_html = "<li>None specified.</li>"

    # --- Format the final template ---
    return JOB_CARD_TEMPLATE.format(
        companyName=data.get("companyName", "Not specified"),
        jobTitle=data.get("jobTitle", "Not specified"),
        location=data.get("location", "Not specified"),
        workType=data.get("workType", "Not specified"),
        workTypeEmoji=data.get("workTypeEmoji", "❓"),
        salary=data.get("salary", "Not specified"),
        fit_bg_color=fit_details.get("bg_color"),
        fit_text_color=fit_details.get("text_color"),
        fit_emoji=fit_details.get("emoji"),
        fit_word=fit_details.get("word"),
        fit_score=fit_score,
        fitReasoning=data.get("fitReasoning", ""),
        matching_skills_list=matching_skills_html,
        missing_skills_list=missing_skills_html,
        notes=data.get("notes", ""),
        companyDescription=data.get("companyDescription", ""),
        linkedinUrl=data.get("linkedinUrl", "#")
    )
