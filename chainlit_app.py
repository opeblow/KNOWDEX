"""
KNOWDEX - Chainlit Frontend with Chat History & Resume Conversation
This provides a beautiful chat interface with persistent chat history.
"""

import chainlit as cl
from chainlit.types import ThreadDict
from agent.agent import run_research
from backend.database import engine
from backend.models import Research, User
from sqlmodel import Session, select
import json
from datetime import datetime
import uuid
from typing import Optional, Dict, List
import hashlib

# Import data layer
from chainlit_data_layer import cl_data_layer

# Register data layer with Chainlit
cl.data_layer = cl_data_layer


# ==================== USER MANAGEMENT ====================

def get_user_from_header(headers: Dict) -> cl.User:
    """
    Extract user from request headers.
    If X-User-Email header exists, use it. Otherwise, create anonymous user.
    This allows recruiters to use the app without login.
    """
    user_email = headers.get("X-User-Email", None)
    
    if not user_email:
        # Create anonymous user with a unique identifier based on session
        # For recruiters, we'll use a default "demo" user
        user_email = "demo@knowdex.local"
        user_name = "Demo User"
    else:
        user_name = headers.get("X-User-Name", user_email.split("@")[0])
    
    # Get or create user in database
    with Session(engine) as session:
        statement = select(User).where(User.email == user_email)
        user = session.exec(statement).first()
        
        if not user:
            user = User(
                email=user_email,
                name=user_name
            )
            session.add(user)
            session.commit()
            session.refresh(user)
    
    # Return Chainlit User object
    return cl.User(
        identifier=user_email,
        metadata={
            "user_id": str(user.id),
            "name": user.name,
            "email": user.email
        }
    )


@cl.header_auth_callback
def header_auth_callback(headers: Dict) -> Optional[cl.User]:
    """
    Header authentication callback.
    This allows authentication via headers (no login required).
    Perfect for recruiters and demos!
    """
    return get_user_from_header(headers)


# ==================== DATA PERSISTENCE ====================

@cl.on_chat_start
async def on_chat_start():
    """Called when a new chat session starts"""
    
    # Get current user
    user = cl.user_session.get("user")
    
    # Check if we're resuming a thread
    chat_profile = cl.user_session.get("chat_profile")
    thread_id = cl.user_session.get("id")
    
    # Initialize or load conversation
    if thread_id:
        # Resuming existing conversation
        await cl.Message(
            content=f"👋 Welcome back! Resuming your conversation...",
            author="System"
        ).send()
    else:
        # New conversation
        welcome_message = """# 🧠 Welcome to KNOWDEX!

**Your AI Research Assistant with Real-Time Web Search**

I'm KNOWDEX, your most accurate and up-to-date AI research assistant. I can help you with:

✅ **Current Events & News** - Get the latest information from the web
✅ **Research & Analysis** - Deep dives into any topic
✅ **African Tech Ecosystem** - Startups, funding, policies & more
✅ **Verified Sources** - Every claim is cited with sources

**Chat History Enabled!** 
- Your conversations are automatically saved
- You can resume previous conversations anytime
- All your research is searchable

**How to use:**
- Just ask me any question
- I'll search the web in real-time
- You'll get a comprehensive answer with citations

Try asking me about current events, technology trends, or anything you're curious about!
"""
        await cl.Message(content=welcome_message).send()


@cl.on_message
async def on_message(message: cl.Message):
    """Handle incoming messages and stream responses"""
    
    user = cl.user_session.get("user")
    user_metadata = user.metadata if user else {}
    user_id_str = user_metadata.get("user_id")
    
    if not user_id_str:
        await cl.Message(content="❌ Error: User session not found. Please refresh.").send()
        return
    
    user_id = uuid.UUID(user_id_str)
    user_question = message.content
    
    # Create a message object that we'll stream tokens into
    response_msg = cl.Message(content="")
    
    # Variables to collect the full response
    full_answer = ""
    sources_list = []
    in_sources_section = False
    current_source_title = ""
    
    try:
        # Show thinking indicator
        await response_msg.stream_token("🔍 ")
        
        # Stream the research response
        async for chunk in run_research(user_question):
            # Stream the chunk to the UI
            await response_msg.stream_token(chunk)
            
            # Collect the answer for database storage
            full_answer += chunk
            
            # Parse sources from the response
            if "Sources:" in chunk or "sources:" in chunk.lower():
                in_sources_section = True
            
            if in_sources_section:
                lines = chunk.strip().split('\n')
                for line in lines:
                    # Look for source titles (lines starting with [1], [2], etc.)
                    if line.strip() and line.strip()[0] == '[' and ']' in line:
                        current_source_title = line.strip()
                    # Look for URLs
                    elif line.strip().startswith('http'):
                        if current_source_title:
                            sources_list.append({
                                "title": current_source_title,
                                "url": line.strip()
                            })
                            current_source_title = ""
        
        # Send the final message
        await response_msg.send()
        
        # Save to database
        await save_research(
            question=user_question,
            answer=full_answer,
            sources=sources_list,
            user_id=user_id
        )
        
    except Exception as e:
        error_msg = f"\n\n❌ **Error:** {str(e)}\n\nPlease try again or rephrase your question."
        await response_msg.stream_token(error_msg)
        await response_msg.send()


async def save_research(question: str, answer: str, sources: list, user_id: uuid.UUID):
    """Save the research to the database"""
    with Session(engine) as session:
        research = Research(
            user_id=user_id,
            question=question,
            answer=answer,
            sources=json.dumps(sources)
        )
        session.add(research)
        session.commit()


# ==================== CHAT HISTORY CALLBACKS ====================

@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict):
    """
    Called when resuming a previous conversation.
    Loads the chat history and displays it.
    """
    user = cl.user_session.get("user")
    
    if not user:
        return
    
    # Display restoration message
    await cl.Message(
        content=f"🔄 Resuming conversation from {thread.get('createdAt', 'earlier')}...",
        author="System"
    ).send()
    
    # The thread contains the conversation history
    # Chainlit will automatically restore the messages
    # We just need to acknowledge it
    steps = thread.get("steps", [])
    
    if steps:
        await cl.Message(
            content=f"✅ Restored {len(steps)} messages. Continue the conversation below!",
            author="System"
        ).send()


@cl.on_stop
def on_stop():
    """Called when user stops a running task"""
    print("User stopped the task")


@cl.on_chat_end
def on_chat_end():
    """Called when chat session ends"""
    print("Chat session ended")


# ==================== SETTINGS ====================

@cl.set_chat_profiles
async def chat_profile():
    """
    Define chat profiles (optional - can be used for different modes)
    """
    return [
        cl.ChatProfile(
            name="Research Mode",
            markdown_description="Deep research with web search and citations",
            icon="🔍",
        ),
        cl.ChatProfile(
            name="Quick Mode",
            markdown_description="Fast answers without extensive research",
            icon="⚡",
        ),
    ]


# ==================== ACTIONS ====================

@cl.action_callback("view_history")
async def on_action_view_history(action: cl.Action):
    """Show conversation history for the current user"""
    user = cl.user_session.get("user")
    
    if not user:
        await cl.Message(content="❌ User not found").send()
        return
    
    user_metadata = user.metadata
    user_id = uuid.UUID(user_metadata.get("user_id"))
    
    # Fetch recent conversations
    with Session(engine) as session:
        statement = select(Research).where(Research.user_id == user_id).order_by(Research.created_at.desc()).limit(10)
        recent_research = session.exec(statement).all()
        
        if not recent_research:
            await cl.Message(content="📭 No previous conversations found.").send()
            return
        
        # Format history
        history_text = "# 📚 Your Recent Conversations\n\n"
        for idx, research in enumerate(recent_research, 1):
            history_text += f"**{idx}. {research.question[:100]}...**\n"
            history_text += f"   _Asked: {research.created_at.strftime('%Y-%m-%d %H:%M')}_\n\n"
        
        await cl.Message(content=history_text).send()


# ==================== SETTINGS BUTTON ====================

@cl.on_settings_update
async def setup_agent(settings):
    """Called when user updates settings"""
    print("Settings updated:", settings)
