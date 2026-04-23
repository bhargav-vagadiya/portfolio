from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from pathlib import Path

# Load documents with source tracking
docs_path = Path("docs")
documents = []
for file in docs_path.glob("*.txt"):
    loader = TextLoader(str(file))
    content = loader.load()
    # Inject source filename into metadata
    content[0].metadata["source"] = file.name
    documents.append(content[0])

# Embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en",
    encode_kwargs={"normalize_embeddings": True}
)

# Build vector store
vector_store = FAISS.from_documents(documents, embeddings)
print(f"✅ Stored {len(documents)} documents\n")
print("=" * 60)

# Targeted query
query = "Which database does Bhargav use?"
print(f"\n🔍 Query: {query}")
print("-" * 60)

results = vector_store.similarity_search_with_relevance_scores(query, k=3, score_threshold=0.5)

if not results:
    print("  ⚠️  No results above threshold.")
else:
    for i, (doc, score) in enumerate(results, 1):
        source = doc.metadata.get("source", "unknown")
        from_skills = "✅ YES — from skills.txt!" if source == "skills.txt" else f"❌ NO — from {source}"
        print(f"\n  Result #{i}")
        print(f"  📊 Score     : {score:.4f}")
        print(f"  📁 Source    : {source}  ←  From skills.txt? {from_skills}")
        print(f"  📄 Content   : {doc.page_content[:300]}")
        print()

print("=" * 60)
