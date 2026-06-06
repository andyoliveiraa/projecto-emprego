from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import uvicorn
from sqlalchemy.orm import Session
from database import get_db, Job, init_db
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
    
    return templates.TemplateResponse("index.html", {"request": request, "jobs": jobs, "metrics": metrics})

@app.post("/update_status/{job_id}")
async def update_status(job_id: int, status: str = Form(...), db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if job:
        job.status = status
        db.commit()
    return RedirectResponse(url="/", status_code=303)

def run_web():
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
