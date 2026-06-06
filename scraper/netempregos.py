import aiohttp
from bs4 import BeautifulSoup

class NetEmpregosScraper:
    async def scrape(self, locations):
        jobs = []
        for loc in locations:
            # Exemplo url
            url = f"https://www.net-empregos.com/pesquisa-empregos.asp?chaves=&cidade={loc}&categoria=0&zona=0&tipo=0"
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}) as response:
                        if response.status == 200:
                            html = await response.text()
                            soup = BeautifulSoup(html, 'html.parser')
                            for item in soup.select('.job-item')[:5]:
                                title_el = item.select_one('h2 a')
                                if title_el:
                                    title = title_el.text.strip()
                                    link = "https://www.net-empregos.com/" + title_el['href']
                                    jobs.append({
                                        "title": title,
                                        "company": "N/A",
                                        "location": loc,
                                        "link": link,
                                        "platform": "Net-Empregos",
                                        "description": title
                                    })
            except Exception as e:
                print(f"NetEmpregosScraper Error: {e}")
        return jobs
