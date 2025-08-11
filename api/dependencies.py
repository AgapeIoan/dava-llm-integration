import os
import openai
import chromadb
from chromadb.utils import embedding_functions

# OpenAI Client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY not found in .env file")
openai_client = openai.OpenAI(api_key=api_key)

# ChromaDB Collection
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "book_summaries"
EMBEDDING_MODEL = "text-embedding-3-small"

db_client = chromadb.PersistentClient(path=CHROMA_PATH)
openai_ef = embedding_functions.OpenAIEmbeddingFunction(api_key=api_key, model_name=EMBEDDING_MODEL)
collection = db_client.get_collection(name=COLLECTION_NAME, embedding_function=openai_ef)

print("Dependencies (OpenAI client and ChromaDB collection) initialized successfully.")