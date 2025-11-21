import json
from fastapi.responses import StreamingResponse

async def openai_to_sse(generator):
    async for token in generator:
        if token:
            yield f"data:{json.dumps({"type":"token","content":token})}\n\n"

def sse_response(generator):
    return StreamingResponse(openai_to_sse(generator),media_type="text/event-stream")