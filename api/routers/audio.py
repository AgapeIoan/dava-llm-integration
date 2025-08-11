import hashlib
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse

from api.models import TTSRequest, STTResponse

from api.dependencies import openai_client

router = APIRouter(
    prefix="/audio",
    tags=["Audio Processing"]
)

@router.post("/text-to-speech")
async def tts_handler(request: TTSRequest):
    """
    Converts text to speech using a specified voice.
    Implements simple caching to avoid re-generating the same audio.
    """
    print(f"-> Generating audio with voice: '{request.voice.value}'")
    try:
        cache_key = request.text + request.voice.value
        hashed_filename = hashlib.md5(cache_key.encode()).hexdigest()
        speech_file_path = f"static/audio/{hashed_filename}.mp3"

        if not speech_file_path.exists():
            response = openai_client.audio.speech.create(
                model="tts-1",
                voice=request.voice.value,
                input=request.text
            )
            response.stream_to_file(speech_file_path)
        else:
            print(f"-> Serving cached audio file for voice '{request.voice.value}'.")

        return FileResponse(path=speech_file_path, media_type="audio/mpeg")

    except Exception as e:
        print(f"An error occurred in TTS generation: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate audio.")


@router.post("/speech-to-text", response_model=STTResponse)
async def stt_handler(
    file: UploadFile = File(...),
    language: str = Form("en")
):
    """
    Accepts an audio file and an optional language code, then transcribes it to text.
    """
    print(f"-> Received audio file for transcription in language: '{language}'")
    try:
        transcription = openai_client.audio.transcriptions.create(
            model="whisper-1",
            file=(file.filename, file.file),
            language=language
        )
        
        print(f"<- Transcription successful: '{transcription.text}'")
        return STTResponse(text=transcription.text)

    except Exception as e:
        print(f"An error occurred during transcription: {e}")
        if "is not a valid ISO-639-1" in str(e):
             raise HTTPException(status_code=400, detail=f"Invalid language code '{language}'.")
        raise HTTPException(status_code=500, detail="Failed to transcribe audio.")