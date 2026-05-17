from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from utils.llm import load_llm


def rewrite_resume(resume_data: dict, jd_data: dict, match_data: dict) -> dict:
    return {
        "summary": rewrite_summary(resume_data, jd_data),
        "experience": rewrite_experience(resume_data, jd_data, match_data),
        "projects": rewrite_projects(resume_data, jd_data),
    }


def rewrite_summary(resume_data: dict, jd_data: dict) -> str:
    llm = load_llm()

    prompt = PromptTemplate(
        input_variables=["name", "skills", "responsibilities", "tone"],
        template="""
You are an expert resume writer.

Write a 3-sentence professional summary for a resume.

Candidate info:
- Name: {name}
- Skills: {skills}

Target job context:
- Key responsibilities: {responsibilities}
- Company tone: {tone}

Rules:
- Do NOT fabricate experience or skills the candidate does not have
- Use keywords from the job responsibilities naturally
- Match the tone of the company
- Be concise and impactful
- Do not start with "I"

Return only the summary paragraph, nothing else.
"""
    )

    chain = prompt | llm | StrOutputParser()
    return chain.invoke({
        "name": resume_data["structured"]["name"],
        "skills": ", ".join(resume_data["structured"]["skills"]),
        "responsibilities": "\n".join(jd_data["responsibilities"]),
        "tone": jd_data["tone"]
    })


def rewrite_experience(resume_data: dict, jd_data: dict, match_data: dict) -> list:
    llm = load_llm()
    rewritten_experience = []

    prompt = PromptTemplate(
        input_variables=["job_title", "company", "duration", "bullets", "jd_skills", "matched_skills"],
        template="""
You are an expert resume writer specializing in ATS optimization.

Rewrite the bullet points for this work experience to better align with the target job.

Current experience:
- Job Title: {job_title}
- Company: {company}
- Duration: {duration}
- Current bullets:
{bullets}

Target job context:
- Required skills: {jd_skills}
- Skills this candidate already matched: {matched_skills}

Rules:
- Keep the same number of bullet points
- Do NOT invent responsibilities or tools not mentioned in the original
- Naturally incorporate matched skills where relevant
- Use strong action verbs (Built, Engineered, Designed, Implemented, etc.)
- Add metrics/impact where implied (e.g. "improved performance" → "improved performance by ~X%")
- Each bullet must start with "-"

Return only the rewritten bullet points, nothing else.
"""
    )

    chain = prompt | llm | StrOutputParser()
    print("Rewriting Experience...")
    for job in resume_data["structured"]["experience"]:
        bullets_text = "\n".join([f"- {b}" for b in job["bullets"]])

        result = chain.invoke({
            "job_title": job["title"],
            "company": job["company"],
            "duration": job["duration"],
            "bullets": bullets_text,
            "jd_skills": ", ".join(jd_data["required_skills"]),
            "matched_skills": ", ".join(match_data["matched"])
        })

        rewritten_experience.append({
            "title": job["title"],
            "company": job["company"],
            "duration": job["duration"],
            "bullets": [b.strip() for b in result.strip().split("\n") if b.strip()]
        })

    return rewritten_experience


def rewrite_projects(resume_data: dict, jd_data: dict) -> list:
    llm = load_llm()
    rewritten_projects = []

    prompt = PromptTemplate(
        input_variables=["project_name", "tech", "bullets", "jd_skills"],
        template="""
You are an expert resume writer.

Rewrite the bullet points for this project to better highlight relevance to the target job.

Project:
- Name: {project_name}
- Tech stack: {tech}
- Current bullets:
{bullets}

Target job required skills: {jd_skills}

Rules:
- Do NOT invent features or technologies not in the original
- Highlight technical decisions and impact
- Use strong action verbs
- Each bullet must start with "-"

Return only the rewritten bullet points, nothing else.
"""
    )

    chain = prompt | llm | StrOutputParser()
    print("Rewriting Projects...")
    for project in resume_data["structured"]["projects"]:
        bullets_text = "\n".join([f"- {b}" for b in project["bullets"]])

        result = chain.invoke({
            "project_name": project["name"],
            "tech": project["tech"],
            "bullets": bullets_text,
            "jd_skills": ", ".join(jd_data["required_skills"])
        })

        rewritten_projects.append({
            "name": project["name"],
            "tech": project["tech"],
            "bullets": [b.strip() for b in result.strip().split("\n") if b.strip()]
        })

    return rewritten_projects