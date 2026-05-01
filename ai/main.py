from typing import Any
import os

from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import before_model
from langchain_community.vectorstores import FAISS
from langchain_core.messages import SystemMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langgraph.runtime import Runtime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://bhargav-vagadiya.github.io"],
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["Content-Type"],
)

class ChatRequest(BaseModel):
    message: str

llm = ChatGroq(
    model="openai/gpt-oss-20b"
)

# Absolute path so it works locally AND on Vercel regardless of cwd
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Use bundled model_cache/ (committed to repo) — no download at runtime
embeddings = FastEmbedEmbeddings(
    model_name="BAAI/bge-small-en-v1.5",
    cache_dir=os.path.join(_BASE_DIR, "model_cache")
)


# Load persisted vector store from disk
vector_store = FAISS.load_local(
    os.path.join(_BASE_DIR, "vector_store"),
    embeddings,
    allow_dangerous_deserialization=True
)

print("✅ Loaded vector store from ./vector_store/")

def extract_text(message):
    content = message.content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(
            item.get("text", "") if isinstance(item, dict) else str(item)
            for item in content
        )
    return str(content)

@before_model
def rag_injection(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    query = extract_text(state["messages"][-1])
    results = vector_store.similarity_search_with_relevance_scores(
        query,
        k=1,
        score_threshold=0.7,
    )
    if results:
        context = "\n\n".join([doc.page_content for doc, _ in results])
        state["messages"] = state["messages"] + [
            SystemMessage(content=f"Answer from this knowledge base: {context}",)
        ]
    return {
        "messages": state["messages"],
    }

@tool(parse_docstring=True)
def fetch_rag(query: str):
    """
    Fetch relevant knowledge from the knowledge base.

    Args:
       query: User question or topic to search.

    Returns:
       Relevant context as plain text.
   """
    # Primary search — lowered threshold so broad queries still match
    results = vector_store.similarity_search_with_relevance_scores(
        query,
        k=3,
        score_threshold=0.45,
    )
    if results:
        return "\n\n".join([doc.page_content for doc, score in results])

    # Fallback — return best-effort top result with no threshold
    fallback = vector_store.similarity_search(query, k=1)
    if fallback:
        return fallback[0].page_content

    return "No information found"


agent = create_agent(
    model=llm,
    name="Bhargav",
    tools=[fetch_rag],
    system_prompt=(
        "You are Bhargav Vagadiya — a Flutter developer. Always answer in first person as Bhargav.\n\n"

        "QUESTION CLASSIFICATION (decide this FIRST before doing anything else):\n\n"

        "CATEGORY A — Portfolio questions (answer these using fetch_rag):\n"
        "  Examples: 'How many years of experience do you have?', 'What projects have you built?',\n"
        "  'What is your tech stack?', 'Are you available for hire?', 'Tell me about yourself',\n"
        "  'What companies have you worked at?', 'What skills do you have?'\n"
        "  → Call fetch_rag, then answer concisely from the retrieved context.\n\n"

        "CATEGORY B — Technical deep-dive / interview questions (DO NOT answer these):\n"
        "  Examples: 'Explain Firebase push notifications', 'How does BLoC work?',\n"
        "  'What is MVVM?', 'Describe REST API', 'How do you handle state management?',\n"
        "  'What are Dart Isolates?', 'Explain socket.io', 'What is your approach to X?',\n"
        "  'What are your strengths/weaknesses?', 'Where do you see yourself in 5 years?'\n"
        "  → Respond EXACTLY: \"Sounds like an interview question! 😄 I'd love to discuss this properly. "
        "Please reach out at bhargav.h.vagadiya@gmail.com to schedule a call.\"\n\n"

        "RULES:\n"
        "- Any question starting with 'Explain', 'How does', 'Describe', 'What is [a concept]', "
        "'How do you implement', 'Walk me through' = CATEGORY B.\n"
        "- General questions about Bhargav's background, experience, or portfolio = CATEGORY A.\n"
        "- For CATEGORY A: always call fetch_rag first; if result is irrelevant, retry with rephrased keywords.\n"
        "- Never invent facts. If fetch_rag returns nothing useful after two tries, say: "
        "'I don't have that detail, feel free to email me at bhargav.h.vagadiya@gmail.com'\n"
        "- Be concise, warm, and professional."
    )
)


print("code compiled.... executing question")

@app.get("/")
def root():
    return {"status": "AI server running"}

@app.post("/chat")
def chat(req: ChatRequest):
    response = agent.invoke({
        "messages": [{"role": "user", "content": req.message}]
    })
    return {"response": response["messages"][-1].content}


@app.post("/chat-stream")
def chat_stream(req: ChatRequest):
    """
    Server-Sent Events streaming endpoint.
    Uses stream_mode='messages' for token-level streaming from the LangGraph agent.
    Each event: data: <text chunk>\n\n
    End marker:  data: [DONE]\n\n
    """
    def generator():
        sent_any = False
        try:
            for chunk in agent.stream(
                {"messages": [{"role": "user", "content": req.message}]},
                stream_mode="messages",
            ):
                # stream_mode="messages" yields (message_chunk, metadata) tuples
                try:
                    msg_chunk, metadata = chunk
                except (TypeError, ValueError):
                    continue

                # NOTE: The node name equals the agent's `name` param ("Bhargav"),
                # NOT the generic string "agent". So we skip the node-name filter
                # and only exclude pure tool-call chunks (empty visible content).
                content = getattr(msg_chunk, "content", None)
                has_tool_calls = bool(getattr(msg_chunk, "tool_calls", None))

                if content and isinstance(content, str) and not has_tool_calls:
                    # SSE: send each line as a separate data: line
                    for line in content.split("\n"):
                        yield f"data: {line}\n"
                    yield "\n"
                    sent_any = True

        except Exception as e:
            print(f"[chat-stream] streaming error: {e}")
            yield f"data: [ERROR] {e}\n\n"
            sent_any = True

        # Fallback: if stream_mode gave nothing, use regular invoke
        if not sent_any:
            try:
                print("[chat-stream] stream was empty — falling back to invoke()")
                response = agent.invoke({
                    "messages": [{"role": "user", "content": req.message}]
                })
                text = response["messages"][-1].content or ""
                for line in text.split("\n"):
                    yield f"data: {line}\n"
                yield "\n"
            except Exception as e2:
                yield f"data: [ERROR] {e2}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )