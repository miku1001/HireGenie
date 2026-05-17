from orchestrator import run_pipeline

result = run_pipeline(
    resume_file="ref.pdf",
    jd_text="""
    We are looking for a Python Backend Developer with experience in
    FastAPI, PostgreSQL, Docker, and REST APIs.
    """
)

print("=== MATCH SCORE ===")
print(result["match"]["match_score"])

print("\n=== OVERALL REVIEW SCORE ===")
print(result["review"]["overall_score"])

print("\n=== REWRITTEN SUMMARY ===")
print(result["rewritten"]["summary"])


print("\n=== SUGGESTIONS ===")
for s in result["review"]["suggestions"]:
    print(s)