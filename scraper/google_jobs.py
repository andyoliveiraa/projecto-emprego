class GoogleJobsScraper:
    async def scrape(self, locations):
        jobs = []
        # Scraping direto do Google Jobs requer bypasses complexos ou APIs como SerpApi.
        # Estrutura base implementada para integração futura.
        for loc in locations:
            for result in data.get("organic_results", [])[:20]:
                # TODO: Integrate with SerpApi or similar when API key is available
                pass
        return jobs
