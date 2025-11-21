from sqlmodel import SQLModel,Field
from typing import Optional
from datetime import datetime
import uuid

#User Table
class User(SQLModel,table=True):
    id:uuid.UUID=Field(default_factory=uuid.uuid4,primary_key=True)
    email:str=Field(default="user@knowdex.local",index=True)
    name:Optional[str]=Field(default="Test User")
    created_at:datetime=Field(default_factory=datetime.utcnow)


#Saving every question asked 

class Research(SQLModel,table=True):
    id:uuid.UUID=Field(default_factory=uuid.uuid4,primary_key=True)
    #links research to each user with their individual id
    user_id:uuid.UUID=Field(foreign_key="user.id")
    #what user asked
    question:str=Field(index=True)
    #The full answer from knowdex (with citations)
    answer:str=Field(default="")
    sources:str=Field(default="[]")
    #The time the research  happened
    created_at:datetime=Field(default_factory=datetime.utcnow)
