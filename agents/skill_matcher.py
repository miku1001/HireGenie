from langchain_core.output_parsers import StrOutputParser
from utils.llm import load_llm
from langchain_core.prompts import PromptTemplate

from utils.cache import cache, make_key

def match_skills(jd_data: dict, resume_data: dict) -> dict:
  key = f"match_{make_key(str(jd_data['required_skills']), str(resume_data['structured']['skills']))}"

  if key in cache:
        print(">>> Skills match cache hit!")
        return cache[key]

  llm = load_llm()

  job_skills = ', '.join(jd_data['required_skills'])
  resume_skills = ', '.join(resume_data['structured']['skills'])

  prompt = PromptTemplate(
    input_variables = ['jd_skills', 'resume_skills'],
    template = """
Compare these skills and categorize each JD skill:

JD_SKILLS: {jd_skills}
CANDIDATE_SKILLS: {resume_skills}

MATCHED: (exact or clear match)
PARTIAL: (related but not exact)
MISSING: (not present)

Respond EXACTLY:
MATCHED: skill1, skill2
PARTIAL: skill1 (candidate has: ...), ...
MISSING: skill1, skill2
MATCH_SCORE: (0-100)
"""
  )
  chain = prompt | llm | StrOutputParser()
  result = chain.invoke({'jd_skills': job_skills, 'resume_skills': resume_skills})
  parsed = parse_match_output(result)
  cache.set(key, parsed, expire=43200)
  return parsed

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