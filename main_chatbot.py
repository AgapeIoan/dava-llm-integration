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

def get_book_recommendation(user_prompt: str, advanced_flow: bool = True):
    """
    Handles the book recommendation flow with a choice between two strategies.

    Args:
        user_prompt (str): The user's input.
        advanced_flow (bool): If True, uses the 2-call flow for a more conversational response.
                              If False, uses the 1-call optimized flow.
    """

    print("-> Retrieving relevant context from the database...")
    results = collection.query(query_texts=[user_prompt], n_results=3)
    context = "\n\n".join(results['documents'][0])

    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_summary_by_title",
                "description": "Get the detailed summary of a specific book by its exact title.",
                "parameters": {
                    "type": "object",
                    "properties": {"title": {"type": "string", "description": "The exact title of the book."}},
                    "required": ["title"],
                },
            },
        }
    ]

    if advanced_flow:
        print("-> Using ADVANCED flow (2 API calls) for a conversational response.")
        system_prompt = f"""
You are a helpful and friendly book recommendation chatbot. Your primary goal is to perform two steps:
1. Based on the user's request and the provided context, you must first recommend ONE single book that is the best match. Keep the recommendation response concise and conversational.
2. After making the recommendation, you MUST call the `get_summary_by_title` tool to provide the user with a detailed summary of that book.
Only recommend books found in the following context.
---
CONTEXT:
{context}
---
"""
        tool_choice = "auto"
    else:
        print("-> Using SIMPLE flow (1 API call) for an optimized response.")
        system_prompt = f"""
You are a book-finding engine. Your only task is to analyze the user's request and the provided book summaries (context) to find the single best book match.
Once you have identified the best matching book, you MUST call the `get_summary_by_title` function with the exact title of that book.
Do not respond with any conversational text. Your only output should be a function call.
CONTEXT:
---
{context}
---
"""
        tool_choice = {"type": "function", "function": {"name": "get_summary_by_title"}}

    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
    
    print("-> Sending request to LLM...")
    response = openai.chat.completions.create(
        model=LLM_MODEL, messages=messages, tools=tools, tool_choice=tool_choice
    )
    response_message = response.choices[0].message
    messages.append(response_message)

    tool_calls = response_message.tool_calls
    if not tool_calls:
        # If the model didn't call a tool (e.g., for a greeting or if it can't find a match)
        print("\n--- Chatbot Response ---")
        print(response_message.content or "I'm sorry, I couldn't find a suitable book based on your request. Please try rephrasing.")
        return

    tool_call = tool_calls[0]
    function_name = tool_call.function.name
    if function_name != "get_summary_by_title":
        print(f"Error: An unexpected tool was called: {function_name}")
        return
        
    function_args = json.loads(tool_call.function.arguments)
    book_title = function_args.get("title")
    summary = get_summary_by_title(title=book_title)

    # Final Response Generation
    if advanced_flow:
        print("-> Sending tool output back to LLM for the final response...")
        messages.append({"tool_call_id": tool_call.id, "role": "tool", "name": function_name, "content": summary})
        final_response = openai.chat.completions.create(model=LLM_MODEL, messages=messages)
        final_content = final_response.choices[0].message.content
    else:
        final_content = (
            f"Based on your request, I recommend the book: **{book_title}**!\n\n"
            f"Here is a detailed summary for you:\n"
            f"{summary}"
        )
    
    print("\n--- Chatbot Recommendation ---")
    print(final_content.strip())

if __name__ == "__main__":
    print("Welcome to the Book Recommendation Chatbot!")
    print("Ask me for a book recommendation based on your interests. Type 'exit' to quit.")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
        
        get_book_recommendation(user_input)
