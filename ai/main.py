from typing import Any

from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import before_model
from langchain_community.vectorstores import FAISS
from langchain_core.messages import AIMessage, ToolMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from  dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langgraph.runtime import Runtime

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-20b"
)

# Load embeddings (must match what was used during ingestion)
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en",
    encode_kwargs={"normalize_embeddings": True}
)

# Load persisted vector store from disk
vector_store = FAISS.load_local(
    "vector_store",
    embeddings,
    allow_dangerous_deserialization=True
)

print("✅ Loaded vector store from ./vector_store/")

def extract_text(message):
    content = message.content

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        # extract only text parts
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
    results = vector_store.similarity_search_with_relevance_scores(
        query,
        k=1,
        score_threshold=0.7,
    )
    if results:
       return "\n\n".join([doc.page_content for doc, _ in results])
    else :
        return "No information found"



agent = create_agent(model=llm,name="Bhargav AI",tools=[fetch_rag],system_prompt="Only Use *fetch_rag* function to retrieve relevant information.This is a valid & latest information provided officially by bhargav. Try to save token as much as possible.")

print("code compiled.... executing question")


result = agent.invoke(
    {"messages": [{"role": "user", "content": "tell me about your projects."}]}
)

print(result["messages"][-1].content_blocks)
