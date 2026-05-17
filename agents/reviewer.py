from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from utils.llm import load_llm

def review(rewritten_data: dict, jd_data: dict, match_data: dict) -> dict:
  scores = score_resume(rewritten_data, jd_data)

  return {
        "scores": scores,
        "suggestions": suggest(rewritten_data, jd_data, match_data),
        "overall_score": calculate_overall_score(scores),
        "approved": is_approved(scores)
    }

def score_resume(rewritten_data: dict, jd_data: dict) -> dict:
  llm = load_llm()

  prompt = PromptTemplate(
        input_variables=["summary", "experience_bullets", "jd_skills", "jd_tone"],
        template="""
You are an ATS (Applicant Tracking System) expert and senior recruiter.

Evaluate this resume content against the job requirements.

Resume Summary:
{summary}

Experience Bullets:
{experience_bullets}

Job Required Skills: {jd_skills}
Company Tone: {jd_tone}

Score each category from 0-100:
1. ATS_SCORE: How well does it match ATS keyword requirements?
2. CLARITY_SCORE: Are the bullet points clear and impactful?
3. TONE_SCORE: Does the writing match the company tone?
4. KEYWORD_SCORE: Are JD keywords naturally incorporated?

Respond in this exact format:
ATS_SCORE: (number)
CLARITY_SCORE: (number)
TONE_SCORE: (number)
KEYWORD_SCORE: (number)
"""
    )
  
  all_bullets = []
  for job in rewritten_data["experience"]:
      for bullet in job["bullets"]:
          all_bullets.append(bullet)

  chain = prompt | llm | StrOutputParser()
  result = chain.invoke({
        "summary": rewritten_data["summary"],
        "experience_bullets": "\n".join(all_bullets),
        "jd_skills": ", ".join(jd_data["required_skills"]),
        "jd_tone": jd_data["tone"]
  })

  return parse_scores(result)

def parse_scores(raw: str) -> dict: 
   lines = raw.strip().split('\n')
   scores = {
      "ats": 0,
      "clarity": 0,
      "tone": 0,
      "keyword": 0
   }

   for line in lines:
      line = line.strip()
      try:
          if line.startswith("ATS_SCORE:"):
              scores["ats"] = int(line.replace("ATS_SCORE:", "").strip())
          elif line.startswith("CLARITY_SCORE:"):
              scores["clarity"] = int(line.replace("CLARITY_SCORE:", "").strip())
          elif line.startswith("TONE_SCORE:"):
              scores["tone"] = int(line.replace("TONE_SCORE:", "").strip())
          elif line.startswith("KEYWORD_SCORE:"):
              scores["keyword"] = int(line.replace("KEYWORD_SCORE:", "").strip())
      except ValueError:
          pass

   return scores

def suggest(rewritten_data: dict, jd_data: dict, match_data: dict) -> list:
    llm = load_llm()

    prompt = PromptTemplate(
        input_variables=["summary", "missing_skills", "jd_responsibilities"],
        template="""
You are a professional resume coach.

Review this resume summary and identify specific improvements.

Summary: {summary}

Skills still missing from resume: {missing_skills}
Job key responsibilities: {jd_responsibilities}

Give 3-5 specific, actionable suggestions to improve the resume.

Rules:
- Be specific, not generic (not "improve your bullets" but "add metrics to your FastAPI bullet")
- Focus on what's missing or weak
- Each suggestion must start with "-"

Return only the suggestions, nothing else.
"""
    )

    chain = prompt | llm | StrOutputParser()

    result = chain.invoke({
        "summary": rewritten_data["summary"],
        "missing_skills": ", ".join(match_data["missing"]),
        "jd_responsibilities": "\n".join(jd_data["responsibilities"])
    })

    return [s.strip() for s in result.strip().split("\n") if s.strip().startswith("-")]
   
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
