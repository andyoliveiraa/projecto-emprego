import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import asyncio

from database import SessionLocal, Job, UserProfile, init_db
from scraper.manager import ScraperManager
from matcher import match_job_with_cv
from cover_letter import generate_cover_letter
from utils import extract_text_from_pdf

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

scraper_manager = ScraperManager()

@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")
    init_db()
    if not job_scraper_task.is_running():
        job_scraper_task.start()

@bot.command(name="setcv")
async def set_cv(ctx):
    if not ctx.message.attachments:
        await ctx.send("Por favor, anexa o teu CV em formato PDF junto com o comando `!setcv`.")
        return
        
    attachment = ctx.message.attachments[0]
    if not attachment.filename.endswith(".pdf"):
        await ctx.send("O ficheiro deve ser um PDF.")
        return
        
    pdf_bytes = await attachment.read()
    cv_text = extract_text_from_pdf(pdf_bytes)
    
    if not cv_text:
        await ctx.send("Não foi possível extrair o texto do PDF. Verifica se não é uma imagem.")
        return
        
    db = SessionLocal()
    user = db.query(UserProfile).filter(UserProfile.discord_id == str(ctx.author.id)).first()
    if not user:
        user = UserProfile(discord_id=str(ctx.author.id), cv_text=cv_text)
        db.add(user)
    else:
        user.cv_text = cv_text
    db.commit()
    db.close()
    
    await ctx.send("✅ O teu CV foi atualizado com sucesso e será usado para as pesquisas de emprego!")

@bot.command(name="carta")
async def carta_motivacao(ctx, *, empresa: str = None):
    if not empresa:
        await ctx.send("Uso correto: `!carta <nome_da_empresa>`")
        return
        
    db = SessionLocal()
    user = db.query(UserProfile).filter(UserProfile.discord_id == str(ctx.author.id)).first()
    db.close()
    
    if not user or not user.cv_text:
        await ctx.send("Ainda não submeteste o teu CV. Usa `!setcv` anexando um PDF.")
        return
        
    await ctx.send(f"A redigir a carta para a {empresa} de forma humana. Aguarda um momento...")
    carta = generate_cover_letter(user.cv_text, empresa)
    
    if len(carta) > 1900:
        import io
        file = discord.File(io.BytesIO(carta.encode('utf-8')), filename=f"carta_{empresa}.txt")
        await ctx.send("Aqui está a tua carta de motivação:", file=file)
    else:
        await ctx.send(f"```text\n{carta}\n```")

@tasks.loop(hours=1)
async def job_scraper_task():
    print("A iniciar pesquisa de vagas...")
    jobs = await scraper_manager.run_all()
    
    db = SessionLocal()
    users = db.query(UserProfile).all()
    
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
