import json
from fastapi import APIRouter, HTTPException

from api.models import ChatRequest, ChatResponse
from api.dependencies import collection, openai_client
from book_tools import get_summary_by_title

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/", response_model=ChatResponse)
async def chat_handler(request: ChatRequest):

    moderation_response = openai_client.moderations.create(input=request.prompt)
    if moderation_response.results[0].flagged:
        raise HTTPException(status_code=400, detail="Inappropriate content detected.")

    print(f"-> Received prompt: '{request.prompt}'")
    
    # RAG
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
    response = openai_client.chat.completions.create(model="gpt-4o-mini", messages=messages, tools=tools, tool_choice="auto")
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
    final_response = openai_client.chat.completions.create(model="gpt-4o-mini", messages=messages)
    final_content = final_response.choices[0].message.content
    
    return ChatResponse(response=final_content, book_title=book_title)