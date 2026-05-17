from langchain_core.output_parsers import StrOutputParser
from utils.llm import load_llm
from langchain_core.prompts import PromptTemplate

from utils.cache import cache, get_text_hash


#analyze job description
def jd_analyze(jd_text: str) -> dict:
  
  key = f"jd_{get_text_hash(jd_text)}"

  if key in cache:
        print(">>> JD cache hit!")
        return cache[key]
  
  llm = load_llm()

  prompt = PromptTemplate(
    input_variables=["jd_text"],
    template ="""You are an expert job description analyzer.

Given the job description below, extract the following:
Job Description:
{jd_text}

Respond in this exact format:
REQUIRED_SKILLS: (, seperated)
NICE_TO_HAVE: (, seperated)
RESPONSIBILITIES:
- ...
- ...
TONE: (e.g. startup, corporate, casual, formal)
"""
  )

  chain = prompt | llm | StrOutputParser()
  result = chain.invoke({"jd_text": jd_text})
  parsed = parse_jd_output(result)
  cache.set(key, parsed, expire=43200)
  return parsed



#parse jd result
def parse_jd_output(raw: str) -> dict:
    lines = raw.strip().split("\n")
    output = {
        "required_skills": [],
        "nice_to_have": [],
        "responsibilities": [],
        "tone": ""
    }

    for line in lines:
        if line.startswith("REQUIRED_SKILLS:"):
            output["required_skills"] = [s.strip() for s in line.replace("REQUIRED_SKILLS:", "").split(",")]
        elif line.startswith("NICE_TO_HAVE:"):
            output["nice_to_have"] = [s.strip() for s in line.replace("NICE_TO_HAVE:", "").split(",")]
        elif line.startswith("TONE:"):
            output["tone"] = line.replace("TONE:", "").strip()
        elif line.startswith("- "):
            output["responsibilities"].append(line.strip())

    return output