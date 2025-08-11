from pydantic import BaseModel
from enum import Enum

# Chat Models
class ChatRequest(BaseModel):
    prompt: str
    advanced_flow: bool = True

class ChatResponse(BaseModel):
    response: str
    book_title: str | None = None

# TTS Models
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

# STT Models
class STTResponse(BaseModel):
    text: str

# Image Generation Models
class ImageGenerationRequest(BaseModel):
    book_title: str
    book_summary: str

class ImageGenerationResponse(BaseModel):
    image_url: str
    revised_prompt: str