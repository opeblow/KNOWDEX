from pydantic import  BaseModel
from typing import List,Dict,Any,Literal
from datetime import datetime

class citation(BaseModel):
    number:int
    title:str
    url:str
    snippet:str=""

class Message(BaseModel):
    role:Literal["user","assistant","tool","system"]
    content:str
    tool_calls:List[Dict[str,Any]]=[]
    citations:List[citation]=[]

class ResearchRequest(BaseModel):
    question:str
    user_id:str
    session_id:str|None=None

class ResearchResponse(BaseModel):
    session_id:str
    answer:str
    citations:List[citation]
    finished:bool=True