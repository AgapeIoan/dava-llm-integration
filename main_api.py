import os
import json

import openai
import chromadb
import hashlib

from enum import Enum

from dotenv import load_dotenv
from chromadb.utils import embedding_functions
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

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
    
class ChatResponse(BaseModel):
    response: str
    book_title: str | None = None # Optional field for the recommended book title

class TTSVoice(str, Enum):
    alloy = "alloy"
    echo = "echo"
    fable = "fable"
    onyx = "onyx"
    nova = "nova"
    shimmer = "shimmer"
class TTSRequest(BaseModel):
    text: str
    voice: TTSVoice = TTSVoice.nova

class STTResponse(BaseModel):
    text: str

app = FastAPI(
    title="Book Recommender API",
    description="An API for recommending books using RAG and OpenAI Tools."
)

print("Connecting to Vector DB...")
db_client = chromadb.PersistentClient(path=CHROMA_PATH)
openai_ef = embedding_functions.OpenAIEmbeddingFunction(api_key=api_key, model_name=EMBEDDING_MODEL)
collection = db_client.get_collection(name=COLLECTION_NAME, embedding_function=openai_ef)
print("Connection to Vector DB successful.")

os.makedirs("static/audio", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/speech-to-text", response_model=STTResponse)
async def stt_handler(file: UploadFile = File(...), language: str = Form("en")):
    """
    Accepts an audio file and an optional language code, then transcribes to text.
    """
    print(f"-> Received audio file for transcription: {file.filename}")
    try:
        transcription = openai.audio.transcriptions.create(
            model="whisper-1", 
            file=(file.filename, file.file),
            language=language
        )
        
        print(f"<- Transcription successful: '{transcription.text}'")
        return STTResponse(text=transcription.text)

    except Exception as e:
        print(f"An error occurred during transcription: {e}")
        raise HTTPException(status_code=500, detail="Failed to transcribe audio.")

@app.post("/text-to-speech")
async def tts_handler(request: TTSRequest):
    """
    Converts text to speech and returns the audio file.
    Implements simple caching to avoid re-generating the same audio.
    """
    print(f"-> Generating audio with voice: '{request.voice.value}'")
    try:
        hashed_filename = hashlib.md5(request.text.encode()).hexdigest()
        speech_file_path = f"static/audio/{hashed_filename}.mp3"

        # Check if the file already exists (our simple cache)
        if not os.path.exists(speech_file_path):
            print(f"-> Generating new audio file for: '{request.text[:30]}...'")
            response = openai.audio.speech.create(
                model="tts-1",
                voice=request.voice.value,
                input=request.text
            )
            response.stream_to_file(speech_file_path)
        else:
            print(f"-> Serving cached audio file for: '{request.text[:30]}...'")

        return FileResponse(path=speech_file_path, media_type="audio/mpeg")

    except Exception as e:
        print(f"An error occurred in TTS generation: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate audio.")

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