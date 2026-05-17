from langchain_core.output_parsers import StrOutputParser
from utils.llm import load_llm
from langchain_core.prompts import PromptTemplate

#analyze job description
def jd_analyze(jd_text: str) -> dict:
  llm = load_llm()

  prompt = PromptTemplate(
    input_variables=["jd_text"],
    template ="""You are an expert job description analyzer.

Given the job description below, extract the following:
1. Required technical skills (as a comma-separated list)
2. Nice-to-have skills (as a comma-separated list)
3. Key responsibilities (as a bullet list, max 5)
4. Tone of the company (e.g. startup, corporate, casual, formal)

Job Description:
{jd_text}

Respond in this exact format:
REQUIRED_SKILLS: ...
NICE_TO_HAVE: ...
RESPONSIBILITIES:
- ...
- ...
TONE: ...
"""
  )

  chain = prompt | llm | StrOutputParser()
  result = chain.invoke({"jd_text": jd_text})
  return parse_jd_output(result)



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