import aiohttp
import os
import urllib.parse
from dotenv import load_dotenv
from datetime import datetime, timedelta

class GoogleJobsScraper:
    def __init__(self):
        self.last_run = None

    async def scrape(self, locations: list[str]) -> list[dict]:
        jobs = []
        
        # Limitar a execução a 2 vezes por dia (a cada 12 horas)
        if self.last_run and (datetime.now() - self.last_run) < timedelta(hours=12):
            print(f"[DEBUG] Google Jobs ignorado. Aguardando 12h para poupar API (Última vez: {self.last_run.strftime('%Y-%m-%d %H:%M:%S')}).")
            return jobs
            
        load_dotenv()
        api_key = os.getenv("SERPAPI_KEY")
        jobs = []
        
        if not api_key:
            print("🚨 [ERRO CRÍTICO] SERPAPI_KEY não encontrada no .env ou nas variáveis da Discloud! O Google Jobs precisa disto para funcionar.")
            return jobs
            
        try:
            async with aiohttp.ClientSession() as session:
                for loc in locations:
                    url = f"https://serpapi.com/search.json?engine=google_jobs&q=vagas+de+emprego+{urllib.parse.quote(loc)}&hl=pt&gl=pt&api_key={api_key}"
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            if "error" in data:
                                print(f"🚨 [ERRO SERPAPI] {data['error']}")
                            if "jobs_results" not in data:
                                print(f"[DEBUG] SerpApi devolveu 0 resultados para {loc}.")
                            
                            for result in data.get("jobs_results", [])[:20]:
                                title = result.get("title", "Vaga Google Jobs")
                                company = result.get("company_name", "Confidencial")
                                location = result.get("location", loc)
                                link = result.get("related_links", [{"link": ""}])[0].get("link", "")
                                desc = result.get("description", "Vaga encontrada pelo Google Jobs.")
                                
                                jobs.append({
                                    "title": title,
                                    "company": company,
                                    "location": location,
                                    "link": link,
                                    "platform": "Google Jobs",
                                    "description": desc
                                })
                        else:
                            print(f"[DEBUG] Google Jobs error: {response.status}")
            
            # Atualiza o timestamp apenas se chegou ao fim sem erros crasharem o script
            if api_key:
                self.last_run = datetime.now()
                
        except Exception as e:
            print(f"GoogleJobsScraper Error: {e}")
            
        return jobs
