from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from pathlib import Path
import os

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

# Embeddings — cache_dir points to model_cache/ inside ai/ so it gets
# committed to git and deployed to Vercel without any runtime download
_CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model_cache")

embeddings = FastEmbedEmbeddings(
    model_name="BAAI/bge-small-en-v1.5",
    cache_dir=_CACHE_DIR
)

# Create vector store
vector_store = FAISS.from_documents(documents, embeddings)

# Persist to disk
vector_store.save_local("vector_store")

print(f"✅ Stored and saved {len(documents)} documents to ./vector_store/")