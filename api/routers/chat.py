import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse 

from api.models import ChatRequest
from api.dependencies import collection, openai_client
from book_tools import get_summary_by_title

router = APIRouter(prefix="/chat", tags=["Chat"])

async def stream_generator(book_title, messages):
    """
    Genereaza raspunsul final in mod streaming.
    Trimite mai intai titlul cartii, apoi continutul de la LLM.
    """
    # Trimitem titlul cartii cu un prefix special
    if book_title:
        yield f"TITLE::{book_title}\n"

    # Facem al doilea apel la LLM in mod streaming
    stream = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        stream=True
    )
    # Iteram prin fiecare bucata de text si o trimitem catre client
    for chunk in stream:
        content = chunk.choices[0].delta.content or ""
        yield content


@router.post("/")
async def chat_handler(request: ChatRequest):
    # Moderation
    moderation_response = openai_client.moderations.create(input=request.prompt)
    if moderation_response.results[0].flagged:
        raise HTTPException(status_code=400, detail="Inappropriate content detected.")

    print(f"-> Received prompt for streaming: '{request.prompt}'")
    
    # RAG
    results = collection.query(query_texts=[request.prompt], n_results=3)
    context = "\n\n".join(results['documents'][0])
    
    # Folosim prompt-ul prietenos
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

    # First LLM Call (pentru a alege cartea si a apela tool-ul)
    response = openai_client.chat.completions.create(model="gpt-4o-mini", messages=messages, tools=tools, tool_choice="auto")
    response_message = response.choices[0].message
    messages.append(response_message)
    
    tool_calls = response_message.tool_calls
    if not tool_calls:
        # Daca nu exista tool call, returnam un raspuns simplu in mod streaming
        async def no_tool_stream():
            yield response_message.content or "I couldn't find a suitable recommendation. Please rephrase your request."
        return StreamingResponse(no_tool_stream(), media_type="text/event-stream")

    # Tool Execution
    tool_call = tool_calls[0]
    function_args = json.loads(tool_call.function.arguments)
    book_title = function_args.get("title")
    summary = get_summary_by_title(title=book_title)

    # Adaugam rezultatul tool-ului la istoria conversatiei
    messages.append({"tool_call_id": tool_call.id, "role": "tool", "name": "get_summary_by_title", "content": summary})
    
    # Returnam StreamingResponse care foloseste generatorul nostru
    return StreamingResponse(stream_generator(book_title, messages), media_type="text/event-stream")