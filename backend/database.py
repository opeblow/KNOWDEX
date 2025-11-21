from sqlmodel import SQLModel,create_engine


DATABASE_URL="sqlite:///./knowdex_local.db"

engine=create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    connect_args={"check_same_thread":False}
)

def get_db():
    with engine.begin() as conn:
        yield conn 
