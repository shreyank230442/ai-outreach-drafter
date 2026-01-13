# rag/retriever.py
import faiss
import pickle
import os
from sentence_transformers import SentenceTransformer

MODEL = SentenceTransformer("all-MiniLM-L6-v2")
VECTOR_DIR = "data/vectors"

def retrieve_context(user_id, query, k=3):
    index_path = f"{VECTOR_DIR}/user_{user_id}.faiss"
    meta_path = f"{VECTOR_DIR}/user_{user_id}.pkl"

    if not os.path.exists(index_path):
        return ""

    index = faiss.read_index(index_path)
    with open(meta_path, "rb") as f:
        documents = pickle.load(f)

    query_embedding = MODEL.encode([query])
    _, indices = index.search(query_embedding, k)

    return "\n".join(documents[i] for i in indices[0])