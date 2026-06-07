import os
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import google.generativeai as genai
from dotenv import load_dotenv
import json
from llm_manager import generate_with_fallback

def filter_job_without_cv(job_title: str, job_description: str, job_location: str, target_locations: list[str]) -> dict:
    if not job_description:
        return {"is_valid": False, "reason": "Sem descrição disponível."}
        
    prompt = f"""
    You are an AI assistant.
    I will provide you with a Job Title and a Job Description.
    Your task is ONLY to verify two conditions:
    1. Is the job description written in Portuguese?
    2. Does the job explicitly locate in or allow remote work from these specific locations: {", ".join(target_locations)}?

    CRITICAL RULE 1: If the Job Description is written in English or any language other than Portuguese, you MUST return is_valid as false, and the reason should be "A vaga não está escrita em Português."
    
    CRITICAL RULE 2: Carefully read the Job Title ("{job_title}"), the stated location ("{job_location}"), and the Job Description. If the true location of the job does not explicitly match one of the target locations (for example, if it is located in the United States, Brazil, or a different city in Portugal that is not Remote), you MUST return is_valid as false, and the reason should be "A vaga não é na localização pretendida."

    Job Title:
    {job_title}

    Job Description:
    {job_description}

    Return the result strictly as a valid JSON object with two keys:
    "is_valid": a boolean (true or false).
    "reason": a short, concise sentence (in Portuguese) explaining why.
    Do not return markdown, just the JSON string.
    """
    
    try:
        import re
        text = generate_with_fallback(prompt, premium=False, is_json=True, provider="nvidia")
        
        # Limpar markdown
        if text.startswith("```json"):
            text = text[7:-3].strip()
        elif text.startswith("```"):
            text = text[3:-3].strip()
            
        # Tentar extrair apenas o objeto JSON caso o modelo tenha retornado texto adicional
        match = re.search(r'\\{.*?\\}', text, re.DOTALL)
        if match:
            text = match.group(0)
            
        result = json.loads(text)
        return {
            "is_valid": bool(result.get("is_valid", False)),
            "reason": result.get("reason", "No reason provided.")
        }
    except Exception as e:
        print(f"Error filtering job: {e}")
        return {"is_valid": False, "reason": "Erro durante a análise IA."}

def adapt_cv_anti_ai(cv_text: str, job_title: str, job_description: str) -> str:
    """ Adapta o currículo e passa-o por um detetor de IA interno para garantir humanidade. """

    
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
    try:
        draft_cv = generate_with_fallback(draft_prompt, premium=True, is_json=False)
        
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
        
        text = generate_with_fallback(detector_prompt, premium=True, is_json=False)
        return text
    except Exception as e:
        return f"Erro ao gerar CV: {e}"
