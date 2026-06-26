from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_cv(job_description, cv_text):
    prompt = f"""
    You are an expert HR recruiter. Analyze this CV against the job description.

    JOB DESCRIPTION:
    {job_description}

    CV:
    {cv_text}

    Give:
    1. A match score out of 10
    2. Top 3 strenghths of this CV for this job
    3. Top 3 missing skills or weaknesses
    4. One specific advice to improve the CV
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

#test
# job = """
# We are looking for a Full stack Developer with:
# - React.js experience
# - Spring Boot backend
# - Docker knowledge
# - CI/CD pipeline experience
# - Good Communication skills
# """

# cv = """
# Syrine Ahmed - Software Engineer
# Skills: React.js , Spring Boot , Docker , Github Actions , PostgresSQL
# Projects: Built WeLoad platform with microservices architecture
# Education: Software Engineering degree from ESPRIT
# Languages: Arabic, French, English, German
# """

print("=== CV ANALYZER ===")
job = input ("Paste the job description: ")
cv = input("Paste your CV text: ")

print("\nAnalyzing ... 🔍\n")
result = analyze_cv(job, cv)
print(result)