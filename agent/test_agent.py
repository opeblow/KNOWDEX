import asyncio
from agent.agent import run_research

async def main():
    print("KNOWDEX is waking up....\n")
    print("Question:Who is the richest man in Africa today?\n")

    async for  chunk in run_research("Who is the richest man in Africa today?"):
        print(chunk,end="",flush=True)

    print("\n\nKNOWDEX has finished")

if __name__=="__main__":
    asyncio.run(main())
    


    