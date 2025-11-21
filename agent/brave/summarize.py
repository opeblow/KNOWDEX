from agent.tools.base  import BaseTool
from agent.tools.registry import registry
from agent.config import settings
import httpx

@registry.register
class BraveSummarizeTool(BaseTool):
    name:str="brave_summarize"
    description:str="Get a clean,accurate summarry of any webpage using Brave Summarizer"
    parameters:dict={
        "type":"object",
        "properties":{"url":{"type":"string","description":"Full URL of the page"}},
        "required":["url"]
        
    }

    async def run(self,url:str)->str:
        async with httpx.AsyncClient() as client:
            response=await client.get(
                "https://api.search.brave.com/v1/summarizer",
                headers={"X-Suscription-Token":settings.BRAVE_API_KEY},
                params={"url":str},
                timeout=30
            )
            response.raise_for_status()
            data=response.json()
            return data.get("summary","Could not summarize this page.")
