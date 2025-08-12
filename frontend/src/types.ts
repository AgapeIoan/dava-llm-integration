// Tipul pentru un mesaj in UI-ul nostru
export type Message = {
  sender: 'user' | 'bot';
  text: string;
  bookTitle?: string;
  imageUrl?: string;
  isImageLoading?: boolean;
};

// Tipul pentru raspunsul de la endpoint-ul /chat/
export type ChatResponse = {
  response: string;
  book_title: string | null;
};

// Tipul pentru raspunsul de la endpoint-ul /audio/speech-to-text
export type STTResponse = {
  text: string;
};

// Tipul pentru raspunsul de la /image/generate
export type ImageGenerationResponse = {
  image_url: string;
  revised_prompt: string;
};