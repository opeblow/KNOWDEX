from agent.tools .base import BaseTool
from agent.tools.registry import registry
import httpx

@registry.register
class WikepediaTool(BaseTool):
    name:str="wikepedia"
    description:str="Search Wikipedia and return  most relevant page content"
    parameters:dict={
        "type":"object",
        "properties":{"query":{"type":"string","description":"Topic to look up"}},
        "required":["query"]

    }
    async def run(self,query:str)->str:
        search_url="https://en.wikipedia.org/w/api.php"
        params={
            "action":"query",
            "list":"search",
            "srsearch":query,
            "format":"json"
        }
        async with httpx.AsyncClient() as client:
            response=await client.get(search_url,params=params)
            data=response.json()
            results=data["query"]["search"]
            if not results:
                return "No wikipedia page found."
            title=results[0]["title"]
            extract_url="https://en.wikipedia.org/api/rest_v1/page/summary/"+ title
            response_2=await client.get(extract_url)
            summary=response_2.json().get("extract","No summary")
            return f"Wikipedia:{title}\n\n{summary}"