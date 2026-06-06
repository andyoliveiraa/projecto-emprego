import os
from google import genai
from dotenv import load_dotenv
import json

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

def match_job_with_cv(job_description: str, cv_text: str) -> dict:
    if not cv_text or not job_description:
        return {"score": 0.0, "reason": "CV or Job description missing."}
        
    prompt = f"""
    You are an expert tech recruiter and AI assistant.
    I will provide you with a Job Description and a Candidate's CV.
    Your task is to analyze how well the CV matches the Job Description.

    CRITICAL RULE: If the Job Description is written in English or any language other than Portuguese, you MUST return a score of 0, and the reason should be "A vaga não está escrita em Português."

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
        client = genai.Client(api_key=api_key) if api_key else genai.Client()
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:-3].strip()
        elif text.startswith("```"):
            text = text[3:-3].strip()
            
        result = json.loads(text)
        return {
            "score": float(result.get("score", 0)),
            "reason": result.get("reason", "No reason provided.")
        }
    except Exception as e:
        print(f"Error matching CV: {e}")
        return {"score": 0.0, "reason": "Error during analysis."}
