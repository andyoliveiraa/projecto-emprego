import asyncio
import aiohttp
from database import SessionLocal, Job, UserJobMatch, User, SearchLog
from scraper.manager import ScraperManager
from matcher import filter_job_without_cv
import unicodedata
import json

scraper_manager = ScraperManager()

def normalize_text(text: str) -> str:
    if not text: return ""
    return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8').lower()

async def send_discord_webhook(webhook_url: str, title: str, company: str, location: str, match_reason: str, link: str, platform: str):
    if not webhook_url: return
    
    embed = {
        "title": f"Nova vaga imperdível: {title}",
        "url": link,
        "color": 11032055, # Roxo
        "fields": [
            {"name": "Empresa", "value": company, "inline": True},
            {"name": "Localização", "value": location, "inline": True},
            {"name": "Plataforma", "value": platform, "inline": False},
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
        all_locations = {"Covilhã", "Remoto", "Teletrabalho"}
        
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
                
            print(f"[Worker] IA a validar vaga '{job.title}'...")
            match_info = filter_job_without_cv(job.title, job.description, job.location, user_locs)
            
            status = "Não fiz" if match_info["is_valid"] else "Lixo"
                
            match = UserJobMatch(
                user_id=user.id,
                job_id=job.id,
                match_score=0.0,
                match_reason=match_info["reason"],
                status=status
            )
            db.add(match)
            db.commit()
            
            if status != "Lixo" and user.webhook_url:
                await send_discord_webhook(user.webhook_url, job.title, job.company, job.location, match.match_reason, job.link, job.platform)
                
            print(f"[Worker] Validado: {match_info['is_valid']} - A aguardar 16 segundos...")
            await asyncio.sleep(16)
                
    db.close()
    print("[Worker] Ciclo concluído.")

async def log_and_yield(db, user_id, message, level="INFO"):
    log = SearchLog(user_id=user_id, message=message, level=level)
    db.add(log)
    db.commit()
    print(f"[Worker - User {user_id}] {message}")
    return f"data: {json.dumps({'message': message, 'level': level})}\n\n"

async def run_scraper_for_user_stream(user_id: int):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        yield await log_and_yield(db, user_id, "Utilizador não encontrado", "ERROR")
        db.close()
        return

    yield await log_and_yield(db, user.id, f"A iniciar busca forçada para {user.username}...")
    
    locations = [l.strip() for l in user.locations.split(',')] if user.locations else ["Covilhã", "Remoto", "Teletrabalho"]
    yield await log_and_yield(db, user.id, f"A procurar nas localizações: {', '.join(locations)}...")
    
    try:
        jobs_data = await scraper_manager.run_all(locations)
    except Exception as e:
        yield await log_and_yield(db, user.id, f"Erro crítico na extração: {e}", "ERROR")
        db.close()
        return
        
    yield await log_and_yield(db, user.id, f"Foram extraídas {len(jobs_data)} vagas globais.")
    
    novas = 0
    analisadas = 0
    matches_encontrados = 0
    
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
            novas += 1
            
        match_exists = db.query(UserJobMatch).filter(UserJobMatch.user_id == user.id, UserJobMatch.job_id == job.id).first()
        if match_exists:
            continue
            
        analisadas += 1
        
        job_text_norm = normalize_text(job.title + " " + job.location + " " + (job.description or ""))
        is_valid_loc = any(normalize_text(loc) in job_text_norm for loc in locations)
        
        if not is_valid_loc:
            match = UserJobMatch(user_id=user.id, job_id=job.id, status="Lixo")
            db.add(match)
            db.commit()
            continue
            
        try:
            match_info = filter_job_without_cv(job.title, job.description, job.location, locations)
            
            status = "Não fiz" if match_info["is_valid"] else "Lixo"
            if match_info["is_valid"]:
                matches_encontrados += 1
                
            match = UserJobMatch(
                user_id=user.id,
                job_id=job.id,
                match_score=0.0,
                match_reason=match_info["reason"],
                status=status
            )
            db.add(match)
            db.commit()
            
            level = "SUCCESS" if match_info['is_valid'] else "INFO"
            yield await log_and_yield(db, user.id, f"Válido: {match_info['is_valid']} - Motivo: {match_info['reason'][:60]}...", level)
            
            if status != "Lixo" and user.webhook_url:
                await send_discord_webhook(user.webhook_url, job.title, job.company, job.location, match.match_reason, job.link, job.platform)
                yield await log_and_yield(db, user.id, "Notificação enviada para o Discord!", "SUCCESS")
            
            yield await log_and_yield(db, user.id, "Aguardando 16 segundos para respeitar limite da API...")
            await asyncio.sleep(16)
        except Exception as e:
            yield await log_and_yield(db, user.id, f"Erro de IA: {str(e)}", "ERROR")
            
    yield await log_and_yield(db, user.id, f"Busca terminada! {novas} novas no portal, {analisadas} para ti, {matches_encontrados} passaram no filtro IA.", "SUCCESS")
    db.close()

async def worker_loop():
    while True:
        try:
            await run_scraper_cycle()
        except Exception as e:
            print(f"[Worker] Erro crítico no ciclo: {e}")
        print("[Worker] A dormir por 1 hora...")
        await asyncio.sleep(3600)
