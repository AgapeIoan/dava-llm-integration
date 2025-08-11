import chromadb
import os
import openai
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Constants
SOURCE_FILE = "book_summaries.md"
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "book_summaries"
EMBEDDING_MODEL = "text-embedding-3-small"

def parse_summaries(file_path):
    """
    Parses a markdown file with '## Title:' delimiters to extract book titles and summaries.
    Returns a list of dictionaries, where each dictionary represents a book.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return []

    books = []
    # Split the content by the title marker
    sections = content.split('## Title:')
    for section in sections:
        if section.strip():
            # The first line is the title, the rest is the summary
            parts = section.strip().split('\n', 1)
            title = parts[0].strip()
            summary = parts[1].strip() if len(parts) > 1 else ""
            books.append({"title": title, "summary": summary})
    return books

def main():
    """
    Main function to set up the ChromaDB vector store.
    It parses the source file and loads the data into a persistent Chroma collection.
    """
    print("--- Starting Vector DB Setup ---")

    books = parse_summaries(SOURCE_FILE)
    if not books:
        print("No books found to process. Exiting.")
        return

    print(f"Found {len(books)} books in '{SOURCE_FILE}'.")

    client = chromadb.PersistentClient(path=CHROMA_PATH)

    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=os.getenv("OPENAI_API_KEY"),
        model_name=EMBEDDING_MODEL
    )

    print(f"Loading or creating collection: '{COLLECTION_NAME}' with model '{EMBEDDING_MODEL}'")
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=openai_ef
    )

    documents = [book['summary'] for book in books]
    metadatas = [{'title': book['title']} for book in books]
    ids = [f"book_{i}_{book['title'].replace(' ', '_').lower()}" for i, book in enumerate(books)]

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )

    print(f"Successfully loaded {collection.count()} documents into the collection.")
    print("--- Vector DB Setup Complete ---")


if __name__ == "__main__":
    main()