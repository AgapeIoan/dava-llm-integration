import openai
import chromadb
import os
import json
from dotenv import load_dotenv
from chromadb.utils import embedding_functions

# Import our custom tool function
from book_tools import get_summary_by_title

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in .env file")

openai.api_key = api_key

# Constants
LLM_MODEL = "gpt-4o-mini"
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "book_summaries"
EMBEDDING_MODEL = "text-embedding-3-small"

# Initialize ChromaDB client and get the collection
print("Connecting to Vector DB...")
client = chromadb.PersistentClient(path=CHROMA_PATH)

# We must specify the same embedding function used during setup
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=api_key,
    model_name=EMBEDDING_MODEL
)
collection = client.get_collection(
    name=COLLECTION_NAME,
    embedding_function=openai_ef
)
print("Connection successful.")


def get_book_recommendation(user_prompt: str):
    """
    Handles the core RAG and LLM interaction.
    """
    results = collection.query(
        query_texts=[user_prompt],
        n_results=3
    )
    
    retrieved_documents = results['documents'][0]
    context = "\n\n".join(retrieved_documents)
    
    print("\n--- Context Retrieved from DB ---")
    print(context)
    print("---------------------------------\n")


if __name__ == "__main__":
    print("Welcome to the Book Recommendation Chatbot!")
    print("Ask me for a book recommendation based on your interests. Type 'exit' to quit.")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
        
        get_book_recommendation(user_input)
