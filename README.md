# 🚀 Projecto Emprego AI (Plataforma SaaS Premium)

Bem-vindo à **Empregos AI SaaS**, a tua plataforma pessoal revolucionária para procura inteligente e automatizada de vagas de emprego. Construída em Python com **FastAPI** e potenciada pelos cérebros artificiais da **Google Gemini**, esta plataforma foi desenhada para te poupar horas de pesquisa manual e candidaturas aborrecidas! 🎯

---

## 🌟 Funcionalidades Estrelares

- 👤 **Plataforma Multi-Utilizador**: Registo e autenticação seguros de utilizadores. O teu espaço é apenas teu!
- 🎨 **Painel Central Premium**: Uma interface de luxo, rápida e moderna em *Dark Mode*, para gerir as tuas vagas em listas: *"Pendentes"*, *"Já fiz"* e *"Não quero"*.
- 🧠 **Avaliador de Match (IA de Filtro)**: A Inteligência Artificial da Google atua como o teu recrutador pessoal. Ela lê o teu Currículo em PDF e compara-o detalhadamente com a vaga e a localização. As vagas inúteis ou falsas vão diretamente para o lixo. Só vês o que interessa!
- 🕵️‍♂️ **Motor "Anti-Detetor de IA" (Exclusivo)**: Um mecanismo avançado de duas camadas. O sistema adapta o teu currículo à vaga e, logo de seguida, submete-o a um detetor rigoroso interno. Se o texto cheirar a robô ou a clichés de IA (ex: "proativo", "sinergia"), o sistema reescreve o CV até parecer 100% natural, conversacional e perfeitamente humano! ✨
- ✍️ **Gerador de Cartas de Motivação**: Cria cartas mágicas e prontas a enviar para qualquer empresa com um simples clique.
- 🕷️ **Web Scraping Massivo e à Prova de Bala**: Procura automática em:
  - 🟢 **NetEmpregos** (Maior fonte de vagas em Portugal)
  - 🔵 **LinkedIn** (Raspagem cuidadosa)
  - 🌐 **Google Jobs** (Integração Oficial Inteligente da SerpApi)
  - 🟠 **Indeed** (Raspagem Avançada para furar a Cloudflare)
- 🔔 **Notificações por Discord Webhook**: O teu próprio assistente que te pinga no Discord sempre que uma "vaga de ouro" (Match > 50%) for encontrada na tua cidade!

---

## 🛠️ Stack Tecnológica

- **Backend / Web Server**: FastAPI ⚡, Uvicorn, SQLAlchemy (SQLite)
- **Motores de Scraping**: Aiohttp, BeautifulSoup4, SerpApi Oficial
- **Inteligência Artificial**: `google.generativeai` (Gemini 1.5 Flash 🏎️ e Gemini 2.5 Flash 🧠)
- **Segurança & Autenticação**: `passlib`, `bcrypt`, `python-jose`
- **UI/Frontend**: Jinja2 Templates, HTML5, CSS3, e JavaScript Vanilla com foco numa *Experiência de Utilizador* e design imaculados.

---

## ⚙️ Instalação e Deploy Rápido

### 1. 📦 Instalar Dependências
Garante que tens o Python (3.10+) instalado na tua máquina e executa:
```bash
pip install -r requirements.txt
```

### 2. 🔑 Chaves Mágicas (Configuração `.env`)
Cria um ficheiro escondido com o nome `.env` na raiz do projeto e cola lá os teus segredos:
```env
GEMINI_API_KEY=tua_chave_google_api_aqui
SERPAPI_KEY=tua_chave_serpapi_aqui
```

### 3. 🚀 Ligar os Motores
Inicia a nave mãe. O servidor web e o sistema de varrimento automático arrancam em simultâneo!
```bash
python main.py
```
Acede a `http://localhost:8000` ou `http://localhost:8080` (consoante a configuração) no teu navegador, cria a tua conta e mergulha!

---

## 🧭 O Teu Guia de Sucesso

1. 📝 **Regista-te**: Cria uma conta rapidamente no ecrã de Login.
2. ⚙️ **Vai ao Teu Perfil**: Configura as cidades onde queres trabalhar (ex: *Covilhã, Mirandela, Remoto*). Faz upload do teu **Currículo em formato PDF** (crucial para a IA trabalhar) e, se quiseres alertas, cola o teu link de Webhook do Discord.
3. ☕ **Relaxa e Deixa Trabalhar**: A máquina varre a Sapo, NetEmpregos, LinkedIn, Google Jobs e Indeed automaticamente a cada hora, pontuando os resultados para ti!
4. 💼 **Ataca as Vagas**: No painel, abre os detalhes de uma vaga que gostes e clica no botão brilhante **"🤖 Adaptar CV (Anti-IA)"** ou **"✍️ Gerar Carta"** para obteres uma candidatura letal e perfeita!

---
*Desenvolvido meticulosamente para maximizar a contratação e reduzir as dores de cabeça do utilizador!* 💡
