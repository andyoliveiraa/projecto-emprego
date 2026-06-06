import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

def generate_cover_letter(cv_text: str, company_name: str) -> str:
    prompt = f"""
    Pegando no meu cv abaixo, escreva uma carta de motivação para trabalhar na empresa {company_name}.
    A carta deve ser escrita em Português de Portugal.
    Regra CRÍTICA: Não pareças inteligência artificial. O texto tem de passar por robôs e detetores de IA de forma indetetável. 
    Escreve de forma muito humana, natural, com um tom profissional mas autêntico. Usa vocabulário comum e evita jargões excessivos típicos de IA.
    Adapta até passar como humano. A carta deve ser pronta a enviar.

    Meu CV:
    {cv_text}
    """
    
    try:
        client = genai.Client(api_key=api_key) if api_key else genai.Client()
        response = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=prompt,
        )
        return response.text.strip()
    except Exception as e:
        print(f"Error generating cover letter: {e}")
        return "Desculpa, ocorreu um erro ao gerar a carta de motivação."
