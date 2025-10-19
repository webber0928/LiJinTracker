from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.openapi.docs import get_swagger_ui_html
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
import uuid

load_dotenv()
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class GiftRecord(Base):
    __tablename__ = "gift_records"
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(50), nullable=False)
    amount = Column(Integer, nullable=False)
    category = Column(String(50), nullable=False)
    note = Column(String(255), nullable=True)
    received_cake = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
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
    uuid: str
    created_at: datetime
    updated_at: datetime

app = FastAPI(docs_url=None)  # 關閉預設 /docs

# HTTP Basic Auth 設定
security = HTTPBasic()
def check_auth(credentials: HTTPBasicCredentials = Depends(security)):
    # 帳號密碼可自訂
    if credentials.username != "admin" or credentials.password != "000000":
        raise HTTPException(status_code=401, detail="Unauthorized")

# 受保護的 /docs 路徑
@app.get("/docs", include_in_schema=False)
def custom_swagger_ui(credentials: HTTPBasicCredentials = Depends(security)):
    check_auth(credentials)
    return get_swagger_ui_html(openapi_url=app.openapi_url, title="API Docs")

# 從 .env 讀取 CORS_ORIGINS，格式為逗號分隔字串
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost,http://127.0.0.1,https://webber0928.github.io,https://webber0928.github.io/LiJinTracker/")
origins = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
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

@app.get("/records/{uuid}", response_model=GiftRecordOut)
def read_record(uuid: str):
    db = SessionLocal()
    record = db.query(GiftRecord).filter(GiftRecord.uuid == uuid).first()
    db.close()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record

@app.put("/records/{uuid}", response_model=GiftRecordOut)
def update_record(uuid: str, record: GiftRecordCreate):
    db = SessionLocal()
    db_record = db.query(GiftRecord).filter(GiftRecord.uuid == uuid).first()
    if not db_record:
        db.close()
        raise HTTPException(status_code=404, detail="Record not found")
    for key, value in record.dict().items():
        setattr(db_record, key, value)
    db_record.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_record)
    db.close()
    return db_record

# @app.delete("/records/{uuid}")
# def delete_record(uuid: str):
#     db = SessionLocal()
#     db_record = db.query(GiftRecord).filter(GiftRecord.uuid == uuid).first()
#     if not db_record:
#         db.close()
#         raise HTTPException(status_code=404, detail="Record not found")
#     db_record.is_deleted = True
#     db.commit()
#     db.refresh(db_record)
#     db.close()
#     return {"ok": True}
