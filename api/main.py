import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from .routers import chat, audio, image

# Load environment variables before anything else
load_dotenv()


app = FastAPI(
    title="Book Recommender API",
    description="An API for recommending books using RAG, multimodal features, and OpenAI."
)

# Mount static files
os.makedirs("static/audio", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include the routers
app.include_router(chat.router)
app.include_router(audio.router)
app.include_router(image.router)

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Book Recommender API!"}