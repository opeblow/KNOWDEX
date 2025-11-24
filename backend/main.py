from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from backend.routers import research,history
from backend.database import engine
from backend.models import User,Research
import os

with engine.begin() as conn:
    User.metadata.create_all(bind=conn)
    Research.metadata.create_all(bind=conn)

app=FastAPI(
    title="KNOWDEX-AI Research Agent",
    description="Streaming + Citations + Permanent History",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(research.router,prefix="/api")
app.include_router(history.router,prefix="/api")

@app.get("/")
def home():
    return {
        "message":"KNOWDEX Backend is LIVE with permanent memory!",
        "endpoints":{
            "Ask a question(streaming)":"POST/api/research ->{question:'Your question'}",
            "See all saved chats":"GET/api/history"
        },
        "status":"Portfolio-ready"

    }

    