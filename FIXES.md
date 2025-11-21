# KNOWDEX Fix Log

## 2025-11-21 Updates

- **Dependency import crash (`requirements.txt`)**  
  - *Line replaced:* inserted `sqlmodel` right after `pydantic-settings`.  
  - *Change:* `sqlmodel` dependency was missing, so importing `create_engine` in `backend/database.py` raised `ModuleNotFoundError`. Adding it ensures the backend starts cleanly.

- **CORS middleware keyword error (`backend/main.py`)**  
  - *Line replaced:* `allow_credential=True` → `allow_credentials=True` inside the `app.add_middleware(...)` call.  
  - *Change:* FastAPI expected the pluralized keyword; the typo caused `TypeError: unexpected keyword argument 'allow_credential'`.

- **Streaming research endpoint returning 500 (`backend/routers/research.py`)**  
  - *Lines replaced:* Entire handler body refactored so the route returns `StreamingResponse(stream_response(), media_type="text/plain")` instead of behaving as an async generator.  
  - *Change:* FastAPI tried to JSON-encode the async generator (`TypeError: 'async_generator' object is not iterable`). The new structure wraps the generator in a `StreamingResponse`, keeps answer aggregation, schedules the DB save in `background_tasks`, and ensures `get_user()` actually fetches/creates the default user by executing the SQLModel query.


