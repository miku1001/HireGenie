from langchain_core.output_parsers import StrOutputParser
from utils.llm import load_llm
from langchain_core.prompts import PromptTemplate

def match_skills(jd_data: dict, resume_data: dict) -> dict:
  llm = load_llm()

  job_skills = ', '.join(jd_data['required_skills'])
  resume_skills = ', '.join(resume_data['structured']['skills'])

  prompt = PromptTemplate(
    input_variables = ['job_skills', 'resume_skills'],
    template = """
You are an expert technical recruiter comparing a candidate's skills to a job description.

Job Required Skills: {jd_skills}
Candidate Skills: {resume_skills}

Categorize each JD skill into one of three categories:
1. MATCHED - candidate clearly has this skill
2. PARTIAL - candidate has a related/similar skill but not exact
3. MISSING - candidate does not have this skill at all

Respond in this exact format:
MATCHED: skill1, skill2, ...
PARTIAL: skill1 (candidate has: ...), skill2 (candidate has: ...), ...
MISSING: skill1, skill2, ...
MATCH_SCORE: (a number from 0-100 representing overall match percentage)
"""
  )
  chain = prompt | llm | StrOutputParser()
  print("Matching Skills...")
  result = chain.invoke({'jd_skills': job_skills, 'resume_skills': resume_skills})

  return parse_match_output(result)

def parse_match_output(raw:str) -> dict:
  lines = raw.strip().split("\n")
  output = {
    "matched": [],
    "partial": [],
    "missing": [],
    "match_score": 0
  }

  for line in lines:
    line = line.strip()

    if line.startswith("MATCHED:"):
      raw_skills = line.replace("MATCHED:", "").strip()
      if raw_skills:
        output["matched"] = [skills.strip() for skills in raw_skills.split(',')]
    
    elif line.startswith("PARTIAL:"):
      raw_skills = line.replace("PARTIAL:", "").strip()
      if raw_skills:
        output["partial"] = [skills.strip() for skills in raw_skills.split(',')]
    
    elif line.startswith("MISSING:"):
      raw_skills = line.replace("MISSING:", "").strip()
      if raw_skills:
        output["missing"] = [skills.strip() for skills in raw_skills.split(',')]
    
    elif line.startswith("MATCH_SCORE:"):
      try:
        score = line.replace("MATCH_SCORE:", "").strip()
        output["match_score"] = int(score)
      except ValueError:
        output["match_score"] = 0

  return output


  