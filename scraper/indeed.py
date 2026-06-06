import aiohttp
from bs4 import BeautifulSoup
import urllib.parse

class IndeedScraper:
    async def scrape(self, locations: list[str]) -> list[dict]:
        jobs = []
        try:
            # Cabeçalhos para tentar contornar bloqueios simples (Indeed é protegido pelo Cloudflare)
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "pt-PT,pt;q=0.9,en-US;q=0.8,en;q=0.7",
                "Sec-Ch-Ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google Chrome\";v=\"114\"",
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": "\"Windows\"",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1"
            }
            
            async with aiohttp.ClientSession() as session:
                for loc in locations:
                    query_loc = loc if loc.lower() != "remoto" else ""
                    query_q = "Remoto" if loc.lower() == "remoto" else ""
                    
                    url = f"https://pt.indeed.com/jobs?q={query_q}&l={urllib.parse.quote(query_loc)}"
                    async with session.get(url, headers=headers) as response:
                        if response.status == 200:
                            html = await response.read()
                            soup = BeautifulSoup(html, 'html.parser')
                            
                            # Indeed cards
                            job_cards = soup.find_all('td', class_='resultContent')
                            
                            for card in job_cards[:15]:
                                title_elem = card.find('h2', class_='jobTitle')
                                title = title_elem.text.strip() if title_elem else "Vaga Indeed"
                                
                                company_elem = card.find('span', class_='companyName') or card.find('span', attrs={"data-testid": "company-name"})
                                company = company_elem.text.strip() if company_elem else "Confidencial"
                                
                                loc_elem = card.find('div', class_='companyLocation') or card.find('div', attrs={"data-testid": "text-location"})
                                location = loc_elem.text.strip() if loc_elem else loc
                                
                                link_elem = card.find('a', class_='jcs-JobTitle')
                                link = "https://pt.indeed.com" + link_elem['href'] if link_elem and 'href' in link_elem.attrs else url
                                
                                jobs.append({
                                    "title": title,
                                    "company": company,
                                    "location": location,
                                    "link": link,
                                    "platform": "Indeed",
                                    "description": f"Vaga no Indeed para {title} na {company} em {location}. Abre o link para detalhes."
                                })
                        else:
                            print(f"[DEBUG] IndeedScraper bloqueado ou com erro ({response.status}) para {loc}")
                            
        except Exception as e:
            print(f"IndeedScraper Error: {e}")
            
        return jobs
