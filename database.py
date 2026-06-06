from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./jobs.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    company = Column(String, index=True)
    location = Column(String)
    link = Column(String, unique=True, index=True)
    platform = Column(String)
    description = Column(Text, nullable=True)
    match_score = Column(Float, default=0.0)
    match_reason = Column(Text, nullable=True)
    status = Column(String, default="Não fiz") # "Já fiz", "Não fiz", "Não quero"
    discovered_at = Column(DateTime, default=datetime.utcnow)
    notified = Column(Boolean, default=False)

class UserProfile(Base):
    __tablename__ = "user_profiles"
    discord_id = Column(String, primary_key=True, index=True)
    cv_text = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
