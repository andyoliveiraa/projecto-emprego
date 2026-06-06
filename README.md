# Empregos Matcher

O Empregos Matcher é uma plataforma Web e um Bot de Discord desenvolvidos em Python que pesquisam automaticamente empregos em Portugal (com destaque nas regiões da Covilhã, Mirandela e Remoto) usando plataformas como Sapo Empregos, Net-Empregos e ITJobs.
Cruza automaticamente os requisitos da vaga com o teu CV usando Inteligência Artificial (Google Gemini) e ainda consegue gerar cartas de motivação indetetáveis e com aspeto humano.

## Funcionalidades
- **Bot Discord**:
  - `!setcv`: Define o teu CV carregando um PDF.
  - `!carta <nome-empresa>`: Gera uma carta de motivação.
  - Alertas automáticos na DM em caso de compatibilidade da vaga (> 50%).
- **Portal Web**:
  - Dashboard interativo (Dark Mode Roxo).
  - Gestão de candidaturas ("Já fiz", "Não fiz", "Não quero").
  - Painel de Métricas em tempo real.

## Como Executar Localmente
1. Clona este repositório.
2. Cria um ambiente virtual e instala as dependências:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Configura o ficheiro `.env` na raiz do projeto com as chaves:
   ```
   DISCORD_TOKEN=teu_token_aqui
   GEMINI_API_KEY=tua_chave_aqui
   ```
4. Executa:
   ```bash
   python main.py
   ```
5. O portal web fica ativo em `http://localhost:8080`.

## Hospedagem (Discloud)
Este projeto já inclui o ficheiro `discloud.config` pronto para deploy na Discloud (tipo `site`).
Basta zippar os ficheiros (sem a pasta `venv` nem a base de dados) e fazer upload na plataforma.
