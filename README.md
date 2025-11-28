# 🧠 KNOWDEX - AI Research Assistant

<div align="center">

**Your AI Research Assistant with Real-Time Web Search and Citations**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.121+-green.svg)](https://fastapi.tiangolo.com/)
[![Chainlit](https://img.shields.io/badge/Chainlit-1.0+-purple.svg)](https://chainlit.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[Live Demo](https://knowdex.onrender.com/) | [Backend API](https://knowdex.onrender.com/docs)

</div>

---

## 🌟 Features

- **🔍 Real-Time Web Search**: Powered by Brave Search API for the latest information
- **📚 Source Citations**: Every factual claim is backed by verifiable sources
- **💬 Beautiful Chat UI**: Built with Chainlit for an exceptional user experience
- **💾 Chat History**: Automatically saves all conversations with full context
- **🔄 Resume Conversations**: Pick up where you left off anytime
- **🔐 Header Authentication**: No login required - perfect for recruiters!
- **⚡ Streaming Responses**: See answers as they're being generated
- **🌍 African Tech Focus**: Deep knowledge of African technology ecosystem
- **🚀 Dual Deployment**: Both API and Chat UI deployable separately

## 🏗️ Architecture

```
KNOWDEX/
├── agent/              # Core AI agent logic
│   ├── agent.py       # Main research orchestration
│   ├── brave/         # Brave Search integration
│   └── config.py      # Configuration settings
├── backend/           # FastAPI REST API
│   ├── main.py       # API server
│   ├── routers/      # API endpoints
│   ├── models.py     # Database models
│   └── database.py   # DB connection
├── chainlit_app.py   # Chainlit frontend
├── .chainlit         # Chainlit configuration
├── chainlit.md       # Welcome page content
└── public/           # Static assets
```

## 🚀 Quick Start (Local Development)

### Prerequisites

- Python 3.9 or higher
- OpenAI API key
- Brave Search API key

### 1. Clone and Setup

```bash
# Clone the repository
cd KNOWDEX

# Create virtual environment
python -m venv myenv
source myenv/bin/activate  # On Windows: myenv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Brave Search Configuration
BRAVE_API_KEY=your_brave_api_key_here

# Optional: Database
DATABASE_URL=sqlite:///./knowdex_local.db
```

### 3. Run the Application

#### Option A: Run Chainlit Frontend (Recommended)

```bash
chainlit run chainlit_app.py -w
```

Then open your browser to: **http://localhost:8000**

The `-w` flag enables hot-reload during development.

#### Option B: Run FastAPI Backend Only

```bash
uvicorn backend.main:app --reload
```

API Documentation available at: **http://localhost:8000/docs**

### 4. Test the Application

Once running, you can:

- **Chat Interface**: Ask questions like "What are the latest AI developments?"
- **Chat History**: All conversations are automatically saved - click the history icon to view
- **Resume Conversations**: Click any previous conversation to continue where you left off
- **API Endpoint**: POST to `/api/research` with `{"question": "your question"}`
- **View History**: GET `/api/history` to see all past research

### 5. Test Chat History (Optional)

Run the test script to verify everything works:

```bash
python test_chat_history.py
```

This will check:
- ✅ Database setup
- ✅ Chat history storage
- ✅ Authentication
- ✅ All features working

## 📦 Deployment

### Deploying to Render

#### Option 1: Deploy Chainlit Frontend

1. **Create a new Web Service on Render**
2. **Connect your GitHub repository**
3. **Configure the service:**

```yaml
# Build Command
pip install -r requirements.txt

# Start Command
chainlit run chainlit_app.py -h 0.0.0.0 -p $PORT
```

4. **Add Environment Variables:**
   - `OPENAI_API_KEY`
   - `BRAVE_API_KEY`

5. **Deploy!**

#### Option 2: Deploy FastAPI Backend

1. **Create a new Web Service on Render**
2. **Connect your GitHub repository**
3. **Configure the service:**

```yaml
# Build Command
pip install -r requirements.txt

# Start Command
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

4. **Add Environment Variables** (same as above)

#### Option 3: Deploy Both (Docker - Advanced)

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["chainlit", "run", "chainlit_app.py", "-h", "0.0.0.0", "-p", "8000"]
```

Then deploy to Render using Docker.

### Deploying to Other Platforms

<details>
<summary><b>Heroku</b></summary>

Create a `Procfile`:
```
web: chainlit run chainlit_app.py -h 0.0.0.0 -p $PORT
```
</details>

<details>
<summary><b>Railway</b></summary>

Add to your Railway configuration:
```
Start Command: chainlit run chainlit_app.py -h 0.0.0.0 -p $PORT
```
</details>

<details>
<summary><b>AWS/Google Cloud/Azure</b></summary>

Use the Docker deployment method for maximum flexibility.
</details>

## 🛠️ API Usage

### Research Endpoint (Streaming)

```bash
curl -X POST "http://localhost:8000/api/research" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the latest developments in AI?"}'
```

### Get Chat History

```bash
curl -X GET "http://localhost:8000/api/history"
```

### Python Client Example

```python
import httpx
import asyncio

async def research(question: str):
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST",
            "http://localhost:8000/api/research",
            json={"question": question}
        ) as response:
            async for chunk in response.aiter_text():
                print(chunk, end="", flush=True)

asyncio.run(research("What is quantum computing?"))
```

## 🎨 Customization

### Modify the AI Prompt

Edit `agent/agent.py` to customize the system prompt and behavior:

```python
SYSTEM_PROMPT = f"""
You are KNOWDEX, the most accurate AI research assistant...
# Add your custom instructions here
"""
```

### Customize the UI

Edit `.chainlit` configuration file:

```toml
[UI]
name = "Your Custom Name"
description = "Your custom description"

[UI.theme.light]
    primary = "#YOUR_COLOR"
```

### Add Custom Styling

Edit `public/style.css` to customize the appearance.

## 📊 Database Schema

```sql
-- Users Table
CREATE TABLE user (
    id UUID PRIMARY KEY,
    email VARCHAR,
    name VARCHAR,
    created_at TIMESTAMP
);

-- Research Table
CREATE TABLE research (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES user(id),
    question TEXT,
    answer TEXT,
    sources JSON,
    created_at TIMESTAMP
);
```

## 🔧 Troubleshooting

### Issue: "Module not found" error

```bash
# Ensure you're in the virtual environment
source myenv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Database not created

```bash
# The database is created automatically on first run
# If issues persist, delete knowdex_local.db and restart
```

### Issue: API keys not working

```bash
# Verify your .env file exists and has the correct keys
cat .env

# Restart the application after adding keys
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for GPT-4 API
- **Brave** for Search API
- **Chainlit** for the amazing chat framework
- **FastAPI** for the robust backend framework

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

<div align="center">

**Built with ❤️ for the AI Engineering Community**

⭐ Star this repo if you find it helpful!

</div>

