import os
from google import genai
from dotenv import load_dotenv
import json

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

def match_job_with_cv(job_title: str, job_description: str, job_location: str, target_locations: list[str], cv_text: str) -> dict:
    if not cv_text or not job_description:
        return {"score": 0.0, "reason": "CV or Job description missing."}
        
    prompt = f"""
    You are an expert tech recruiter and AI assistant.
    I will provide you with a Job Title, a Job Description and a Candidate's CV.
    Your task is to analyze how well the CV matches the Job Description.

    CRITICAL RULE 1: If the Job Description is written in English or any language other than Portuguese, you MUST return a score of 0, and the reason should be "A vaga não está escrita em Português."
    
    CRITICAL RULE 2: The candidate is ONLY looking for jobs in these locations: {", ".join(target_locations)}. Carefully read the Job Title ("{job_title}"), the stated location ("{job_location}"), and the Job Description. If the true location of the job does not explicitly match one of the target locations (for example, if it is located in the United States, Brazil, or a different city in Portugal that is not Remote), you MUST return a score of 0, and the reason should be "A vaga não é na localização pretendida."

    Job Title:
    {job_title}

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
            model='gemini-1.5-flash',
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

def adapt_cv_anti_ai(cv_text: str, job_title: str, job_description: str) -> str:
    """ Adapta o currículo e passa-o por um detetor de IA interno para garantir humanidade. """
    client = genai.Client(api_key=api_key) if api_key else genai.Client()
    
    # 1. Primeira passagem: Adaptar o CV
    draft_prompt = f"""
    You are an expert resume writer. Adapt the following CV to match this Job Description.
    IMPORTANT: Write in Portuguese. Highlight relevant skills and rephrase experiences to match the job requirements.
    DO NOT use robotic, overly formal, or cliché AI phrases like "Em suma", "Sou um indivíduo altamente motivado", "Com um histórico comprovado".
    Use natural, direct, and conversational professional language. Add slight natural variations in sentence structure.
    
    Job Title: {job_title}
    Job Description: {job_description}
    Candidate CV: {cv_text}
    
    Return ONLY the adapted CV text.
    """
    
    response = client.models.generate_content(model='gemini-2.5-flash', contents=draft_prompt)
    draft_cv = response.text.strip()
    
    # 2. Detetor Anti-IA e Refinamento
    detector_prompt = f"""
    You are an extremely strict AI-detector tool designed to catch AI-generated text.
    Review this resume draft. If it sounds like AI (e.g. uses predictable sentence structures, perfect but soulless formatting, cliché buzzwords like 'proativo', 'histórico comprovado', 'sinergia', 'apaixonado'), you MUST rewrite it to sound 100% like a real, imperfect human professional wrote it.
    
    Rules for the final human version:
    - Write in Portuguese.
    - Keep sentences concise and punchy.
    - Use active voice and specific numbers/metrics where possible.
    - Remove ANY fluffy adjectives.
    - It must look like a normal text resume.
    
    Draft CV:
    {draft_cv}
    
    Return ONLY the final, human-proofed CV.
    """
    
    final_response = client.models.generate_content(model='gemini-2.5-flash', contents=detector_prompt)
    return final_response.text.strip()
