import aiohttp
from bs4 import BeautifulSoup

class ITJobsScraper:
    async def scrape(self, locations):
        jobs = []
        for loc in locations:
            url = f"https://www.itjobs.pt/emprego?q=&location={loc}"
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}) as response:
                        if response.status == 200:
                            html = await response.read()
                            soup = BeautifulSoup(html, 'html.parser')
                            for item in soup.select('.job-item')[:5]: # placeholder class
                                title_el = item.select_one('.title')
                                if title_el:
                                    title = title_el.text.strip()
                                    link = "https://www.itjobs.pt"
                                    jobs.append({
                                        "title": title,
                                        "company": "N/A",
                                        "location": loc,
                                        "link": link,
                                        "platform": "ITJobs",
                                        "description": title
                                    })
            except Exception as e:
                print(f"ITJobsScraper Error: {e}")
        return jobs
