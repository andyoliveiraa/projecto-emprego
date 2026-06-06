import aiohttp
from bs4 import BeautifulSoup
import urllib.parse

class LinkedInScraper:
    async def scrape(self, locations: list[str]) -> list[dict]:
        jobs = []
        try:
            async with aiohttp.ClientSession() as session:
                for loc in locations:
                    # Pesquisar vagas gerais na localização sem keywords (conforme pedido)
                    url = f"https://www.linkedin.com/jobs/search/?location={urllib.parse.quote(loc)}"
                    async with session.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}) as response:
                        if response.status == 200:
                            html = await response.read()
                            soup = BeautifulSoup(html, 'html.parser')
                            
                            # Limite de 10 vagas por hora/pesquisa conforme pedido para evitar bloqueios
                            items = soup.find_all('div', class_='base-card')
                            for item in items[:10]:
                                title_el = item.find('h3', class_='base-search-card__title')
                                company_el = item.find('h4', class_='base-search-card__subtitle')
                                location_el = item.find('span', class_='job-search-card__location')
                                link_el = item.find('a', class_='base-card__full-link')
                                
                                title = title_el.text.strip() if title_el else 'Vaga LinkedIn'
                                company = company_el.text.strip() if company_el else 'Confidencial'
                                job_loc = location_el.text.strip() if location_el else loc
                                link = link_el['href'] if link_el and 'href' in link_el.attrs else ''
                                
                                jobs.append({
                                    "title": title,
                                    "company": company,
                                    "location": job_loc,
                                    "link": link.split('?')[0], # Limpar tracking do link
                                    "platform": "LinkedIn",
                                    "description": f"Vaga no LinkedIn para {title} em {company}. Vê o link para mais detalhes."
                                })
        except Exception as e:
            print(f"LinkedInScraper Error: {e}")
        return jobs
