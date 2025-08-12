import type { ChatResponse, STTResponse, ImageGenerationResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export const postChatMessage = async (prompt: string): Promise<ChatResponse> => {
  const response = await fetch(`${API_BASE_URL}/chat/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      prompt: prompt,
      advanced_flow: true,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to get a response from the server.');
  }

  return response.json();
};

export const transcribeAudio = async (blobUrl: string): Promise<STTResponse> => {
  const audioBlob = await fetch(blobUrl).then(res => res.blob());

  const formData = new FormData();
  formData.append('file', audioBlob, 'audio.wav');

  const response = await fetch(`${API_BASE_URL}/audio/speech-to-text`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to transcribe audio.');
  }

  return response.json();
};

export const fetchTtsAudio = async (text: string): Promise<Blob> => {
  const response = await fetch(`${API_BASE_URL}/audio/text-to-speech`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      text: text,
      voice: 'shimmer', 
    }),
  });

  if (!response.ok) {
    throw new Error('Failed to fetch TTS audio.');
  }

  return response.blob();
};

export const generateImage = async (book_title: string, book_summary: string): Promise<ImageGenerationResponse> => {
  const response = await fetch(`${API_BASE_URL}/image/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      book_title: book_title,
      book_summary: book_summary,
    }),
  });

  if (!response.ok) {
    throw new Error('Failed to generate image.');
  }

  return response.json();
};

export const streamChatMessage = async (
  prompt: string,
  onChunkReceived: (chunk: string) => void,
  onSuccess: () => void,
  onError: (error: Error) => void
) => {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt, advanced_flow: true }),
    });

    if (!response.body) {
      throw new Error('Response body is null.');
    }
    if (!response.ok) {
        throw new Error(`Server error: ${response.statusText}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { value, done } = await reader.read();
      if (done) {
        onSuccess(); // Notificam ca stream-ul s-a incheiat
        break;
      }
      const chunk = decoder.decode(value);
      onChunkReceived(chunk); // Trimitem fiecare bucata catre UI
    }
  } catch (error) {
    console.error("Streaming failed:", error);
    onError(error as Error);
  }
};