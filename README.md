# 🚀 Empregos Matcher Pro

O **Empregos Matcher Pro** é uma plataforma avançada composta por um portal Web responsivo (FastAPI) e um Bot para o Discord. O seu objetivo principal é poupar tempo na procura de emprego, pesquisando automaticamente em várias plataformas (ex: SAPO Empregos, Net-Empregos, ITJobs) vagas nas zonas da Covilhã, Mirandela e formato Remoto.

Com a integração do **Google Gemini (Inteligência Artificial)**, a plataforma compara o teu currículo (CV) com as exigências da vaga, atribuindo um "Match Score". Além disso, gera cartas de motivação altamente humanas e indetetáveis por filtros de IA, facilitando a tua candidatura!

---

## ✨ Principais Funcionalidades

### 🤖 Bot de Discord
- **Pesquisa Automática:** Corre em background (a cada 1 hora) e notifica-te via DM se a vaga bater certo com o teu CV (> 50%).
- **Comandos:**
  - `!setcv` - Anexa um ficheiro PDF ao enviares este comando para guardares o teu CV na base de dados.
  - `!carta <Nome da Empresa>` - Gera uma carta de motivação personalizada e natural pronta a enviar.

### 🌐 Dashboard Web
- **Design Premium:** Interface moderna em Dark Mode com destaques a roxo e micro-animações.
- **Painel de Métricas:** Estatísticas em tempo real: *Vagas Encontradas*, *Candidaturas Feitas*, *Por Analisar*, *Rejeitadas*.
- **Gestão de Estado:** Altera o estado de qualquer vaga com um clique para gerires as tuas candidaturas de forma eficiente.

---

## 🛠️ Tecnologias Utilizadas
- **Python 3** (Linguagem Principal)
- **FastAPI** + **Uvicorn** (Servidor Web)
- **Discord.py** (Bot Discord)
- **Google Generative AI** (Integração Gemini)
- **SQLAlchemy** + **SQLite** (Base de Dados)
- **BeautifulSoup4** (Web Scraping)
- **Jinja2** (Motor de Templates HTML)

---

## ⚙️ Instalação e Execução Local

Segue os passos abaixo para correres o projeto no teu próprio computador:

### 1. Clonar ou Aceder ao Projeto
Se já tens os ficheiros locais, basta abrir o terminal na pasta. Caso contrário:
```bash
git clone <URL_DO_TEU_REPOSITORIO>
cd projecto-emprego
```

### 2. Criar e Ativar Ambiente Virtual
Para isolar as dependências do projeto:

**No Windows (PowerShell/CMD):**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**No Linux/MacOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependências
Garante que estás com o ambiente virtual ativado (aparece `(venv)` na linha de comandos) e executa:
```bash
pip install -r requirements.txt
```

### 4. Configurar as Variáveis de Ambiente
Abre o ficheiro `.env` que está na raiz do teu projeto e preenche com as tuas chaves secretas:
```env
DISCORD_TOKEN=teu_token_do_discord_bot_aqui
GEMINI_API_KEY=tua_chave_da_google_gemini_aqui
```
> **Dica:** Consegues o `DISCORD_TOKEN` criando uma aplicação no [Discord Developer Portal](https://discord.com/developers/applications). A `GEMINI_API_KEY` adquire-se gratuitamente na consola do [Google AI Studio](https://aistudio.google.com/).

### 5. Iniciar o Projeto
O ficheiro `main.py` encarrega-se de abrir a interface Web numa porta independente e iniciar as rotinas do Discord Bot ao mesmo tempo:
```bash
python main.py
```
*Após iniciar, o teu portal estará disponível no browser em:* `http://localhost:8080`

---

## ☁️ Deploy no Discloud

Este projeto já está otimizado para a plataforma [Discloud](https://discloudbot.com/) (como um "Site", visto que engloba tanto a Web como o Bot, garantindo que as portas não dão conflito).

**Como fazer upload:**
1. Seleciona todos os ficheiros do teu projeto.
2. **Remove da seleção as pastas** `venv/`, `__pycache__/` e a base de dados `jobs.db` para não sobrecarregar o upload.
3. Comprime tudo num ficheiro `.zip`.
4. Vai ao painel da Discloud, clica em "Adicionar App" e envia o ZIP. 
5. O ficheiro `discloud.config` já lá está e dirá aos servidores como iniciar a máquina virtual.

```ini
# Configuração atual incluída no teu projeto (discloud.config)
NAME=EmpregosMatcher
TYPE=site
MAIN=main.py
RAM=512
AUTORESTART=false
VERSION=latest
```

---

## 🚀 Próximos Passos & Expansão
- Adicionar chaves do SerpApi no ficheiro `scraper/google_jobs.py` para ativar extrações do Google Empregos nativamente.
- Refinar os seletores CSS do SAPO e Net-Empregos caso os websites atualizem a interface gráfica.

---

## 📜 Licença
Projeto desenvolvido para fins pessoais de monitorização inteligente e centralização de anúncios de emprego. Ideal para impulsionar a taxa de sucesso nas candidaturas de forma humana e produtiva.
