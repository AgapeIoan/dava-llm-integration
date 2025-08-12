import json
import re

from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from api.models import ChatRequest
from api.dependencies import collection, openai_client
from book_tools import get_summary_by_title

router = APIRouter(prefix="/chat", tags=["Chat"])

try:
    PROMPT_TEMPLATE_PATH = Path(__file__).resolve().parents[2] / "prompt.txt"
    with open(PROMPT_TEMPLATE_PATH, "r", encoding="utf-8") as f:
        PROMPT_TEMPLATE = f.read()
    print("Prompt template loaded successfully.")
except FileNotFoundError:
    print("ERROR: prompt.txt not found. Please create it in the project root.")
    PROMPT_TEMPLATE = "You are a helpful assistant. Context: {context}" # Un fallback simplu

async def stream_and_moderate_generator(book_title, messages):
    """
    Genereaza raspunsul final in mod streaming, cu moderare.
    """
    if book_title:
        yield f"TITLE::{book_title}\n"

    sentence_buffer = ""
    WORD_COUNT_THRESHOLD = 10
    
    stream = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        stream=True
    )

    try:
        for chunk in stream:
            content = chunk.choices[0].delta.content or ""
            sentence_buffer += content

            parts = re.split(r'([.!?])', sentence_buffer)
            word_count = len(sentence_buffer.split())

            if len(parts) > 2 or word_count > WORD_COUNT_THRESHOLD:
                sentence_to_check = "".join(parts[:-1]) if len(parts) > 2 else sentence_buffer
                sentence_buffer = parts[-1] if len(parts) > 2 else ""

                if not sentence_to_check.strip(): continue

                moderation_response = openai_client.moderations.create(input=sentence_to_check)
                if moderation_response.results[0].flagged:
                    print(f"<- OUTPUT FLAGGED: '{sentence_to_check}'")
                    yield "I am unable to provide a response that complies with safety guidelines. Please try a different topic."
                    return

                yield sentence_to_check

        if sentence_buffer.strip():
            moderation_response = openai_client.moderations.create(input=sentence_buffer)
            if moderation_response.results[0].flagged:
                print(f"<- FINAL BUFFER FLAGGED: '{sentence_buffer}'")
                yield "I am unable to provide a response that complies with safety guidelines. Please try a different topic."
            else:
                yield sentence_buffer
    except Exception as e:
        print(f"An error occurred during streaming: {e}")
        yield "An unexpected error occurred. Please try again."


@router.post("/")
async def chat_handler(request: ChatRequest):
    """
    Orchestreaza intregul flux de chat: moderare input, RAG, tool calling, si streaming cu moderare output.
    """
    # Moderarea Input-ului
    moderation_response = openai_client.moderations.create(input=request.prompt)
    if moderation_response.results[0].flagged:
        raise HTTPException(status_code=400, detail="Inappropriate content detected in user input.")

    print(f"-> Received prompt for streaming: '{request.prompt}'")
    
    # Retrieval (RAG)
    results = collection.query(query_texts=[request.prompt], n_results=3)
    context = "\n\n".join(results['documents'][0])
    
    # Augmentation
    system_prompt = PROMPT_TEMPLATE.format(context=context)
    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": request.prompt}]
    tools = [{"type": "function", "function": {"name": "get_summary_by_title", "description": "Get a book's summary by title.", "parameters": {"type": "object", "properties": {"title": {"type": "string"}}, "required": ["title"]}}}]

    # Primul Apel LLM (pentru a alege cartea)
    response = openai_client.chat.completions.create(model="gpt-4o-mini", messages=messages, tools=tools, tool_choice="auto")
    response_message = response.choices[0].message
    messages.append(response_message)
    
    # Gestionarea Cazului fara Tool Call
    tool_calls = response_message.tool_calls
    if not tool_calls:
        async def no_tool_stream():
            yield response_message.content or "I couldn't find a suitable recommendation. Please rephrase your request."
        return StreamingResponse(no_tool_stream(), media_type="text/event-stream")

    # Executia Tool-ului
    tool_call = tool_calls[0]
    function_args = json.loads(tool_call.function.arguments)
    book_title = function_args.get("title")
    summary = get_summary_by_title(title=book_title)

    # Adaugam rezultatul tool-ului la istoria conversatiei
    messages.append({"tool_call_id": tool_call.id, "role": "tool", "name": "get_summary_by_title", "content": summary})
    priming_instruction = {
        "role": "system",
        "content": "You have successfully retrieved the book summary. Now, present your complete response to the user. Start with a warm, friendly, and conversational sentence to introduce your recommendation, as instructed in your persona. Then, seamlessly integrate the detailed summary you retrieved. Conclude with a friendly closing remark."
    }
    messages.append(priming_instruction)
    # Returnam Raspunsul Final prin Streaming cu Moderare
    return StreamingResponse(stream_and_moderate_generator(book_title, messages), media_type="text/event-stream")