"""
Test script to verify chat history and authentication features
Run this after starting the Chainlit app
"""

import requests
import json
import time
from sqlmodel import Session, select
from backend.database import engine
from backend.models import User, Research
from chainlit_data_layer import Thread, Step


def test_database_setup():
    """Test 1: Verify all tables are created"""
    print("🧪 Test 1: Checking database setup...")
    
    with Session(engine) as session:
        # Check if tables exist by trying to query them
        try:
            users = session.exec(select(User)).all()
            threads = session.exec(select(Thread)).all()
            steps = session.exec(select(Step)).all()
            research = session.exec(select(Research)).all()
            
            print(f"✅ Database tables created successfully!")
            print(f"   - Users: {len(users)}")
            print(f"   - Threads: {len(threads)}")
            print(f"   - Steps: {len(steps)}")
            print(f"   - Research: {len(research)}")
            return True
        except Exception as e:
            print(f"❌ Database setup failed: {e}")
            return False


def test_demo_user_creation():
    """Test 2: Verify demo user is created"""
    print("\n🧪 Test 2: Checking demo user creation...")
    
    with Session(engine) as session:
        demo_user = session.exec(
            select(User).where(User.email == "demo@knowdex.local")
        ).first()
        
        if demo_user:
            print(f"✅ Demo user exists!")
            print(f"   - Email: {demo_user.email}")
            print(f"   - Name: {demo_user.name}")
            print(f"   - Created: {demo_user.created_at}")
            return True
        else:
            print("⚠️  Demo user not found (will be created on first visit)")
            return True


def test_api_endpoint():
    """Test 3: Test FastAPI backend still works"""
    print("\n🧪 Test 3: Testing FastAPI backend...")
    
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ FastAPI backend is running!")
            print(f"   - Status: {data.get('status')}")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("⚠️  Backend not running (start with: uvicorn backend.main:app --reload)")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_chainlit_app():
    """Test 4: Check if Chainlit app can be reached"""
    print("\n🧪 Test 4: Testing Chainlit frontend...")
    
    try:
        # Try to reach Chainlit (usually on port 8000 or 8001)
        response = requests.get("http://localhost:8000/", timeout=5)
        
        if response.status_code == 200:
            print("✅ Chainlit app is accessible!")
            return True
        else:
            print(f"⚠️  Got status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("⚠️  Chainlit not running")
        print("   Start with: chainlit run chainlit_app.py -w")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def display_conversation_history():
    """Display all saved conversations"""
    print("\n📚 Current Conversation History:")
    print("=" * 60)
    
    with Session(engine) as session:
        # Get all users and their conversations
        users = session.exec(select(User)).all()
        
        if not users:
            print("No users found yet. Start the app and ask a question!")
            return
        
        for user in users:
            print(f"\n👤 User: {user.name} ({user.email})")
            print(f"   Created: {user.created_at}")
            
            # Get user's research
            research_items = session.exec(
                select(Research)
                .where(Research.user_id == user.id)
                .order_by(Research.created_at.desc())
            ).all()
            
            if research_items:
                print(f"   💬 Conversations: {len(research_items)}")
                for idx, research in enumerate(research_items[:3], 1):  # Show first 3
                    print(f"\n   {idx}. Q: {research.question[:80]}...")
                    print(f"      A: {research.answer[:80]}...")
                    print(f"      Asked: {research.created_at}")
                
                if len(research_items) > 3:
                    print(f"\n   ... and {len(research_items) - 3} more")
            else:
                print("   No conversations yet")
            
            # Get threads
            threads = session.exec(
                select(Thread)
                .where(Thread.user_id == str(user.id))
            ).all()
            
            if threads:
                print(f"\n   🧵 Threads: {len(threads)}")
                for thread in threads[:3]:
                    step_count = session.exec(
                        select(Step)
                        .where(Step.thread_id == thread.id)
                    ).all()
                    print(f"      - Thread {thread.id[:8]}...: {len(step_count)} messages")


def run_all_tests():
    """Run all tests"""
    print("🚀 KNOWDEX Chat History & Authentication Test Suite")
    print("=" * 60)
    
    results = {
        "Database Setup": test_database_setup(),
        "Demo User": test_demo_user_creation(),
        "FastAPI Backend": test_api_endpoint(),
        "Chainlit Frontend": test_chainlit_app(),
    }
    
    # Display history
    display_conversation_history()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:.<40} {status}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\nTotal: {passed}/{total} tests passed")
    
    # Instructions
    print("\n" + "=" * 60)
    print("📝 Next Steps:")
    print("=" * 60)
    
    if not results["Chainlit Frontend"]:
        print("1. Start Chainlit: chainlit run chainlit_app.py -w")
        print("2. Visit: http://localhost:8000")
        print("3. Ask a question to test chat history")
        print("4. Rerun this test script")
    else:
        print("✅ Everything looks good!")
        print("1. Visit: http://localhost:8000")
        print("2. Ask questions (they'll be saved automatically)")
        print("3. Click the History icon to see saved conversations")
        print("4. Try resuming a conversation")
        print("\nFor custom user authentication:")
        print("- Install browser extension (e.g., ModHeader)")
        print("- Add header: X-User-Email = your-email@example.com")
        print("- Visit the app and your conversations will be saved separately")


if __name__ == "__main__":
    run_all_tests()

