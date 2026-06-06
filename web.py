from fastapi import FastAPI, Request, Depends, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import uvicorn
from sqlalchemy.orm import Session
from database import get_db, Job, AppConfig, init_db
from utils import extract_text_from_pdf
import os

app = FastAPI()
init_db()

os.makedirs("templates", exist_ok=True)
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_jobs(request: Request, db: Session = Depends(get_db)):
    jobs = db.query(Job).order_by(Job.discovered_at.desc()).limit(100).all()
    
    metrics = {
        "total": len(jobs),
        "applied": sum(1 for j in jobs if j.status == "Já fiz"),
        "pending": sum(1 for j in jobs if j.status == "Não fiz"),
        "rejected": sum(1 for j in jobs if j.status == "Não quero")
    }
    
    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={"request": request, "jobs": jobs, "metrics": metrics}
    )

@app.post("/update_status/{job_id}")
async def update_status(job_id: int, status: str = Form(...), db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if job:
        job.status = status
        db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.get("/settings", response_class=HTMLResponse)
async def get_settings(request: Request, db: Session = Depends(get_db)):
    config = db.query(AppConfig).first()
    if not config:
        config = AppConfig()
        db.add(config)
        db.commit()
        db.refresh(config)
    return templates.TemplateResponse(
        request=request, 
        name="settings.html", 
        context={"request": request, "config": config}
    )

@app.post("/settings")
async def save_settings(
    locations: str = Form("Covilhã,Mirandela,Remoto"),
    discord_user_id: str = Form(""),
    cv_file: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    config = db.query(AppConfig).first()
    if not config:
        config = AppConfig()
        db.add(config)
    
    config.locations = locations
    config.discord_user_id = discord_user_id
    
    if cv_file and cv_file.filename:
        pdf_bytes = await cv_file.read()
        text = extract_text_from_pdf(pdf_bytes)
        if text:
            config.cv_text = text
            
    db.commit()
    return RedirectResponse(url="/settings", status_code=303)

def run_web():
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
