// Tipul pentru un mesaj in UI-ul nostru
export type Message = {
  sender: 'user' | 'bot';
  text: string;
};

// Tipul pentru raspunsul de la endpoint-ul /chat/
export type ChatResponse = {
  response: string;
  book_title: string | null;
};