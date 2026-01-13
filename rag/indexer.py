# rag/indexer.py
import faiss
import os
import pickle
from sentence_transformers import SentenceTransformer

MODEL = SentenceTransformer("all-MiniLM-L6-v2")
VECTOR_DIR = "data/vectors"

os.makedirs(VECTOR_DIR, exist_ok=True)

def chunk_text(text, chunk_size=300):
    words = text.split()
    return [
        " ".join(words[i:i+chunk_size])
        for i in range(0, len(words), chunk_size)
    ]


def build_user_index(user_id, documents: list[str]):
    embeddings = MODEL.encode(documents)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    faiss.write_index(index, f"{VECTOR_DIR}/user_{user_id}.faiss")
    with open(f"{VECTOR_DIR}/user_{user_id}.pkl", "wb") as f:
        pickle.dump(documents, f)