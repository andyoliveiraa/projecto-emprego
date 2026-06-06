import aiohttp
from bs4 import BeautifulSoup
import urllib.parse

class NetEmpregosScraper:
    async def scrape(self, locations: list[str]) -> list[dict]:
        jobs = []
        try:
            async with aiohttp.ClientSession() as session:
                for loc in locations:
                    url = f"https://www.net-empregos.com/rss.asp?cidade={urllib.parse.quote(loc)}"
                    async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}) as response:
                        if response.status == 200:
                            xml_data = await response.read()
                            soup = BeautifulSoup(xml_data, 'xml')
                            items = soup.find_all('item')
                            
                            for item in items[:20]:
                                title = item.find('title').text.strip() if item.find('title') else 'Vaga Net-Empregos'
                                link = item.find('link').text.strip() if item.find('link') else ''
                                desc = item.find('description').text.strip() if item.find('description') else ''
                                
                                jobs.append({
                                    "title": title,
                                    "company": "Confidencial",
                                    "location": loc,
                                    "link": link,
                                    "platform": "Net-Empregos",
                                    "description": desc
                                })
        except Exception as e:
            print(f"NetEmpregosScraper Error: {e}")
        return jobs
