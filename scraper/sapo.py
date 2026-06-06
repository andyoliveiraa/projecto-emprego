import aiohttp
from bs4 import BeautifulSoup

class SapoScraper:
    async def scrape(self, locations):
        jobs = []
        # Exemplo simples de scraping do SAPO
        # Na prática os seletores dependem do HTML atual do site
        for loc in locations:
            url = f"https://emprego.sapo.pt/pesquisa?q=&location={loc}"
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}) as response:
                        if response.status == 200:
                            html = await response.read()
                            soup = BeautifulSoup(html, 'html.parser')
                            # Mock seletores
                            for item in soup.select('.job-offer-card')[:20]:
                                title_el = item.select_one('.job-offer-title a')
                                if title_el:
                                    title = title_el.text.strip()
                                    link = "https://emprego.sapo.pt" + title_el['href']
                                    company = item.select_one('.job-offer-company').text.strip() if item.select_one('.job-offer-company') else "N/A"
                                    jobs.append({
                                        "title": title,
                                        "company": company,
                                        "location": loc,
                                        "link": link,
                                        "platform": "SAPO Emprego",
                                        "description": title
                                    })
            except Exception as e:
                print(f"SapoScraper Error: {e}")
        return jobs
