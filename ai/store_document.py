from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from pathlib import Path

# Load documents
docs_path = Path("docs")
documents = []

for file in docs_path.glob("*.txt"):
    loader = TextLoader(str(file))
    content = loader.load()
    document_name = " ".join(word.capitalize() for word in file.stem.split("_"))
    content[0].metadata["title"] = document_name
    content[0].metadata["source"] = file.name
    documents.append(content[0])

# Embeddings (ONNX-based via fastembed — no torch dependency)
embeddings = FastEmbedEmbeddings(
    model_name="BAAI/bge-small-en-v1.5"
)

# Create vector store
vector_store = FAISS.from_documents(documents, embeddings)

# Persist to disk
vector_store.save_local("vector_store")

print(f"✅ Stored and saved {len(documents)} documents to ./vector_store/")