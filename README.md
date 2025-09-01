# AI Book Recommendation Chatbot

This project is a full-stack, multimodal AI chatbot that provides personalized book recommendations. Built with a Python/FastAPI backend and a React frontend, it leverages OpenAI's models to deliver an intelligent and interactive user experience.

The core of the application is a RAG (Retrieval-Augmented Generation) pipeline that uses a local **ChromaDB** vector store to ground its recommendations in a defined knowledge base. The chatbot is enhanced with multimodal capabilities, including voice commands (Speech-to-Text), audio responses (Text-to-Speech), and AI-powered image generation for book cover concepts.

## ✨ Features

-   **Conversational Recommendations:** Ask for books based on themes, genres, or abstract ideas.
-   **RAG Pipeline:** Utilizes a local **ChromaDB** vector store for semantic search.
-   **Detailed Summaries via Tool Calling:** Employs OpenAI's Tool Calling feature for complex, agent-like behavior.
-   **Multimodal Capabilities:**
    -   🗣️ **Speech-to-Text (STT):** Transcribes user voice commands.
    -   🔊 **Text-to-Speech (TTS):** Converts bot responses to audio.
    -   🖼️ **Image Generation:** Creates unique cover concepts with DALL-E 3.
-   **Robust AI Safety & Security:** Implements content moderation for both user input and AI-generated output.
-   **Advanced Prompt Engineering:** A sophisticated system prompt provides a clear persona, strict operational rules, and defenses against common adversarial attacks.
-   **Modern Tech Stack:** Built with a FastAPI backend and a React (Vite + TypeScript) frontend, fully containerized with Docker.

## 🏛️ Project Architecture

The application follows a modern client-server architecture with a clear separation of concerns, as illustrated below.

![System Architecture Diagram](https://img.agapeioan.ro/github/llmintegrationdava_system_architecture.drawio.png)

-   **Frontend:** A responsive web interface built with **React** and TypeScript. **(Currently a work in progress)**.
-   **Backend:** A powerful and scalable API built with **FastAPI** that orchestrates all AI logic.
-   **AI Core:**
    -   **OpenAI API:** Leverages `gpt-4o-mini`, `text-embedding-3-small`, `tts-1`, `whisper-1`, and `dall-e-3`.
    -   **Vector Store:** Uses **ChromaDB** for efficient semantic search.
-   **Containerization:** The entire application is containerized using **Docker** and orchestrated with **Docker Compose**.

---

## 🚀 Getting Started

### Prerequisites

-   An **OpenAI API Key**.
-   **Python** 3.10+
-   **Node.js** 20.x+
-   **Docker** and **Docker Compose**

### Setup Steps

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/AgapeIoan/dava-llm-integration.git
    cd dava-llm-integration
    ```

2.  **Create the environment file:**
    Create a file named `.env` in the root directory and add your OpenAI API key:
    ```
    OPENAI_API_KEY="sk-..."
    VITE_API_BASE_URL=http://backend:8000
    ```

3.  **Populate the vector database:**
    This one-time setup step is required to create the local ChromaDB database.
    ```bash
    # Set up a Python virtual environment
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate

    # Install dependencies and run the setup script
    pip install -r requirements.txt
    python setup_vectordb.py
    ```

4.  **(Important) Install Frontend Dependencies:**
    The Docker build process requires the `package-lock.json` file to be present.
    ```bash
    cd frontend
    npm install
    cd ..
    ```

5.  **Build and run the containers:**
    ```bash
    docker-compose up --build
    ```

---

## 🧪 API Testing (Swagger UI)

While the frontend is under development, the backend API is fully functional and can be tested directly via its interactive documentation.

1.  **Ensure the Docker containers are running.**
2.  **Access the API documentation:**
    Open your browser and navigate to `http://localhost:8000/docs`.

You will find a complete list of all available endpoints (`/chat`, `/audio/text-to-speech`, etc.) with detailed information on how to use them.

### Example API Calls:

-   **`/chat` endpoint:**
    ```json
    {
      "prompt": "a book about war and society",
      "advanced_flow": true
    }
    ```
-   **`/audio/text-to-speech` endpoint:**
    ```json
    {
      "text": "Hello, this is a test.",
      "voice": "nova"
    }
    ```
-   **`/audio/speech-to-text` endpoint:**
    Use the interface to upload an audio file (`.mp3`, `.m4a`, etc.).

-   **`/image/generate` endpoint:**
    ```json
    {
      "book_title": "Dune",
      "book_summary": "A science fiction novel set in the distant future amidst a feudal interstellar society..."
    }
    ```

### Accessing the Frontend

The React frontend is a work in progress. Once the containers are running, you can view the current state of the UI at: `http://localhost:5173`.
