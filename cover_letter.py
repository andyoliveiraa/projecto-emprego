from llm_manager import generate_with_fallback

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
        text = generate_with_fallback(prompt, premium=True, is_json=False)
        return text
    except Exception as e:
        print(f"Error generating cover letter: {e}")
        return "Erro ao gerar carta de motivação."
