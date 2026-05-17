from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from utils.llm import load_llm


def review(rewritten_data: dict, jd_data: dict, match_data: dict) -> dict:
    raw_result = review_all(rewritten_data, jd_data, match_data)
    scores = raw_result["scores"]

    return {
        "scores": scores,
        "suggestions": raw_result["suggestions"],
        "overall_score": calculate_overall_score(scores),
        "approved": is_approved(scores)
    }


def review_all(rewritten_data: dict, jd_data: dict, match_data: dict) -> dict:
    llm = load_llm()

    all_bullets = []
    for job in rewritten_data["experience"]:
        for bullet in job["bullets"]:
            all_bullets.append(f"- {bullet}")

    prompt = PromptTemplate(
        input_variables=[
            "summary", "bullets",
            "jd_skills", "jd_tone",
            "missing_skills", "jd_responsibilities"
        ],
        template="""
You are an ATS expert and resume coach. Evaluate and give feedback.

SUMMARY: {summary}
BULLETS:
{bullets}
JD_SKILLS: {jd_skills}
JD_TONE: {jd_tone}
MISSING: {missing_skills}
RESPONSIBILITIES:
{jd_responsibilities}

Respond in this EXACT format:

ATS_SCORE: (0-100)
CLARITY_SCORE: (0-100)
TONE_SCORE: (0-100)
KEYWORD_SCORE: (0-100)
SUGGESTIONS:
- (specific suggestion)
- (specific suggestion)
- (specific suggestion)
"""
    )

    chain = prompt | llm | StrOutputParser()

    print(">>> Reviewing resume (1 LLM call)...")

    raw = chain.invoke({
        "summary": rewritten_data["summary"],
        "bullets": "\n".join(all_bullets),
        "jd_skills": ", ".join(jd_data["required_skills"]),
        "jd_tone": jd_data["tone"],
        "missing_skills": ", ".join(match_data["missing"]),
        "jd_responsibilities": "\n".join(jd_data["responsibilities"])
    })

    return _parse_review_output(raw)


def _parse_review_output(raw: str) -> dict:
    lines = raw.strip().split("\n")

    result = {
        "scores": {
            "ats": 0,
            "clarity": 0,
            "tone": 0,
            "keyword": 0
        },
        "suggestions": []
    }

    current_section = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        try:
            if line.startswith("ATS_SCORE:"):
                result["scores"]["ats"] = int(line.replace("ATS_SCORE:", "").strip())
            elif line.startswith("CLARITY_SCORE:"):
                result["scores"]["clarity"] = int(line.replace("CLARITY_SCORE:", "").strip())
            elif line.startswith("TONE_SCORE:"):
                result["scores"]["tone"] = int(line.replace("TONE_SCORE:", "").strip())
            elif line.startswith("KEYWORD_SCORE:"):
                result["scores"]["keyword"] = int(line.replace("KEYWORD_SCORE:", "").strip())
            elif line == "SUGGESTIONS:":
                current_section = "suggestions"
            elif line.startswith("-") and current_section == "suggestions":
                result["suggestions"].append(line[1:].strip())
        except ValueError:
            pass

    return result


def calculate_overall_score(scores: dict) -> int:
    weights = {
        "ats": 0.4,
        "clarity": 0.2,
        "tone": 0.2,
        "keyword": 0.2
    }

    return int(
        scores["ats"] * weights["ats"] +
        scores["clarity"] * weights["clarity"] +
        scores["tone"] * weights["tone"] +
        scores["keyword"] * weights["keyword"]
    )


def is_approved(scores: dict) -> bool:
    overall = calculate_overall_score(scores)
    return overall >= 70