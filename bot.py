import os
import discord
from discord.ext import commands, tasks
from discord import app_commands
from dotenv import load_dotenv
import asyncio

from database import SessionLocal, Job, UserProfile, AppConfig, init_db
from scraper.manager import ScraperManager
from matcher import match_job_with_cv
from cover_letter import generate_cover_letter
from utils import extract_text_from_pdf

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Removemos o message_content=True para evitar o erro PrivilegedIntentsRequired
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

scraper_manager = ScraperManager()

@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")
    init_db()
    
    # Sincronizar os slash commands
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)
        
    if not job_scraper_task.is_running():
        job_scraper_task.start()

@bot.tree.command(name="setcv", description="Carrega o teu currículo em formato PDF")
@app_commands.describe(ficheiro="O ficheiro PDF do teu currículo")
async def set_cv(interaction: discord.Interaction, ficheiro: discord.Attachment):
    if not ficheiro.filename.endswith(".pdf"):
        await interaction.response.send_message("O ficheiro deve ser um PDF.", ephemeral=True)
        return
        
    pdf_bytes = await ficheiro.read()
    cv_text = extract_text_from_pdf(pdf_bytes)
    
    if not cv_text:
        await interaction.response.send_message("Não foi possível extrair texto. Verifica se não é imagem.", ephemeral=True)
        return
        
    db = SessionLocal()
    user = db.query(UserProfile).filter(UserProfile.discord_id == str(interaction.user.id)).first()
    if not user:
        user = UserProfile(discord_id=str(interaction.user.id), cv_text=cv_text)
        db.add(user)
    else:
        user.cv_text = cv_text
    db.commit()
    db.close()
    
    await interaction.response.send_message("✅ O teu CV foi atualizado com sucesso!", ephemeral=True)

@bot.tree.command(name="carta", description="Gera uma carta de motivação humana para uma empresa")
@app_commands.describe(empresa="O nome da empresa à qual te queres candidatar")
async def carta_motivacao(interaction: discord.Interaction, empresa: str):
    await interaction.response.defer(ephemeral=True)
    
    db = SessionLocal()
    user = db.query(UserProfile).filter(UserProfile.discord_id == str(interaction.user.id)).first()
    config = db.query(AppConfig).first()
    db.close()
    
    cv_text = None
    if user and user.cv_text:
        cv_text = user.cv_text
    elif config and config.cv_text and str(interaction.user.id) == config.discord_user_id:
        cv_text = config.cv_text
        
    if not cv_text:
        await interaction.followup.send("Ainda não submeteste o teu CV. Usa /setcv ou a página web.")
        return
        
    carta = generate_cover_letter(cv_text, empresa)
    
    if len(carta) > 1900:
        import io
        file = discord.File(io.BytesIO(carta.encode('utf-8')), filename=f"carta_{empresa}.txt")
        await interaction.followup.send("Aqui está a tua carta de motivação:", file=file)
    else:
        await interaction.followup.send(f"```text\n{carta}\n```")

@tasks.loop(hours=1)
async def job_scraper_task():
    print("A iniciar pesquisa de vagas...")
    db = SessionLocal()
    
    config = db.query(AppConfig).first()
    locations = ["Covilhã", "Mirandela", "Remoto"]
    if config and config.locations:
        locations = [l.strip() for l in config.locations.split(',')]
        
    jobs = await scraper_manager.run_all(locations)
    users = db.query(UserProfile).all()
    
    if config and config.cv_text and config.discord_user_id:
        if not any(u.discord_id == config.discord_user_id for u in users):
            virtual_user = UserProfile(discord_id=config.discord_user_id, cv_text=config.cv_text)
            users.append(virtual_user)
        else:
            for u in users:
                if u.discord_id == config.discord_user_id:
                    u.cv_text = config.cv_text
    
    for job in jobs:
        existing_job = db.query(Job).filter(Job.link == job["link"]).first()
        if not existing_job:
            new_job = Job(
                title=job["title"],
                company=job["company"],
                location=job["location"],
                link=job["link"],
                platform=job["platform"],
                description=job["description"]
            )
            db.add(new_job)
            db.commit()
            db.refresh(new_job)
            
            for user in users:
                if user.cv_text:
                    match_info = match_job_with_cv(new_job.description, user.cv_text)
                    new_job.match_score = match_info["score"]
                    new_job.match_reason = match_info["reason"]
                    db.commit()
                    
                    if match_info["score"] > 50:
                        try:
                            discord_user = await bot.fetch_user(int(user.discord_id))
                            embed = discord.Embed(title=f"Nova vaga: {new_job.title}", url=new_job.link, color=0x00ff00)
                            embed.add_field(name="Empresa", value=new_job.company, inline=True)
                            embed.add_field(name="Localização", value=new_job.location, inline=True)
                            embed.add_field(name="Plataforma", value=new_job.platform, inline=False)
                            embed.add_field(name="Match Score", value=f"{new_job.match_score}%", inline=True)
                            embed.add_field(name="Motivo", value=new_job.match_reason, inline=False)
                            await discord_user.send(embed=embed)
                        except Exception as e:
                            print(f"Erro ao enviar DM para {user.discord_id}: {e}")
    db.close()
    print("Pesquisa de vagas concluída.")

def run_bot():
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("DISCORD_TOKEN não encontrado no .env")
