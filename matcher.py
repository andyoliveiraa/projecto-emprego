import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def match_job_with_cv(job_description: str, cv_text: str) -> dict:
    if not cv_text or not job_description:
        return {"score": 0.0, "reason": "CV or Job description missing."}
        
    prompt = f"""
    You are an expert tech recruiter and AI assistant.
    I will provide you with a Job Description and a Candidate's CV.
    Your task is to analyze how well the CV matches the Job Description.

    Job Description:
    {job_description}

    Candidate CV:
    {cv_text}

    Return the result strictly as a valid JSON object with two keys:
    "score": a number from 0 to 100 representing the match percentage.
    "reason": a short, concise sentence (in Portuguese) explaining the score and why they match (or don't match).
    Do not return markdown, just the JSON string.
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:-3].strip()
        elif text.startswith("```"):
            text = text[3:-3].strip()
            
        import json
        result = json.loads(text)
        return {
            "score": float(result.get("score", 0)),
            "reason": result.get("reason", "No reason provided.")
        }
    except Exception as e:
        print(f"Error matching CV: {e}")
        return {"score": 0.0, "reason": "Error during analysis."}
