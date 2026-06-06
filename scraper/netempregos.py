import aiohttp
from bs4 import BeautifulSoup

class NetEmpregosScraper:
    async def scrape(self, locations: list[str]) -> list[dict]:
        jobs = []
        try:
            url = "https://www.net-empregos.com/rss.asp"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}) as response:
                    if response.status == 200:
                        xml_data = await response.read()
                        soup = BeautifulSoup(xml_data, 'xml') # Parser XML
                        items = soup.find_all('item')
                        
                        for item in items[:20]:
                            title = item.find('title').text.strip() if item.find('title') else 'Vaga Net-Empregos'
                            link = item.find('link').text.strip() if item.find('link') else ''
                            desc = item.find('description').text.strip() if item.find('description') else ''
                            
                            jobs.append({
                                "title": title,
                                "company": "Confidencial",
                                "location": "Portugal",
                                "link": link,
                                "platform": "Net-Empregos",
                                "description": desc
                            })
        except Exception as e:
            print(f"NetEmpregosScraper Error: {e}")
        return jobs
