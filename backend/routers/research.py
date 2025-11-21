from fastapi import APIRouter,BackgroundTasks
from pydantic import BaseModel
from typing import AsyncGenerator
import json
from agent.agent import run_research
from backend.database import engine
from backend.models import Research,User
from sqlmodel import Session,select
from fastapi.responses import StreamingResponse

router=APIRouter()

class ResearchRequest(BaseModel):
    question:str

def get_user()->User:
    with Session(engine) as session:
        statement=select(User).where(User.email=='user@knowdex.local')
        if not user:
            user=User(email="user@knowdex.local",name="Test User")
            session.add(user)
            session.commit()
            session.refresh(user)

#POST/API/RESEARCH ENDPOINT
@router.post("/research",response_class=StreamingResponse,response_model=None)
async def research_endpoint(
    request:ResearchRequest,
    background_tasks:BackgroundTasks
)->AsyncGenerator[str,None]:
    """
    1. Streams the answer live (word by word)
    2. When finished -> saves everything to database automatically
    """
    user=get_user()
    full_answer=""
    sources_list=[]

    async for chunk in run_research(request.question):
        yield chunk

        if chunk.strip().startswith("http"):
            pass
        elif chunk.strip().startswith("["):
            pass
        else:
            full_answer+=chunk
        
        if "sources:" in chunk or "sources:" in chunk.lower():
            lines=chunk.strip().split("\n")
            for i in range(1,len(lines),2):
                if i + 1 < len(lines):
                    title=lines[i].strip("[]1234567890.")
                    url=lines[i+1].strip()
                    if url.startswith("http"):
                        sources_list.append({"title":title,"url":url})

    def save_to_db():
        with Session(engine) as session:
            research=Research(
                user_id=user.id,
                question=request.question,
                answer=full_answer.strip(),
                sources=json.dumps(sources_list)
            )
            session.add(research)
            session.commit()

    background_tasks.add_task(save_to_db)

    yield "\n\n[DONE]"

    