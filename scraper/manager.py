import asyncio

from .sapo import SapoScraper
from .netempregos import NetEmpregosScraper
from .itjobs import ITJobsScraper
from .google_jobs import GoogleJobsScraper
from .linkedin import LinkedInScraper
from .indeed import IndeedScraper

class ScraperManager:
    def __init__(self):
        self.scrapers = [
            NetEmpregosScraper(),
            LinkedInScraper(),
            GoogleJobsScraper(),
            IndeedScraper()
            # SapoScraper(), # Desativado devido a proteções anti-bot pesadas
            # ITJobsScraper() # Desativado devido a proteções anti-bot pesadas
        ]

    async def run_all(self, locations: list[str]):
        tasks = [scraper.scrape(locations) for scraper in self.scrapers]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_jobs = []
        for i, res in enumerate(results):
            scraper_name = self.scrapers[i].__class__.__name__
            if isinstance(res, Exception):
                print(f"[DEBUG] Scraper error ({scraper_name}): {res}")
            else:
                print(f"[DEBUG] {scraper_name} retornou {len(res)} vagas.")
                all_jobs.extend(res)
        return all_jobs
