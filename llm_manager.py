import os
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import google.generativeai as genai
from dotenv import load_dotenv

# Dependências adicionais para o fallback
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import anthropic
except ImportError:
    anthropic = None

load_dotenv()

# Configurações de API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def call_gemini(prompt: str, premium: bool) -> str:
    if not GEMINI_API_KEY:
        raise Exception("Gemini API Key missing")
        
    model_name = 'gemini-2.5-flash' if premium else 'gemini-2.0-flash-lite'
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(prompt)
    return response.text.strip()

def call_nvidia(prompt: str, premium: bool) -> str:
    if not NVIDIA_API_KEY or not OpenAI:
        raise Exception("Nvidia API Key missing or openai package not installed")
        
    client = OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=NVIDIA_API_KEY
    )
    
    # Podemos usar o meta/llama-3.1-70b-instruct gratuito fornecido pela Nvidia
    model_name = "meta/llama-3.1-70b-instruct"
    
    completion = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        top_p=0.7,
        max_tokens=2048,
    )
    return completion.choices[0].message.content.strip()

def call_claude(prompt: str, premium: bool) -> str:
    if not CLAUDE_API_KEY or not anthropic:
        raise Exception("Claude API Key missing or anthropic package not installed")
        
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    
    # Sonnet para premium, Haiku para tarefas rápidas
    model_name = "claude-3-5-sonnet-20241022" if premium else "claude-3-haiku-20240307"
    
    message = client.messages.create(
        model=model_name,
        max_tokens=2048,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return message.content[0].text.strip()

def generate_with_fallback(prompt: str, premium: bool = False, is_json: bool = False, provider: str = "gemini") -> str:
    """
    Tenta gerar conteúdo passando pelos 3 modelos.
    Se provider="nvidia", tenta Nvidia -> Gemini -> Claude
    """
    
    errors = []
    
    if provider == "nvidia":
        try:
            print("[LLM Manager] A tentar Nvidia (Primário)...")
            result = call_nvidia(prompt, premium)
            if result: return result
        except Exception as e:
            errors.append(f"Nvidia Error: {e}")
            print(f"[LLM Manager] Nvidia falhou. {e}")
            
        try:
            result = call_gemini(prompt, premium)
            if result: return result
        except Exception as e:
            errors.append(f"Gemini Error: {e}")
            
        try:
            result = call_claude(prompt, premium)
            if result: return result
        except Exception as e:
            errors.append(f"Claude Error: {e}")
            
    else:
        # 1. Tentar Gemini
        try:
            # print("[LLM Manager] A tentar Gemini...") # Reduzir spam na consola
            result = call_gemini(prompt, premium)
            if result:
                return result
        except Exception as e:
            error_msg = str(e)
            short_error = error_msg.split('\n')[0] if '\n' in error_msg else error_msg
            errors.append(f"Gemini Error: {short_error}")
            
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg or "Quota exceeded" in error_msg:
                print(f"[LLM Manager] Gemini atingiu o limite (429). A ativar fallback automático...")
            else:
                print(f"[LLM Manager] Gemini falhou. {short_error}")
                
        # 2. Tentar Nvidia (Llama)
        try:
            print("[LLM Manager] A tentar Nvidia (Fallback 1)...")
            result = call_nvidia(prompt, premium)
            if result:
                return result
        except Exception as e:
            errors.append(f"Nvidia Error: {e}")
            print(f"[LLM Manager] Nvidia falhou. {e}")

        # 3. Tentar Claude
        try:
            print("[LLM Manager] A tentar Claude (Fallback 2)...")
            result = call_claude(prompt, premium)
            if result:
                return result
        except Exception as e:
            errors.append(f"Claude Error: {e}")
            print(f"[LLM Manager] Claude falhou. {e}")
            
        # Se falharam todos
        if is_json:
            return '{"is_valid": false, "reason": "Erro Crítico: Todas as IAs falharam."}'
        else:
            return f"Erro Crítico ao gerar conteúdo. Todas as IAs falharam. Logs: {' | '.join(errors)}"
