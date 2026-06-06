import urllib.request
from bs4 import BeautifulSoup

def fetch_and_print(url, site):
    print(f"--- {site} ---")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')
        soup = BeautifulSoup(html, 'html.parser')
        
        # ITJobs
        if site == "ITJobs":
            items = soup.find_all('div', class_='block-container')
            for i in items[:2]:
                title = i.find('a', class_='title')
                company = i.find('div', class_='list-name')
                print("Title:", title.text.strip() if title else 'N/A')
                print("Company:", company.text.strip() if company else 'N/A')
                
        # Net-Empregos
        elif site == "NetEmpregos":
            items = soup.find_all('div', class_='job-offer')
            for i in items[:2]:
                title = i.find('h2')
                print("Title:", title.text.strip() if title else 'N/A')

        # Sapo
        elif site == "Sapo":
            items = soup.find_all('div', attrs={'data-type': 'job-ad'})
            for i in items[:2]:
                title = i.find('h2')
                print("Title:", title.text.strip() if title else 'N/A')
                
    except Exception as e:
        print(f"Error: {e}")

fetch_and_print('https://www.itjobs.pt/emprego?q=Remoto', 'ITJobs')
fetch_and_print('https://www.net-empregos.com/pesquisa-empregos.asp?cidade=Covilh%E3', 'NetEmpregos')
fetch_and_print('https://emprego.sapo.pt/pesquisa?location=Covilh%C3%A3', 'Sapo')
