# ai/server.py
"""FastAPI server for streaming AI chat responses.
This file resides in the project's AI folder and provides an endpoint
`/chat` that streams token chunks using Server‑Sent Events (SSE).
"""

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import os

# Import the existing LangChain agent from main.py
from main import agent

app = FastAPI()

async def sse_generator(message: str):
    """Yield AI response chunks as SSE data lines.
    For a production model you would hook into the LLM token stream.
    Here we invoke the agent synchronously and split the final answer
    into words for a simple streaming demo.
    """
    result = agent.invoke({"messages": [{"role": "user", "content": message}]})
    # Extract content from the last AIMessage
    ai_msg = result.get("messages", [])[-1]
    content = getattr(ai_msg, "content", "") if hasattr(ai_msg, "content") else ai_msg.get("content", "")
    for word in content.split():
        yield f"data: {word}\n\n"

@app.get("/chat")
async def chat_endpoint(request: Request):
    msg = request.query_params.get("message", "")
    if not msg:
        return {"error": "No message provided"}
    return StreamingResponse(sse_generator(msg), media_type="text/event-stream")

