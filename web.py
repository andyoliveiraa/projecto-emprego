from fastapi import FastAPI, Request, Depends, Form, UploadFile, File, Cookie, Response, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db, User, Job, UserJobMatch, init_db, SearchLog
from auth import get_password_hash, verify_password, create_access_token, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta
from jose import jwt, JWTError
from utils import extract_text_from_pdf
from matcher import adapt_cv_anti_ai
from cover_letter import generate_cover_letter
import os
import unicodedata
from contextlib import asynccontextmanager
import asyncio
from worker import worker_loop, run_scraper_for_user_stream
from fastapi.responses import StreamingResponse

def normalize_text(text: str) -> str:
    if not text:
        return ""
    return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8').lower()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicia o ciclo de extração e IA em background assim que o servidor web arranca
    task = asyncio.create_task(worker_loop())
    yield
    task.cancel()

app = FastAPI(lifespan=lifespan)
init_db()

os.makedirs("templates", exist_ok=True)
templates = Jinja2Templates(directory="templates")

# Dependency to get current user from cookie
def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        if token.startswith("Bearer "):
            token = token[7:]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None
    user = db.query(User).filter(User.username == username).first()
    return user

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html", context={"request": request})

@app.post("/login")
async def login(request: Request, response: Response, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(request=request, name="login.html", context={"request": request, "error": "Credenciais inválidas"})
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html", context={"request": request})

@app.post("/register")
async def register(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == username).first():
        return templates.TemplateResponse(request=request, name="register.html", context={"request": request, "error": "Utilizador já existe"})
    
    hashed_password = get_password_hash(password)
    new_user = User(username=username, password_hash=hashed_password)
    db.add(new_user)
    db.commit()
    return RedirectResponse(url="/login", status_code=303)

@app.get("/logout")
async def logout(response: Response):
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("access_token")
    return response

@app.get("/", response_class=HTMLResponse)
async def dashboard_pending(request: Request, loc: str = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user: return RedirectResponse(url="/login", status_code=303)
    return render_dashboard(request, current_user, db, "Não fiz", "pending", loc)

@app.get("/applied", response_class=HTMLResponse)
async def dashboard_applied(request: Request, loc: str = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user: return RedirectResponse(url="/login", status_code=303)
    return render_dashboard(request, current_user, db, "Já fiz", "applied", loc)

@app.get("/rejected", response_class=HTMLResponse)
async def dashboard_rejected(request: Request, loc: str = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user: return RedirectResponse(url="/login", status_code=303)
    return render_dashboard(request, current_user, db, "Não quero", "rejected", loc)

def render_dashboard(request, current_user, db, target_status, current_page, loc):
    all_matches = db.query(UserJobMatch).filter(UserJobMatch.user_id == current_user.id).all()
    
    metrics = {
        "total": len([m for m in all_matches if m.status != "Lixo"]),
        "applied": sum(1 for m in all_matches if m.status == "Já fiz"),
        "pending": sum(1 for m in all_matches if m.status == "Não fiz"),
        "rejected": sum(1 for m in all_matches if m.status == "Não quero")
    }
    
    matches = [m for m in all_matches if m.status == target_status]
    if loc:
        matches = [m for m in matches if m.job.location and normalize_text(loc) in normalize_text(m.job.location)]
    
    matches.sort(key=lambda x: (1 if x.job.location and "covilha" in normalize_text(x.job.location) else 0, x.job.discovered_at.timestamp() if x.job.discovered_at else 0), reverse=True)
    matches = matches[:100]
    
    return templates.TemplateResponse(
        request=request,
        name="index.html", 
        context={"request": request, "user": current_user, "matches": matches, "metrics": metrics, "current_page": current_page, "current_loc": loc}
    )

@app.post("/update_status/{match_id}")
async def update_status(match_id: int, status: str = Form(...), return_to: str = Form("/"), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user: return RedirectResponse(url="/login", status_code=303)
    match = db.query(UserJobMatch).filter(UserJobMatch.id == match_id, UserJobMatch.user_id == current_user.id).first()
    if match:
        match.status = status
        db.commit()
    return RedirectResponse(url=return_to, status_code=303)

@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request, current_user: User = Depends(get_current_user)):
    if not current_user: return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(request=request, name="settings.html", context={"request": request, "user": current_user})

@app.post("/settings")
async def save_settings(
    locations: str = Form("Covilhã,Mirandela,Remoto,Teletrabalho"),
    webhook_url: str = Form(""),
    cv_file: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user: return RedirectResponse(url="/login", status_code=303)
    
    current_user.locations = locations
    current_user.webhook_url = webhook_url
    
    if cv_file and cv_file.filename:
        pdf_bytes = await cv_file.read()
        text = extract_text_from_pdf(pdf_bytes)
        if text:
            current_user.cv_text = text
            
    db.commit()
    return RedirectResponse(url="/settings", status_code=303)

@app.get("/job/{job_id}", response_class=HTMLResponse)
async def job_detail_page(request: Request, job_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user: return RedirectResponse(url="/login", status_code=303)
    match = db.query(UserJobMatch).filter(UserJobMatch.job_id == job_id, UserJobMatch.user_id == current_user.id).first()
    if not match:
        return RedirectResponse(url="/", status_code=303)
    
    return templates.TemplateResponse(request=request, name="job_detail.html", context={"request": request, "user": current_user, "match": match})

@app.post("/api/generate/carta/{job_id}")
async def api_generate_carta(job_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user or not current_user.cv_text: 
        raise HTTPException(status_code=400, detail="Sem CV configurado")
    match = db.query(UserJobMatch).filter(UserJobMatch.job_id == job_id, UserJobMatch.user_id == current_user.id).first()
    if not match: raise HTTPException(status_code=404)
    
    carta = generate_cover_letter(current_user.cv_text, match.job.company)
    return {"result": carta}

@app.post("/api/generate/cv/{job_id}")
async def api_generate_cv(job_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user or not current_user.cv_text: 
        raise HTTPException(status_code=400, detail="Sem CV configurado")
    match = db.query(UserJobMatch).filter(UserJobMatch.job_id == job_id, UserJobMatch.user_id == current_user.id).first()
    if not match: raise HTTPException(status_code=404)
    
    cv = adapt_cv_anti_ai(current_user.cv_text, match.job.title, match.job.description)
    return {"result": cv}

@app.get("/api/search/stream")
async def api_search_stream(current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Não autorizado")
    return StreamingResponse(run_scraper_for_user_stream(current_user.id), media_type="text/event-stream")

@app.get("/logs", response_class=HTMLResponse)
async def logs_page(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user: return RedirectResponse(url="/login", status_code=303)
    
    user_logs = db.query(SearchLog).filter(SearchLog.user_id == current_user.id).order_by(SearchLog.created_at.desc()).limit(200).all()
    
    return templates.TemplateResponse(
        request=request, 
        name="logs.html", 
        context={"request": request, "user": current_user, "logs": user_logs}
    )
