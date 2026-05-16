from agents.jd_analyzer import jd_analyze

sample_jd = """
We are looking for a Python Backend Developer with experience in FastAPI and PostgreSQL.
Nice to have: Docker, Redis, AWS experience.
You will be responsible for building REST APIs, maintaining databases, and collaborating with frontend teams.
We are a fast-paced startup that values innovation.
"""
result = jd_analyze(sample_jd)
print(result)