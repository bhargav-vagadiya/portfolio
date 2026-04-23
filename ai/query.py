from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

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

# Query
query = "which level of education bhargav has done?"
print(f"\n🔍 Query: {query}")
print("-" * 60)

results = vector_store.similarity_search_with_relevance_scores(
    query,
    k=1,
    score_threshold=0.7,
)

if not results:
    print("  ⚠️  No results above threshold.")
else:
    for i, (doc, score) in enumerate(results, 1):
        source = doc.metadata.get("source", "unknown")
        title = doc.metadata.get("title", "unknown")
        print(f"\n  Result #{i}")
        print(f"  📊 Score   : {score:.4f}")
        print(f"  📁 Source  : {source}")
        print(f"  📌 Title   : {title}")
        print(f"  📄 Content : {doc.page_content}")
        print("-" * 60)
