import asyncio
from datetime import datetime, timedelta
import pandas as pd

class GoogleJobsScraper:
    def __init__(self):
        self.last_run = None

    def _run_jobspy_sync(self, loc: str) -> list[dict]:
        try:
            from jobspy import scrape_jobs
            # Configura para procurar no Google, Indeed, LinkedIn e Glassdoor em simultâneo
            is_remote = loc.lower() in ["remoto", "teletrabalho"]
            query_loc = "Portugal" if is_remote else f"{loc}, Portugal"
            
            jobs_df = scrape_jobs(
                site_name=["google", "indeed", "linkedin"],
                search_term="Empregos",
                location=query_loc,
                results_wanted=30, # Vagas por plataforma
                country_indeed="portugal",
                is_remote=is_remote
            )
            
            jobs_list = []
            if jobs_df is not None and not jobs_df.empty:
                # Preencher NA com string vazia para não quebrar
                jobs_df = jobs_df.fillna("")
                
                for _, row in jobs_df.iterrows():
                    title = row.get("title", "Vaga")
                    company = row.get("company", "Confidencial")
                    location = row.get("location", loc)
                    link = row.get("job_url", "")
                    desc = row.get("description", "Vaga encontrada pelo sistema JobSpy.")
                    platform = row.get("site", "JobSpy Engine")
                    
                    if title and link:
                        jobs_list.append({
                            "title": str(title),
                            "company": str(company),
                            "location": str(location),
                            "link": str(link),
                            "platform": f"JobSpy ({platform})",
                            "description": str(desc)
                        })
            return jobs_list
        except ImportError:
            print("[ERRO] A biblioteca python-jobspy não está instalada.")
            return []
        except Exception as e:
            print(f"[ERRO JobSpy] Falhou a procurar vagas para {loc}: {e}")
            return []

    async def scrape(self, locations: list[str]) -> list[dict]:
        jobs = []
        
        # O JobSpy é pesado e completo, pode correr a cada hora perfeitamente sem limites da API
        print("[DEBUG] A arrancar o motor JobSpy (Google, Indeed, LinkedIn, Glassdoor)...")
        
        for loc in locations:
            # Corre o web scraper de forma assíncrona para não bloquear o bot (Discord/FastAPI)
            print(f"[DEBUG] JobSpy a procurar vagas em: {loc}...")
            loc_jobs = await asyncio.to_thread(self._run_jobspy_sync, loc)
            jobs.extend(loc_jobs)
            print(f"[DEBUG] JobSpy encontrou {len(loc_jobs)} vagas para {loc}.")
            
            # Pequena pausa entre localizações
            await asyncio.sleep(2)
            
        self.last_run = datetime.now()
        return jobs
