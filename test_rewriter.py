from agents.jd_analyzer import jd_analyze
from agents.resume_parser import parse_resume
from agents.skill_matcher import match_skills
from agents.rewriter import rewrite_resume
from agents.reviewer import review

sample_jd = """
We are looking for a Python Backend Developer with experience in
FastAPI, PostgreSQL, Docker, and REST APIs.
"""

jd_data = jd_analyze(sample_jd)
resume_data = parse_resume("ref.pdf")
match_data = match_skills(jd_data, resume_data)
rewritten = rewrite_resume(resume_data, jd_data, match_data)
review = review(rewritten, jd_data, match_data)

print('=== SKILL MATCH ===')
print(match_data["matched"])
print(match_data["partial"])
print(match_data["missing"])
print(match_data["match_score"])

print("=== SUMMARY ===")
print(rewritten["summary"])

print("\n=== EXPERIENCE ===")
for job in rewritten["experience"]:
    print(f"\n{job['title']} @ {job['company']}")
    for bullet in job["bullets"]:
        print(bullet)

print("\n=== PROJECTS ===")
for project in rewritten["projects"]:
    print(f"\n{project['name']} ({project['tech']})")
    for bullet in project["bullets"]:
        print(bullet)

print("=== SCORES ===")
print("ATS:", review["scores"]["ats"])
print("Clarity:", review["scores"]["clarity"])
print("Tone:", review["scores"]["tone"])
print("Keyword:", review["scores"]["keyword"])
print("Overall:", review["overall_score"])
print("Approved:", review["approved"])

print("\n=== SUGGESTIONS ===")
for suggestion in review["suggestions"]:
    print(suggestion)