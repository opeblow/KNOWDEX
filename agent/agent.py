
from openai import AsyncOpenAI
from agent.config import settings
import json
import asyncio
import httpx
from datetime import datetime
CURRENT_YEAR=datetime.now().year
CURRENT_DATE=datetime.now().strftime("%B %d,%Y")

SYSTEM_PROMPT = f"""
You are KNOWDEX,the most accurate and up-to-date AI research assistant in Africa.
Today's date ia {CURRENT_DATE} ({CURRENT_YEAR})
STRICT RULES-OBEY EVERY SINGLE ONE:
1. Never output HTML tags like <strong>,<b>,<em>,<br>,<p> - Use plain text only.
   Use **bold**  or **italic** with markdown if needed.

2. TIME AWARENESS (THIS IS CRITICAL):
     - If user says "current","now","today","latest","this year","{CURRENT_YEAR}","recent news","population nw";
     ONLY use information from January 1,{CURRENT_YEAR} to today.
     - If user says "recent" or "in the last few years" - use data from {CURRENT_YEAR -5} to {CURRENT_YEAR}.
     - For historical questions (e.g,"technologies in Africa since 2000")->go back as far as needed.
     - Never cite 2023 or 2024 data when user wants current/{CURRENT_YEAR } info.
     - Specific month mentioned ("November","January 2024","october this year")->Only news/events from that exact month/year,
       if no year given -> assume {CURRENT_YEAR}.

3.  Always use brave_search tool FIRST for:
      .News,Population,Prices,Elections,Funding,Startup,Tech,Policy,Sports,Weather,ETC.
      . Any question that changes over time

4.  Every factual claim must end with [1],[2],[3] etc.

5.  At the end,list all sources with full title and URL.

6.  Be concise,professional,and extremly accurate.

7.  Always call brave_search first for anything that changes over time(news,population,prices,startups,artists,elections,etc)

8.   Always make sure you complete user question,for example when user asks about USA presidential election and you search the web using brave_search make sure you search the start of the election to the finish of the election.

9.    Always make sure you start the beginning of a user prompt and make sure you search the whole web to get a result

11.  There are informations all over the web,do not say you could not see anything...thye least you can say is maybe they are keeping the information private ,but there would always be rumours


10.  You are running in {CURRENT_YEAR} -> act like it. Treat today is {CURRENT_DATE}

DO NOT HALLUCINATE.SEARCH FIRST.BE CURRENT.



"""


class CitationManager:
    def __init__(self): 
        self.citations = []
        self.n = 1
    
    def add(self, title, url): 
        self.citations.append(f"[{self.n}] {title}\n{url}")
        self.n += 1
    
    def format(self):
        return "\n\nSources:\n" + "\n".join(self.citations) if self.citations else ""

async def run_research(question: str):
    """Main research function with proper error handling"""
    citations = CitationManager()
    
    yield "KNOWDEX is waking up...\n\n"
    yield f"Question: {question}\n\n"
    yield "Thinking...\n\n"
    
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question}
    ]
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "brave_search",
                "description": "Search the internet for current information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"}
                    },
                    "required": ["query"]
                }
            }
        }
    ]
    
    try:
        
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0
        )
        
        message = response.choices[0].message
        
        
        if message.tool_calls:
            yield "Searching the web...\n\n"
            
            tool_results = []
            
            for tool_call in message.tool_calls:
                if tool_call.function.name == "brave_search":
                    try:
                        args = json.loads(tool_call.function.arguments)
                        query = args.get("query", "")
                        
                        yield f"Searching for: {query}\n"
                        
                        
                        async with httpx.AsyncClient() as http_client:
                            try:
                                r = await http_client.get(
                                    "https://api.search.brave.com/res/v1/web/search",
                                    headers={
                                        "X-Subscription-Token": settings.BRAVE_API_KEY,
                                        "Accept": "application/json"
                                    },
                                    params={"q": query, "count": 5},
                                    timeout=30.0
                                )
                                
                                
                                if r.status_code != 200:
                                    yield f" Search API returned status {r.status_code}\n"
                                    tool_results.append({
                                        "tool_call_id": tool_call.id,
                                        "output": f"Search failed with status {r.status_code}"
                                    })
                                    continue
                                
                                
                                if not r.text or r.text.strip() == "":
                                    yield " Search returned empty response\n"
                                    tool_results.append({
                                        "tool_call_id": tool_call.id,
                                        "output": "No results found"
                                    })
                                    continue
                                
                                
                                data = r.json()
                                
                            
                                results = data.get("web", {}).get("results", [])
                                
                                if not results:
                                    yield "No results found.\n"
                                    tool_results.append({
                                        "tool_call_id": tool_call.id,
                                        "output": "No results found"
                                    })
                                    continue
                                
                                
                                result_text = ""
                                for idx, item in enumerate(results[:3], 1):
                                    title = item.get("title", "No title")
                                    url = item.get("url", "")
                                    snippet = item.get("description", "")
                                    
                                    citations.add(title, url)
                                    result_text += f"{idx}. {title}\n{snippet}\n{url}\n\n"
                                
                                yield result_text
                                
                                tool_results.append({
                                    "tool_call_id": tool_call.id,
                                    "output": result_text
                                })
                                
                            except httpx.TimeoutException:
                                yield f" Search timed out\n"
                                tool_results.append({
                                    "tool_call_id": tool_call.id,
                                    "output": "Search timed out"
                                })
                            
                            except json.JSONDecodeError as e:
                                yield f" Invalid response from search API\n"
                                tool_results.append({
                                    "tool_call_id": tool_call.id,
                                    "output": "Invalid API response"
                                })
                            
                            except httpx.HTTPError as e:
                                yield f" Network error: {str(e)}\n"
                                tool_results.append({
                                    "tool_call_id": tool_call.id,
                                    "output": f"Network error: {str(e)}"
                                })
                    
                    except Exception as e:
                        yield f"Error processing search: {str(e)}\n"
                        tool_results.append({
                            "tool_call_id": tool_call.id,
                            "output": f"Error: {str(e)}"
                        })
            
            
            messages.append({
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in message.tool_calls
                ]
            })
            
            for result in tool_results:
                messages.append({
                    "role": "tool",
                    "tool_call_id": result["tool_call_id"],
                    "content": result["output"]
                })
        
        
        yield "\n\nGenerating answer...\n\n"
        
        final_response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0
        )
        
        answer = final_response.choices[0].message.content
        yield answer
        yield citations.format()
        yield "\n\n KNOWDEX has finished\n"
        
    except Exception as e:
        yield f"\n\n Fatal Error: {str(e)}\n"
        yield "Please check your API keys and try again.\n"


        