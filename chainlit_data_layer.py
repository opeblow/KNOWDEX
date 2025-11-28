"""
Chainlit Data Layer for Chat History Persistence
This implements Chainlit's data persistence interface using our SQLite database.
"""

from chainlit.data import BaseDataLayer, queue_until_user_message
from chainlit.element import Element
from chainlit.step import StepDict
from chainlit.types import Pagination, ThreadDict, ThreadFilter
from typing import Dict, List, Optional
from sqlmodel import Session, select, col
from backend.database import engine
from backend.models import User
import json
from datetime import datetime
import uuid


# ==================== MODELS FOR CHAT HISTORY ====================

from sqlmodel import SQLModel, Field
from datetime import datetime


class Thread(SQLModel, table=True):
    """Represents a conversation thread"""
    __tablename__ = "threads"
    
    id: str = Field(primary_key=True)
    user_id: str = Field(index=True)
    name: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    thread_metadata: str = Field(default="{}")  # JSON string (renamed from metadata to avoid conflict)
    tags: Optional[str] = Field(default=None)  # JSON string of tags


class Step(SQLModel, table=True):
    """Represents a message/step in a conversation"""
    __tablename__ = "steps"
    
    id: str = Field(primary_key=True)
    thread_id: str = Field(foreign_key="threads.id", index=True)
    parent_id: Optional[str] = Field(default=None)
    name: Optional[str] = Field(default=None)
    type: str = Field(default="user_message")
    input: Optional[str] = Field(default=None)
    output: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    start_time: Optional[str] = Field(default=None)
    end_time: Optional[str] = Field(default=None)
    generation: Optional[str] = Field(default=None)  # JSON string
    step_metadata: str = Field(default="{}")  # JSON string (renamed from metadata to avoid conflict)


class ElementModel(SQLModel, table=True):
    """Represents file/element attachments"""
    __tablename__ = "elements"
    
    id: str = Field(primary_key=True)
    thread_id: str = Field(foreign_key="threads.id", index=True)
    type: str
    url: Optional[str] = Field(default=None)
    name: str
    display: str = Field(default="inline")
    size: Optional[str] = Field(default=None)
    language: Optional[str] = Field(default=None)
    for_id: Optional[str] = Field(default=None)
    mime: Optional[str] = Field(default=None)


# Create tables
with engine.begin() as conn:
    SQLModel.metadata.create_all(bind=conn)


# ==================== DATA LAYER IMPLEMENTATION ====================

class KnowdexDataLayer(BaseDataLayer):
    """
    Custom data layer for KNOWDEX using SQLite.
    Implements Chainlit's data persistence interface.
    """
    
    async def get_user(self, identifier: str) -> Optional[Dict]:
        """Get user by identifier (email)"""
        with Session(engine) as session:
            statement = select(User).where(User.email == identifier)
            user = session.exec(statement).first()
            
            if user:
                return {
                    "id": str(user.id),
                    "identifier": user.email,
                    "metadata": {
                        "name": user.name,
                        "email": user.email,
                        "created_at": user.created_at.isoformat()
                    }
                }
        return None
    
    async def create_user(self, user: Dict) -> Optional[Dict]:
        """Create a new user"""
        with Session(engine) as session:
            new_user = User(
                email=user.get("identifier", "unknown@knowdex.local"),
                name=user.get("metadata", {}).get("name", "Unknown User")
            )
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            
            return {
                "id": str(new_user.id),
                "identifier": new_user.email,
                "metadata": {
                    "name": new_user.name,
                    "email": new_user.email
                }
            }
    
    @queue_until_user_message()
    async def create_step(self, step_dict: StepDict):
        """Create a new step (message) in the conversation"""
        with Session(engine) as session:
            step = Step(
                id=step_dict.get("id", str(uuid.uuid4())),
                thread_id=step_dict.get("threadId", ""),
                parent_id=step_dict.get("parentId"),
                name=step_dict.get("name"),
                type=step_dict.get("type", "user_message"),
                input=step_dict.get("input"),
                output=step_dict.get("output"),
                start_time=step_dict.get("start"),
                end_time=step_dict.get("end"),
                generation=json.dumps(step_dict.get("generation")) if step_dict.get("generation") else None,
                step_metadata=json.dumps(step_dict.get("metadata", {}))
            )
            session.add(step)
            session.commit()
    
    async def get_thread(self, thread_id: str) -> Optional[ThreadDict]:
        """Get a thread by ID"""
        with Session(engine) as session:
            # Get thread
            thread = session.exec(
                select(Thread).where(Thread.id == thread_id)
            ).first()
            
            if not thread:
                return None
            
            # Get steps
            steps = session.exec(
                select(Step).where(Step.thread_id == thread_id).order_by(Step.created_at)
            ).all()
            
            # Format thread
            return {
                "id": thread.id,
                "userId": thread.user_id,
                "name": thread.name,
                "createdAt": thread.created_at.isoformat(),
                "metadata": json.loads(thread.thread_metadata) if thread.thread_metadata else {},
                "steps": [
                    {
                        "id": step.id,
                        "threadId": step.thread_id,
                        "parentId": step.parent_id,
                        "name": step.name,
                        "type": step.type,
                        "input": step.input,
                        "output": step.output,
                        "createdAt": step.created_at.isoformat(),
                        "metadata": json.loads(step.step_metadata) if step.step_metadata else {}
                    }
                    for step in steps
                ]
            }
    
    @queue_until_user_message()
    async def update_step(self, step_dict: StepDict):
        """Update an existing step"""
        with Session(engine) as session:
            step = session.exec(
                select(Step).where(Step.id == step_dict.get("id"))
            ).first()
            
            if step:
                if step_dict.get("output"):
                    step.output = step_dict.get("output")
                if step_dict.get("metadata"):
                    step.step_metadata = json.dumps(step_dict.get("metadata"))
                if step_dict.get("end"):
                    step.end_time = step_dict.get("end")
                
                session.add(step)
                session.commit()
    
    @queue_until_user_message()
    async def delete_step(self, step_id: str):
        """Delete a step"""
        with Session(engine) as session:
            step = session.exec(
                select(Step).where(Step.id == step_id)
            ).first()
            
            if step:
                session.delete(step)
                session.commit()
    
    async def list_threads(
        self,
        pagination: Pagination,
        filters: ThreadFilter
    ) -> Dict:
        """List threads for a user with pagination"""
        with Session(engine) as session:
            # Build query
            query = select(Thread)
            
            if filters.userId:
                query = query.where(Thread.user_id == filters.userId)
            
            if filters.search:
                query = query.where(Thread.name.contains(filters.search))
            
            # Order by created date descending
            query = query.order_by(Thread.created_at.desc())
            
            # Get total count
            total_query = select(Thread)
            if filters.userId:
                total_query = total_query.where(Thread.user_id == filters.userId)
            
            # Apply pagination
            offset = (pagination.first or 0)
            limit = 20  # Default limit
            
            threads = session.exec(query.offset(offset).limit(limit)).all()
            
            # Format threads
            formatted_threads = []
            for thread in threads:
                # Get first step for preview
                first_step = session.exec(
                    select(Step)
                    .where(Step.thread_id == thread.id)
                    .order_by(Step.created_at)
                    .limit(1)
                ).first()
                
                formatted_threads.append({
                    "id": thread.id,
                    "userId": thread.user_id,
                    "name": thread.name or (first_step.input[:50] + "..." if first_step and first_step.input else "New Conversation"),
                    "createdAt": thread.created_at.isoformat(),
                    "metadata": json.loads(thread.thread_metadata) if thread.thread_metadata else {}
                })
            
            return {
                "data": formatted_threads,
                "pageInfo": {
                    "hasNextPage": len(formatted_threads) == limit,
                    "startCursor": pagination.first or 0,
                    "endCursor": (pagination.first or 0) + len(formatted_threads)
                }
            }
    
    async def create_thread(
        self,
        thread_id: str,
        user_id: str,
        name: Optional[str] = None,
        metadata: Optional[Dict] = None,
        tags: Optional[List[str]] = None
    ):
        """Create a new thread"""
        with Session(engine) as session:
            thread = Thread(
                id=thread_id,
                user_id=user_id,
                name=name,
                thread_metadata=json.dumps(metadata or {}),
                tags=json.dumps(tags or [])
            )
            session.add(thread)
            session.commit()
    
    async def update_thread(
        self,
        thread_id: str,
        name: Optional[str] = None,
        metadata: Optional[Dict] = None,
        tags: Optional[List[str]] = None
    ):
        """Update a thread"""
        with Session(engine) as session:
            thread = session.exec(
                select(Thread).where(Thread.id == thread_id)
            ).first()
            
            if thread:
                if name is not None:
                    thread.name = name
                if metadata is not None:
                    thread.thread_metadata = json.dumps(metadata)
                if tags is not None:
                    thread.tags = json.dumps(tags)
                
                session.add(thread)
                session.commit()
    
    async def delete_thread(self, thread_id: str):
        """Delete a thread and all its steps"""
        with Session(engine) as session:
            # Delete steps
            steps = session.exec(
                select(Step).where(Step.thread_id == thread_id)
            ).all()
            
            for step in steps:
                session.delete(step)
            
            # Delete thread
            thread = session.exec(
                select(Thread).where(Thread.id == thread_id)
            ).first()
            
            if thread:
                session.delete(thread)
            
            session.commit()
    
    # ==================== REQUIRED ABSTRACT METHODS ====================
    
    async def get_thread_author(self, thread_id: str) -> Optional[str]:
        """Get the author (user_id) of a thread"""
        with Session(engine) as session:
            thread = session.exec(
                select(Thread).where(Thread.id == thread_id)
            ).first()
            
            if thread:
                return thread.user_id
            return None
    
    async def create_element(self, element: "Element"):
        """Create an element (file attachment)"""
        with Session(engine) as session:
            elem = ElementModel(
                id=element.id or str(uuid.uuid4()),
                thread_id=element.thread_id or "",
                type=element.type or "file",
                url=element.url,
                name=element.name or "unnamed",
                display=element.display or "inline",
                size=element.size,
                language=element.language,
                for_id=element.for_id,
                mime=element.mime
            )
            session.add(elem)
            session.commit()
    
    async def get_element(
        self, thread_id: str, element_id: str
    ) -> Optional["Element"]:
        """Get an element by ID"""
        with Session(engine) as session:
            elem = session.exec(
                select(ElementModel)
                .where(ElementModel.thread_id == thread_id)
                .where(ElementModel.id == element_id)
            ).first()
            
            if elem:
                return Element(
                    id=elem.id,
                    thread_id=elem.thread_id,
                    type=elem.type,
                    url=elem.url,
                    name=elem.name,
                    display=elem.display,
                    size=elem.size,
                    language=elem.language,
                    for_id=elem.for_id,
                    mime=elem.mime
                )
            return None
    
    @queue_until_user_message()
    async def delete_element(self, element_id: str):
        """Delete an element"""
        with Session(engine) as session:
            elem = session.exec(
                select(ElementModel).where(ElementModel.id == element_id)
            ).first()
            
            if elem:
                session.delete(elem)
                session.commit()
    
    async def upsert_feedback(self, feedback: Dict) -> str:
        """
        Store user feedback (thumbs up/down on messages).
        For now, we just log it - you can extend this to store in DB.
        """
        feedback_id = feedback.get("id", str(uuid.uuid4()))
        print(f"Feedback received: {feedback}")
        return feedback_id
    
    async def delete_feedback(self, feedback_id: str) -> bool:
        """Delete feedback by ID"""
        print(f"Deleting feedback: {feedback_id}")
        return True
    
    def build_debug_url(self) -> str:
        """Build a debug URL for the data layer"""
        return ""
    
    async def close(self):
        """Close any open connections"""
        # SQLite via SQLModel handles connections automatically
        pass


# Initialize the data layer
cl_data_layer = KnowdexDataLayer()

