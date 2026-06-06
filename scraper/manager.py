import asyncio

from .sapo import SapoScraper
from .netempregos import NetEmpregosScraper
from .itjobs import ITJobsScraper
from .google_jobs import GoogleJobsScraper

class ScraperManager:
    def __init__(self):
        self.scrapers = [
            SapoScraper(),
            NetEmpregosScraper(),
            ITJobsScraper(),
            GoogleJobsScraper()
        ]
        self.locations = ["Covilhã", "Mirandela", "Remoto", "Remote"]

    async def run_all(self):
        tasks = [scraper.scrape(self.locations) for scraper in self.scrapers]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_jobs = []
        for res in results:
            if isinstance(res, list):
                all_jobs.extend(res)
            else:
                print(f"Scraper error: {res}")
        return all_jobs
