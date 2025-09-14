from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv
import os

load_dotenv()
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class GiftRecord(Base):
    __tablename__ = "gift_records"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    amount = Column(Integer, nullable=False)
    category = Column(String(50), nullable=False)
    note = Column(String(255), nullable=True)
    received_cake = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)

class GiftRecordCreate(BaseModel):
    name: str
    amount: int
    category: str
    note: Optional[str] = None
    received_cake: bool = False

class GiftRecordOut(GiftRecordCreate):
    id: int

app = FastAPI()

# 從 .env 讀取 CORS_ORIGINS，格式為逗號分隔字串
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost,http://127.0.0.1,https://webber0928.github.io,https://webber0928.github.io/LiJinTracker/")
origins = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# 掛載 static 目錄（如果有其他靜態檔案可用）
app.mount("/static", StaticFiles(directory="assets"), name="assets")
import pathlib

# 在 / 直接回傳 index.html
@app.get("/", response_class=HTMLResponse)
def read_index():
    index_path = pathlib.Path(__file__).parent / "index.html"
    with open(index_path, encoding="utf-8") as f:
        return f.read()

@app.post("/records/", response_model=GiftRecordOut)
def create_record(record: GiftRecordCreate):
    db = SessionLocal()
    db_record = GiftRecord(**record.dict())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    db.close()
    return db_record

from fastapi import Query

@app.get("/records/", response_model=List[GiftRecordOut])
def read_records(category: Optional[str] = Query(None)):
    db = SessionLocal()
    query = db.query(GiftRecord).filter(GiftRecord.is_deleted == False)
    if category:
        categories = [c.strip() for c in category.split(",") if c.strip()]
        query = query.filter(GiftRecord.category.in_(categories))
    records = query.all()
    db.close()
    return records

@app.get("/records/{record_id}", response_model=GiftRecordOut)
def read_record(record_id: int):
    db = SessionLocal()
    record = db.query(GiftRecord).filter(GiftRecord.id == record_id).first()
    db.close()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record

@app.put("/records/{record_id}", response_model=GiftRecordOut)
def update_record(record_id: int, record: GiftRecordCreate):
    db = SessionLocal()
    db_record = db.query(GiftRecord).filter(GiftRecord.id == record_id).first()
    if not db_record:
        db.close()
        raise HTTPException(status_code=404, detail="Record not found")
    for key, value in record.dict().items():
        setattr(db_record, key, value)
    db.commit()
    db.refresh(db_record)
    db.close()
    return db_record

@app.delete("/records/{record_id}")
def delete_record(record_id: int):
    db = SessionLocal()
    db_record = db.query(GiftRecord).filter(GiftRecord.id == record_id).first()
    if not db_record:
        db.close()
        raise HTTPException(status_code=404, detail="Record not found")
    db_record.is_deleted = True
    db.commit()
    db.refresh(db_record)
    db.close()
    return {"ok": True}