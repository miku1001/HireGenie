from langchain_core.output_parsers import StrOutputParser
from utils.llm import load_llm
from langchain_core.prompts import PromptTemplate
from utils.file_upload import pdf_extract_text

from utils.cache import cache, get_file_hash


#parse resume
def parse_resume(pdf_file) -> dict:
    if isinstance(pdf_file, str):
        with open(pdf_file, "rb") as handle:
            file_hash = get_file_hash(handle)
    else:
        file_hash = get_file_hash(pdf_file)

    key = f"resume_{file_hash}"

    if key in cache:
     print(">>> Resume cache hit!")
     return cache[key]
    raw_text = pdf_extract_text(pdf_file)
    llm = load_llm()

    prompt = PromptTemplate(
    input_variables=["resume_text"],
    template ="""You are an expert resume parser.

Given the resume below, extract and structure the following sections:
Job Description:
{resume_text}

Respond in this exact format:
NAME: ...
SKILLS: ...
EXPERIENCE:
- TITLE: ... | COMPANY: ... | DURATION: ...
  - bullet point
PROJECTS:
- NAME: ... | TECH: ...(STRICTLY SEPERATE TECH using ,)
  - bullet point
EDUCATION: COURSE: ... | SCHOOL: ... | DURATION: ...
"""
  )

    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({"resume_text": raw_text})

    parsed = {"structured": parse_resume_output(result)}
    cache.set(key, parsed, expire=86400)  # 24 hours
    return parsed

#parse jd result
def parse_resume_output(raw: str) -> dict:
    lines = raw.strip().split("\n")
    output = {
        "name": "",
        "skills": [],
        "experience": [],
        "projects": [],
        "education": ""
    }

    current_section = None
    experience_current_item = None
    project_current_item = None

    for line in lines:
        line = line.strip()

        if line.startswith("NAME:"):
            output['name'] = line.replace("NAME:", "").strip()

        elif line.startswith("SKILLS:"):
            output['skills'] = [s.strip() for s in line.replace('SKILLS:', "").split(',')]

        elif line.startswith("EDUCATION:"):
            output["education"] = line.replace("EDUCATION:", "").strip()
        
        elif line.startswith("EXPERIENCE:"):
            current_section = "experience"

        elif line.startswith('PROJECTS:'):
            current_section = 'projects'
        
        elif line.startswith('- TITLE:') and current_section == "experience":
            parts = line.replace('- TITLE:', "").split("|")
            experience_current_item = {
                "title": parts[0].strip() if len(parts) > 0 else "",
                "company": parts[1].replace('COMPANY:', "").strip() if len(parts) > 1 else "",
                "duration": parts[2].replace('DURATION:', "").strip() if len(parts) > 1 else "",
                "bullets": []
            }

            output['experience'].append(experience_current_item)

        elif line.startswith('- NAME:') and current_section == 'projects':
            parts = line.replace('- TITLE:', "").split("|")
            project_current_item = {
                "name": parts[0].strip() if len(parts) > 0 else "",
                "tech": [item.strip() for item in parts[1].replace('TECH:', "").strip().split(',')] if len(parts) > 1 else "",
                "bullets": []
            }

            output['projects'].append(project_current_item)
        
        elif line.startswith('- ') and current_section == 'experience' and experience_current_item is not None:
            experience_current_item['bullets'].append(line.replace("- ", "" ).strip())
        
        elif line.startswith('- ')  and current_section == 'projects' and project_current_item is not None:
            project_current_item['bullets'].append(line.replace("- ", "" ).strip())

    return output