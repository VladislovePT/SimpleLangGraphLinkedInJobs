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
    '"Cybersecurity" AND (OSINT OR "Threat Intelligence")',
    '"Automation Engineer" AND (AI OR Azure)',
]


job_match_prompt = PromptTemplate(
    input_variables=["profile", "jobs", "date"],
    template="""
Today is {date}.

You are creating a weekly job matching newsletter for the candidate in PROFILE.  
The newsletter should start with a short friendly introduction (2–3 sentences),  
mentioning that it's a personalized summary of job opportunities and fit analysis.

PROFILE:
{profile}

JOBS:
{jobs}

TASK:
For each job in JOBS, compare its requirements/responsibilities with PROFILE.  
Then produce a Markdown newsletter with:

1. **Intro paragraph** (like a weekly jobs digest).
2. **Markdown table** with the following columns (use emojis as headers):

- 🏢 Company Name
- 📝 Company Description (short semantic summary of what the company does)
- Job Title
- ✅/⚖️/❌ (Fit level: Strong, Medium, Weak)
- 💪 Strong Fit Characteristics (comma-separated list)
- ⚠️ Missing Characteristics (comma-separated list)
- 📝 Notes (short clarification if relevant)
- 🚨 Consultancy? (worded judgment + emoji: "Consultancy/Outsourcing 🚨", "Not Consultancy ✅", "Suspected Consultancy ❓")
- 💰 Salary (if provided, otherwise leave blank)
- 📍 Location
- 🌐 Work Type (Remote / Onsite / Hybrid – if Hybrid, indicate expected days per week onsite, e.g., "Hybrid – 2 days onsite")
- 🔗 LinkedIn (URL from PROFILE if available, otherwise leave blank)

FIT CRITERIA:
- ✅ Strong: Candidate meets ≥70% of key requirements.
- ⚖️ Medium: Candidate meets ~40–70% of key requirements.
- ❌ Weak: Candidate meets <40% of key requirements.

CONSULTANCY CHECK (semantic judgment):
- Use the job/company description to decide:
  - "Consultancy/Outsourcing 🚨" if the company provides consulting, outsourcing, body-leasing, or staff augmentation services.
  - "Not Consultancy ✅" if the company is product-based or end-user organization.
  - "Suspected Consultancy ❓" if unclear.

WORK TYPE CHECK:
- If the description mentions remote, hybrid, or onsite, include in 🌐 Work Type column.
- For hybrid, try to identify how many days per week onsite. If unclear, just write "Hybrid ❓".

RULES:
- Compare skills/technologies case-insensitively; treat plural/singular forms as equivalent.
- If a requirement is partially matched, add "(partial)".
- Always include the LinkedIn URL in each row if present in PROFILE.
- Output only Markdown: intro paragraph + table + summary section.
- At the end, add a **summary section** listing total jobs analyzed, and counts of Strong, Medium, Weak fits.

EXAMPLE SUMMARY SECTION:

**Summary:**  
Total jobs analyzed: 5  
✅ Strong fit: 2  
⚖️ Medium fit: 2  
❌ Weak fit: 1
"""
)