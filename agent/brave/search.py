from  agent.tools.base import BaseTool
from agent.tools.registry import registry
from agent.config import settings
import httpx

@registry.register
class  BraveSearchTool(BaseTool):
    name:str="Brave_search"
    description:str="Search the internet using Brave Search.Returs top results with titles,URLs and snippets."
    parameters:dict={
        "type":"object",
        "properties":{"query":{"type":"string","description":"Search query"}},
        "required":["query"]
    }

    async def run(self,query:str)->str:
        url="https://api.search.brave.come/v1/search"
        headers={"X-Subscription-Token":settings.BRAVE_API_KEY}
        params={"q":query,"count":10}

        async with httpx.AsyncClient() as client:
            response=await client.get(url,headers=headers,params=params,timeout=20)
            response.raise_for_status()
            data=response.json()

        results=[]
        for item in data.get("web",{}).get("results",[])[:10]:
            results.append(f"{item["title"]}\n{item["url"]}\n{item.get("snippet")}\n")

        return "\n".join(results) or "No results found"

            