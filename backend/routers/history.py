from fastapi import APIRouter,HTTPException
from sqlmodel import Session,select
from typing import List
from backend.database import engine
from backend.models import Research,User
from pydantic import BaseModel

router=APIRouter()

class ResearchHistoryResponse(BaseModel):
    id:str
    question:str
    answer:str
    sources:str
    created_at:str

#GET/API/HISTORY ENDPOINT
@router.get("/history",response_model=List[ResearchHistoryResponse])
async def get_history():
    """Returns every question and answer a user ever asked KNOWDEX sorted newest first"""
    with Session(engine) as session:
        statement=select(User).where(User.mail=="user@knowdex.local")
        user=session.exec(statement).first()

        if not user:
            raise HTTPException(status_code=404,detail="No User found")
        
        statement=(
            select(Research)
            .where(Research.user_id==user.id)
            .order_by(Research.created_at.desc())
        )
        researches=session.exec(statement).all()

        history=[]
        for r in researches:
            history.append(
                {
                    "id":str(r.id),
                    "question":r.question,
                    "answer":r.answer,
                    "sources":r.sources,
                    "created_at":r.created_at.strftime("%B %d,%Y at %I:%M%p")
                }
            )
        return history
