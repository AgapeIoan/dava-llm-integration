import type { ChatResponse } from '../types';

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