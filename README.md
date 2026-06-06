# Empregos AI SaaS 🚀

Uma Plataforma Web Multi-Utilizador baseada em Inteligência Artificial para procura inteligente de vagas de emprego. Construída em Python com **FastAPI** e potenciada pela IA **Google Gemini**.

## 🌟 Funcionalidades Principais

- **Plataforma Multi-Utilizador**: Registo e Autenticação de utilizadores.
- **Painel Central Moderno**: Gestão de vagas ("Pendente", "Já fiz", "Não quero").
- **Avaliador de Match com IA**: A Inteligência Artificial compara cada vaga com o teu PDF de Currículo (CV) e dá uma pontuação. Vagas sem afinidade ou fora da tua zona alvo vão diretamente para o lixo, não poluindo o teu painel.
- **Motor "Anti-Detetor de IA"**: Um mecanismo inovador de duas camadas. O sistema adapta o teu CV à vaga e, a seguir, passa-o por um detetor rigoroso de IA interno. Se cheirar a "robô", ele reescreve até o tom ficar perfeitamente humano!
- **Gerador de Cartas de Motivação**: Cria cartas personalizadas para a empresa com um clique.
- **Notificações por Discord Webhook**: Avisos automáticos no teu servidor do Discord quando são encontradas "vagas imperdíveis" (Match > 50%).

---

## 🛠️ Tecnologias Utilizadas

- **Backend**: FastAPI, Uvicorn, SQLAlchemy (SQLite)
- **Scraping**: Aiohttp, BeautifulSoup4, SerpApi (Google Jobs)
- **Inteligência Artificial**: `google-genai` (Gemini 2.5 Flash)
- **Autenticação**: `passlib`, `bcrypt`, `python-jose`
- **UI/Frontend**: Jinja2 Templates, HTML5/CSS3 (Aesthetics Premium)

---

## ⚙️ Como Configurar e Executar (Deploy/Local)

### 1. Instalar as Dependências
Certifica-te que tens o Python instalado e corre:
```bash
pip install -r requirements.txt
```
*(Nota: Podes precisar de forçar a instalação do `passlib`, `bcrypt`, `python-jose` e `python-multipart`)*

### 2. Variáveis de Ambiente (`.env`)
Cria um ficheiro `.env` na raiz do teu projeto com as seguintes chaves:
```env
DISCORD_TOKEN=se_ainda_usares_bot_antigo_senao_ignora
GEMINI_API_KEY=tua_chave_google_gemini
SERPAPI_KEY=tua_chave_serpapi_para_google_jobs
```

### 3. Iniciar a Plataforma
Inicia o servidor principal. Ele vai lançar a Plataforma Web e ativar os Scrapers de Extração em segundo plano!
```bash
python main.py
```
Acede a `http://localhost:8000` no teu navegador para criar conta e entrar!

---

## 🧭 Como Usar o Portal

1. **Regista-te**: Cria o teu utilizador no ecrã principal.
2. **Vai a ⚙️ Perfil**: Define as tuas cidades de preferência (ex: *Covilhã,Mirandela,Remoto*), submete o teu Currículo em PDF e (opcionalmente) insere o teu link de Webhook do Discord.
3. **Deixa Trabalhar**: A máquina irá varrer as plataformas Sapo, NetEmpregos, LinkedIn e Google Jobs.
4. **Clica numa Vaga**: No painel, abre uma vaga e carrega no botão **"🤖 Adaptar CV (Anti-IA)"** para conseguires a candidatura perfeita aos olhos humanos!

---
Desenvolvido com foco na experiência do utilizador e na máxima eficiência de RH.
