from fastapi import APIRouter, HTTPException

from ..models import ImageGenerationRequest, ImageGenerationResponse

from ..dependencies import openai_client

router = APIRouter(
    prefix="/image",
    tags=["Image Generation"]
)

@router.post("/generate", response_model=ImageGenerationResponse)
async def image_generation_handler(request: ImageGenerationRequest):
    """
    Generates an image based on a book title and summary using DALL-E 3.
    """
    print(f"-> Received request to generate image for: '{request.book_title}'")
    
    dalle_prompt = (
        f"Create a highly detailed, evocative, and artistic book cover concept for a book titled '{request.book_title}'. "
        f"The story is about: '{request.book_summary}'. "
        "The style should be a digital painting, capturing the main themes of the story. "
        "Do NOT include any text, letters, or words on the image."
    )

    try:
        response = openai_client.images.generate(
            model="dall-e-3",
            prompt=dalle_prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )

        image_url = response.data[0].url
        revised_prompt = response.data[0].revised_prompt
        
        print(f"<- Image generated successfully. URL: {image_url}")
        return ImageGenerationResponse(image_url=image_url, revised_prompt=revised_prompt)

    except Exception as e:
        print(f"An error occurred during image generation: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate image.")