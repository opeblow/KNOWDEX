from pydantic_settings import BaseSettings
import os

from dotenv import load_dotenv
load_dotenv()


class settings(BaseSettings):
    #My keys
    OPENAI_API_KEY:str=os.getenv("OPENAI_API_KEY")
    BRAVE_API_KEY:str=os.getenv("BRAVE_API_KEY")

    #Model settings
    MODEL:str="gpt-4o-mini"
    TEMPERATURE:float=0.0
    MAX_TOKENS:int=1024

    #Agent's behaviour
    MAX_LOOP:int=12
    STREAMING:bool=True

    class config:
        env_file=".env"
        env_file_encoding="utf-8"

settings=settings()

if not settings.OPENAI_API_KEY or not settings.BRAVE_API_KEY:
    print("Warning:API keys not found set in .env file")


