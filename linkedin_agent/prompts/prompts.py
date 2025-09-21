from langchain.prompts import PromptTemplate

jobs_query = [
    "Azure AI Engineer",
    "Senior AI Engineer",
    "IoT Solutions Developer",
    "Cloud AI Developer",
    "Python AI Engineer",
    "LangChain Developer",
    "Generative AI Engineer",
    "Semantic Kernel Engineer",
    "Azure IoT Developer",
    "Azure Cognitive Services",
    '"AI Engineer" AND (Python OR C#) AND Azure',
    '"Software Engineer" AND (LangChain OR LangGraph)',
    '"IoT Developer" AND (Azure OR Python)',
    '"Automation Engineer" AND (AI OR Azure)',
]

job_match_prompt = PromptTemplate(
    input_variables=["profile", "job", "date"],
    template="""
Today is {date}.

You are a career assistant creating a visually appealing HTML summary for a job opportunity.
You will analyze the candidate PROFILE against the provided JOB data.

PROFILE:
{profile}

JOB:
{job}

TASK:
Generate a single, self-contained HTML block using inline CSS. The output must be pure HTML, with no extra text, comments, or markdown.
The HTML should be a 'card' for the job analysis. Use the provided JSON data to fill in the placeholders (e.g., <COMPANY_NAME>).

**Visually emphasize keywords** from the PROFILE's skills list when they appear in your analysis by wrapping them in `<strong>`.

Here is the required HTML structure:

<div style="border: 1px solid #ddd; border-radius: 8px; margin: 16px 0; padding: 16px; font-family: sans-serif; line-height: 1.6;">
    
    <!-- HEADER: Company and Job Title -->
    <h2 style="margin-top: 0; margin-bottom: 8px; font-size: 1.4em;">
        🏢 <COMPANY_NAME> — <JOB_TITLE>
    </h2>
    
    <!-- METADATA: Location, Work Type, Salary -->
    <div style="font-size: 0.9em; color: #555; margin-bottom: 16px;">
        <span>📍 <LOCATION></span> |
        <span><WORK_TYPE_EMOJI> <WORK_TYPE></span> |
        <span>💰 <SALARY></span>
    </div>

    <!-- FIT ASSESSMENT: Colored box for emphasis -->
    <div style="border-radius: 4px; padding: 12px; margin-bottom: 16px; background-color: <FIT_BG_COLOR>; color: <FIT_TEXT_COLOR>;">
        <strong style="font-size: 1.1em;"><FIT_EMOJI> Fit: <FIT_WORD></strong>
        <p style="margin: 8px 0 0 0;"><strong>Justification:</strong> <FIT_REASONING></p>
    </div>

    <!-- DETAILS: Skills analysis -->
    <div>
        <p><strong>✅ Matching Skills:</strong></p>
        <ul style="margin-top: 4px; padding-left: 20px; margin-bottom: 12px;">
            <!-- Repeat for each matching skill. Example: <li><strong>Python:</strong> Profile shows 5 years of experience, and the job requires it for data analysis.</li> -->
            <MATCHING_SKILLS_LIST>
        </ul>

        <p><strong>❌ Missing Skills:</strong></p>
        <ul style="margin-top: 4px; padding-left: 20px; margin-bottom: 12px;">
            <!-- Repeat for each missing skill. Example: <li><strong>Go:</strong> The job lists Go as a required language for microservices, which is not on the profile.</li> -->
            <MISSING_SKILLS_LIST>
        </ul>
        <p><strong>📝 Notes:</strong> <NOTES></p>
    </div>

    <!-- FOOTER: Consultancy, Company Info, Profile Link -->
    <div style="border-top: 1px solid #eee; padding-top: 12px; margin-top: 16px; font-size: 0.9em; color: #555;">
        <p style="margin: 0;"><strong>About <COMPANY_NAME>:</strong> <COMPANY_DESCRIPTION></p>
        <p style="margin: 8px 0 0 0;"><strong>Profile:</strong> <a href="<LINKEDIN_URL>">LinkedIn</a></p>
    </div>
</div>

--- MANDATORY RULES ---
1.  **Output ONLY the HTML card.** No extra text, comments, or markdown.
2.  **Fill all placeholders.** If a value is missing from the JSON, use "Not specified".
3.  **Fit Assessment & Colors:**
    - **Strong Fit (>=80% match):** Use ✅, "Strong", `background-color: #e8f5e9;`, `color: #2e7d32;`.
    - **Medium Fit (~50-80% match):** Use ⚖️, "Medium", `background-color: #fff3e0;`, `color: #f57c00;`.
    - **Weak Fit (<50% match):** Use ❌, "Weak", `background-color: #ffebee;`, `color: #c62828;`.
4.  **Skills Analysis:** For `<MATCHING_SKILLS_LIST>` and `<MISSING_SKILLS_LIST>`, generate a series of `<li>` items.
    - Each `<li>` must contain the skill name in `<strong>` followed by a brief justification for why it's a match or a miss.
    - **Matching Example:** `<li><strong>Python:</strong> Profile shows 5 years of experience, and the job requires it for data analysis.</li>`
    - **Missing Example:** `<li><strong>Go:</strong> The job lists Go for microservices, which is not on the profile.</li>`
5.  **Work Type:** Use an appropriate emoji: 🏢 (Onsite), 🏠 (Remote), 🔄 (Hybrid). For Hybrid, specify days if known (e.g., "Hybrid – 3 days onsite").
6.  **Keyword Emphasis:** In the <NOTES>, <FIT_REASONING>, and <COMPANY_DESCRIPTION> sections, wrap any skills that match the candidate's PROFILE in `<strong>` tags for emphasis.
"""
)