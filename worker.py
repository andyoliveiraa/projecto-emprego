import asyncio
import aiohttp
from database import SessionLocal, Job, UserJobMatch, User
from scraper.manager import ScraperManager
from matcher import match_job_with_cv
import unicodedata

scraper_manager = ScraperManager()

def normalize_text(text: str) -> str:
    if not text: return ""
    return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8').lower()

async def send_discord_webhook(webhook_url: str, title: str, company: str, location: str, match_score: float, match_reason: str, link: str, platform: str):
    if not webhook_url: return
    
    embed = {
        "title": f"Nova vaga imperdível: {title}",
        "url": link,
        "color": 11032055, # Roxo
        "fields": [
            {"name": "Empresa", "value": company, "inline": True},
            {"name": "Localização", "value": location, "inline": True},
            {"name": "Plataforma", "value": platform, "inline": False},
            {"name": "Match Score", "value": f"{match_score}%", "inline": True},
            {"name": "Motivo IA", "value": match_reason, "inline": False}
        ]
    }
    
    payload = {"embeds": [embed]}
    try:
        async with aiohttp.ClientSession() as session:
            await session.post(webhook_url, json=payload)
    except Exception as e:
        print(f"[Worker] Erro ao enviar webhook: {e}")

async def run_scraper_cycle():
    print("[Worker] A iniciar ciclo de extração e avaliação...")
    db = SessionLocal()
    users = db.query(User).all()
    
    all_locations = set()
    for user in users:
        if user.locations:
            for loc in user.locations.split(','):
                all_locations.add(loc.strip())
                
    if not all_locations:
        all_locations = {"Covilhã", "Remoto"}
        
    print(f"[Worker] Procurando nas localizações combinadas: {all_locations}")
    jobs_data = await scraper_manager.run_all(list(all_locations))
    
    for job_data in jobs_data:
        job = db.query(Job).filter(Job.link == job_data["link"]).first()
        if not job:
            job = Job(
                title=job_data["title"],
                company=job_data["company"],
                location=job_data["location"],
                link=job_data["link"],
                platform=job_data["platform"],
                description=job_data["description"]
            )
            db.add(job)
            db.commit()
            db.refresh(job)
            
        for user in users:
            match_exists = db.query(UserJobMatch).filter(UserJobMatch.user_id == user.id, UserJobMatch.job_id == job.id).first()
            if match_exists:
                continue
                
            user_locs = [l.strip() for l in user.locations.split(',')] if user.locations else []
            
            job_text_norm = normalize_text(job.title + " " + job.location + " " + (job.description or ""))
            is_valid_loc = any(normalize_text(loc) in job_text_norm for loc in user_locs)
            
            if not is_valid_loc:
                match = UserJobMatch(user_id=user.id, job_id=job.id, status="Lixo")
                db.add(match)
                db.commit()
                continue
                
            if not user.cv_text:
                match = UserJobMatch(user_id=user.id, job_id=job.id, status="Não fiz")
                db.add(match)
                db.commit()
                continue
                
            print(f"[Worker] IA a calcular Match para utilizador '{user.username}' com vaga '{job.title}'...")
            match_info = match_job_with_cv(job.title, job.description, job.location, user_locs, user.cv_text)
            
            status = "Não fiz"
            if match_info["score"] == 0:
                status = "Lixo"
                
            match = UserJobMatch(
                user_id=user.id,
                job_id=job.id,
                match_score=match_info["score"],
                match_reason=match_info["reason"],
                status=status
            )
            db.add(match)
            db.commit()
            
            if match.match_score > 50 and status != "Lixo" and user.webhook_url:
                await send_discord_webhook(user.webhook_url, job.title, job.company, job.location, match.match_score, match.match_reason, job.link, job.platform)
                
            print(f"[Worker] IA Score {match_info['score']}% - A aguardar 16 segundos (Limite de API Gemini)...")
            await asyncio.sleep(16)
                
    db.close()
    print("[Worker] Ciclo concluído.")

async def worker_loop():
    while True:
        try:
            await run_scraper_cycle()
        except Exception as e:
            print(f"[Worker] Erro crítico no ciclo: {e}")
        print("[Worker] A dormir por 1 hora...")
        await asyncio.sleep(3600)
