import openai
import chromadb
import os
import json
from dotenv import load_dotenv
from chromadb.utils import embedding_functions

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from book_tools import get_summary_by_title

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY not found in .env file")

openai.api_key = api_key

# Constants
LLM_MODEL = "gpt-4o-mini"
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "book_summaries"
EMBEDDING_MODEL = "text-embedding-3-small"

# Pydantic models for data validation
class ChatRequest(BaseModel):
    prompt: str
    advanced_flow: bool = True

# Structure of the JSON the backend will send back
class ChatResponse(BaseModel):
    response: str
    book_title: str | None = None # Optional field for the recommended book title

app = FastAPI(
    title="Book Recommender API",
    description="An API for recommending books using RAG and OpenAI Tools."
)

print("Connecting to Vector DB...")
db_client = chromadb.PersistentClient(path=CHROMA_PATH)
openai_ef = embedding_functions.OpenAIEmbeddingFunction(api_key=api_key, model_name=EMBEDDING_MODEL)
collection = db_client.get_collection(name=COLLECTION_NAME, embedding_function=openai_ef)
print("Connection to Vector DB successful.")

@app.post("/chat", response_model=ChatResponse)
async def chat_handler(request: ChatRequest):
    """
    Main endpoint to handle chat interactions for book recommendations.
    """
    moderation_response = openai.moderations.create(input=request.prompt)
    if moderation_response.results[0].flagged:
        raise HTTPException(status_code=400, detail="Inappropriate content detected.")

    try:
        print(f"-> Received prompt: '{request.prompt}' with advanced_flow={request.advanced_flow}")
        
        results = collection.query(query_texts=[request.prompt], n_results=3)
        context = "\n\n".join(results['documents'][0])
        
        system_prompt = f"""
You are a helpful and friendly book recommendation chatbot. Your goal is to:
1. Recommend ONE single book based on the user's request and the provided context.
2. After making the recommendation, you MUST call the `get_summary_by_title` tool.
---
CONTEXT:
{context}
---
"""
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": request.prompt}]
        tools = [{"type": "function", "function": {"name": "get_summary_by_title", "description": "Get a book's summary by title.", "parameters": {"type": "object", "properties": {"title": {"type": "string"}}, "required": ["title"]}}}]

        # First call
        response = openai.chat.completions.create(model=LLM_MODEL, messages=messages, tools=tools, tool_choice="auto")
        response_message = response.choices[0].message
        messages.append(response_message)
        
        tool_calls = response_message.tool_calls
        if not tool_calls:
            return ChatResponse(response=response_message.content or "I couldn't find a book. Please rephrase.")

        # Tool execution
        tool_call = tool_calls[0]
        function_args = json.loads(tool_call.function.arguments)
        book_title = function_args.get("title")
        summary = get_summary_by_title(title=book_title)

        # Second call
        messages.append({"tool_call_id": tool_call.id, "role": "tool", "name": "get_summary_by_title", "content": summary})
        final_response = openai.chat.completions.create(model=LLM_MODEL, messages=messages)
        final_content = final_response.choices[0].message.content
        
        return ChatResponse(response=final_content, book_title=book_title)

    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred.")