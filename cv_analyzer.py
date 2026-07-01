from groq import Groq
from dotenv import load_dotenv
import os
import json
import streamlit as st


try:
    api_key = st.secrets["GROQ_API_KEY"]
except:
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=api_key)

def translate_result(result, language):
    if language == "English":
        return result
    
    prompt = f"""
    Translate this JSON content to {language}.
    Translate ONLY the text values, keep the keys and numbers exactly the same.
    Return ONLY the JSON, no extra text.
    
    {json.dumps(result)}
    """
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    
    translated = response.choices[0].message.content.strip()
    
    if "```" in translated:
        translated = translated.split("```")[1]
        if translated.startswith("json"):
            translated = translated[4:]
        translated = translated.strip()
    
    return json.loads(translated)

def analyze_cv(job_description, cv_text, language="English"):
    prompt = f"""
    You are an expert HR recruiter. Analyze this CV against the job description.
    
    JOB DESCRIPTION:
    {job_description}
    
    CV:
    {cv_text}
    
    Respond ONLY with a JSON object, no extra text, no markdown, exactly like this:
    {{
        "score": 8,
        "score_label": "Strong match",
        "strengths": [
            "First strength here",
            "Second strength here",
            "Third strength here"
        ],
        "weaknesses": [
            "First weakness here",
            "Second weakness here",
            "Third weakness here"
        ],
        "skills_match": [
            {{"skill": "React.js", "percent": 90}},
            {{"skill": "Spring Boot", "percent": 85}},
            {{"skill": "Docker", "percent": 80}},
            {{"skill": "Communication", "percent": 40}},
            {{"skill": "Cloud", "percent": 20}}
        ],
        "advice": "One specific advice to improve the CV"
    }}
    """
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    
    result = response.choices[0].message.content.strip()

    if "```" in result:
        result = result.split("```")[1]
        if result.startswith("json"):
            result = result[4:]
        result = result.strip()

    return json.loads(result)

if __name__ == "__main__":
    print("=== CV ANALYZER ===")
    job = input("Paste the job description: ")
    cv = input("Paste your CV text: ")
    print("\nAnalyzing... 🔍\n")
    result = analyze_cv(job, cv)
    print(result)


