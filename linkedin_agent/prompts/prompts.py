from langchain.prompts import PromptTemplate

# The search queries remain the same
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

# STEP 1: A lean prompt that instructs the model to return only a JSON object for analysis.
job_analysis_prompt = PromptTemplate(
    input_variables=["profile", "job", "date"],
    template='''
Today is {date}.
You are a career analyst. Your task is to analyze the candidate PROFILE against the JOB description and output a single, valid JSON object with the analysis.

PROFILE:
{profile}

JOB:
{job}

--- MANDATORY RULES ---
1.  Output ONLY a single, valid JSON object. No other text, comments, or markdown.
2.  The JSON must strictly conform to the structure specified below.
3.  **Analysis Process:** First, mentally create a flat list of all skills from the PROFILE, noting their proficiency. Then, for each requirement in the JOB, you MUST search your complete list to find a match. A 'Proficient' or 'Intermediate' skill is a valid match and must be included in `matchingSkills` if relevant.
4.  Determine a numerical `fitScore` between 0 and 100. This score should be weighted: a job requirement matching an 'Expert' skill is a stronger match than one matching an 'Intermediate' skill.
5.  For `matchingSkills`, you must include the `proficiency` level from the profile.
6.  For `workTypeEmoji`, use 🏢 for Onsite, 🏠 for Remote, or 🔄 for Hybrid.
7.  **Onsite Work Caution:** If the `workType` is 'Hybrid' or 'Onsite', you MUST add a cautionary note to the `notes` field. Example: "Caution: This is a hybrid role and may require office presence."
8.  Analyze the original `job` data to extract placeholders like company name, location, etc. If a value cannot be found, use "Not specified".

--- JSON OUTPUT STRUCTURE ---
{{
  "companyName": "string",
  "jobTitle": "string",
  "location": "string",
  "workType": "string",
  "workTypeEmoji": "string",
  "salary": "string",
  "fitScore": "number (0-100)",
  "fitReasoning": "string",
  "matchingSkills": [
    {{ "skill": "string", "proficiency": "string (Expert, Proficient, or Intermediate)", "reason": "string" }}
  ],
  "missingSkills": [
    {{ "skill": "string", "reason": "string" }}
  ],
  "notes": "string",
  "companyDescription": "string",
  "linkedinUrl": "string"
}}
'''
)

