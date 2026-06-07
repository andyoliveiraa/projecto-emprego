from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

DATABASE_URL = "sqlite:///./jobs_saas.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    webhook_url = Column(String, nullable=True)
    locations = Column(String, default="Covilhã,Mirandela,Remoto,Teletrabalho")
    cv_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    matches = relationship("UserJobMatch", back_populates="user")
    logs = relationship("SearchLog", back_populates="user", cascade="all, delete-orphan")

class SearchLog(Base):
    __tablename__ = "search_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(Text)
    level = Column(String, default="INFO") # INFO, ERROR, WARNING, SUCCESS
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="logs")

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    company = Column(String, index=True)
    location = Column(String)
    link = Column(String, unique=True, index=True)
    platform = Column(String)
    description = Column(Text, nullable=True)
    discovered_at = Column(DateTime, default=datetime.utcnow)
    matches = relationship("UserJobMatch", back_populates="job")

class UserJobMatch(Base):
    __tablename__ = "user_job_matches"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    job_id = Column(Integer, ForeignKey("jobs.id"))
    match_score = Column(Float, default=0.0)
    match_reason = Column(Text, nullable=True)
    status = Column(String, default="Não fiz") # "Não fiz", "Já fiz", "Não quero", "Lixo"
    notified = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="matches")
    job = relationship("Job", back_populates="matches")

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
