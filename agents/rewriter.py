from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from utils.llm import load_llm


def rewrite_resume(resume_data: dict, jd_data: dict, match_data: dict) -> dict:
    result = rewrite_all(resume_data, jd_data, match_data)
    return {
        "summary": result["summary"],
        "experience": result["experience"],
        "projects": result["projects"],
    }


def rewrite_all(resume_data: dict, jd_data: dict, match_data: dict) -> dict:
    llm = load_llm()

    experience_text = _format_experience(resume_data["structured"]["experience"])
    projects_text = _format_projects(resume_data["structured"]["projects"])

    prompt = PromptTemplate(
        input_variables=[
            "name", "skills", "jd_skills",
            "matched_skills", "jd_tone", "jd_responsibilities",
            "experience", "projects"
        ],
        template="""
You are an ATS-focused resume writer. Rewrite the resume below to align with the target job.

CANDIDATE: {name}
SKILLS: {skills}

JD_SKILLS: {jd_skills}
JD_MATCHED: {matched_skills}
JD_TONE: {jd_tone}
JD_RESPONSIBILITIES:
{jd_responsibilities}

Rules:
- Do NOT invent skills or experience not in the original
- Use strong action verbs
- Add metrics where implied
- Match company tone
- Each bullet starts with "-"

---

Rewrite the SUMMARY (3 sentences, do not start with "I"):
CURRENT SKILLS: {skills}

Rewrite each EXPERIENCE bullet (keep same count):
{experience}

Rewrite each PROJECT bullet (keep same count):
{projects}

---

Respond in this EXACT format:

SUMMARY:
(rewritten summary here)

EXPERIENCE:
[1]
- bullet
[2]
- bullet
- bullet

PROJECTS:
[1]
- bullet
[2]
- bullet
"""
    )

    chain = prompt | llm | StrOutputParser()

    print(">>> Rewriting resume (1 LLM call)...")

    raw = chain.invoke({
        "name": resume_data["structured"]["name"],
        "skills": ", ".join(resume_data["structured"]["skills"]),
        "jd_skills": ", ".join(jd_data["required_skills"]),
        "matched_skills": ", ".join(match_data["matched"]),
        "jd_tone": jd_data["tone"],
        "jd_responsibilities": "\n".join(jd_data["responsibilities"]),
        "experience": experience_text,
        "projects": projects_text,
    })

    return _parse_rewrite_output(
        raw=raw,
        original_experience=resume_data["structured"]["experience"],
        original_projects=resume_data["structured"]["projects"]
    )


def _format_experience(experience: list) -> str:
    lines = []
    for i, job in enumerate(experience, 1):
        lines.append(f"[{i}] {job['title']} @ {job['company']} | {job['duration']}")
        for bullet in job["bullets"]:
            lines.append(f"- {bullet}")
        lines.append("")
    return "\n".join(lines)


def _format_projects(projects: list) -> str:
    lines = []
    for i, project in enumerate(projects, 1):
        lines.append(f"[{i}] {project['name']} | {project['tech']}")
        for bullet in project["bullets"]:
            lines.append(f"- {bullet}")
        lines.append("")
    return "\n".join(lines)


def _parse_rewrite_output(raw: str, original_experience: list, original_projects: list) -> dict:
    result = {
        "summary": "",
        "experience": [],
        "projects": []
    }

    current_section = None
    current_index = None
    current_bullets = []

    lines = raw.strip().split("\n")

    for line in lines:
        line = line.strip()

        if line == "SUMMARY:":
            current_section = "summary"
            continue

        elif line == "EXPERIENCE:":
            current_section = "experience"
            continue

        elif line == "PROJECTS:":
            if current_section == "experience" and current_index is not None:
                _save_experience(result, original_experience, current_index, current_bullets)
            current_section = "projects"
            current_index = None
            current_bullets = []
            continue

        elif line.startswith("[") and line.endswith("]"):
            if current_index is not None:
                if current_section == "experience":
                    _save_experience(result, original_experience, current_index, current_bullets)
                elif current_section == "projects":
                    _save_project(result, original_projects, current_index, current_bullets)

            current_index = int(line[1:-1]) - 1
            current_bullets = []
            continue

        if current_section == "summary" and line:
            result["summary"] += line + " "

        elif line.startswith("-") and current_index is not None:
            current_bullets.append(line[1:].strip())

    # save last item
    if current_index is not None:
        if current_section == "experience":
            _save_experience(result, original_experience, current_index, current_bullets)
        elif current_section == "projects":
            _save_project(result, original_projects, current_index, current_bullets)

    result["summary"] = result["summary"].strip()
    return result


def _save_experience(result: dict, original: list, index: int, bullets: list):
    if index < len(original):
        result["experience"].append({
            "title": original[index]["title"],
            "company": original[index]["company"],
            "duration": original[index]["duration"],
            "bullets": bullets
        })


def _save_project(result: dict, original: list, index: int, bullets: list):
    if index < len(original):
        result["projects"].append({
            "name": original[index]["name"],
            "tech": original[index]["tech"],
            "bullets": bullets
        })