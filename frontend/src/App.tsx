import { useState, useRef } from 'react';
import type { Message } from './types';
import { ChatWindow } from './components/ChatWindow';
import { MessageInput } from './components/MessageInput';
import { streamChatMessage, fetchTtsAudio, generateImage } from './services/apiService';
import { transcribeAudio } from './services/apiService';
import { ImageModal } from './components/ImageModal';

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [playingIndex, setPlayingIndex] = useState<number | null>(null);
  const [modalImageUrl, setModalImageUrl] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const handleSendMessage = async (text: string) => {
    if (isLoading || text.trim() === '') return;

    const userMessage: Message = { sender: 'user', text };
    setMessages(prev => [...prev, userMessage, { sender: 'bot', text: '' }]);
    setIsLoading(true);

    const onChunk = (chunk: string) => {
      setMessages(prev => {
        const lastMessageIndex = prev.length - 1;
        const lastMessage = prev[lastMessageIndex];
        let updatedMessage = { ...lastMessage };

        // Verificam daca primim titlul cartii
        if (chunk.startsWith("TITLE::")) {
          const title = chunk.replace("TITLE::", "").trim();
          if (title) { // Adaugam titlul doar daca nu e gol
            updatedMessage.bookTitle = title;
          }
        } else {
          // Altfel, adaugam textul la mesaj
          updatedMessage.text += chunk;
        }
        
        // Cream un nou array si inlocuim ultimul mesaj
        const newMessages = [...prev];
        newMessages[lastMessageIndex] = updatedMessage;
        return newMessages;
      });
    };
    
    const onSuccess = () => {
        setIsLoading(false);
    };

    const onError = (error: Error) => {
        // Folosim variabila 'error' pentru a o afisa in consola
        console.error("Streaming error caught in UI:", error); 
        setMessages(prev => {
            const lastMessage = prev[prev.length - 1];
            const updatedMessage = { ...lastMessage, text: 'Oops! Something went wrong. Please try again later.' };
            const newMessages = [...prev];
            newMessages[prev.length-1] = updatedMessage
            return newMessages;
        });
        setIsLoading(false);
    };

    // Apelam un singur serviciu, cel de streaming
    await streamChatMessage(text, onChunk, onSuccess, onError);
  };

  const handleAudioStop = async (blobUrl: string) => {
    if (!blobUrl || isLoading) {
      console.log("Empty or invalid audio blob, or already loading.");
      return;
    }
    
    setIsLoading(true);
    console.log("Audio stopped. Transcribing...");

    try {
      const { text } = await transcribeAudio(blobUrl);
      console.log("Transcription result:", text);
      await handleSendMessage(text);
    } catch (error) {
      console.error("Error transcribing audio:", error);
      const errorMessage: Message = { 
        sender: 'bot', 
        text: 'Sorry, I had trouble understanding the audio. Please try again.' 
      };
      setMessages(prev => [...prev, errorMessage]);
      setIsLoading(false);
    }
  };

  const handlePlayAudio = async (text: string, index: number) => {
    if (audioRef.current) {
      audioRef.current.pause();
    }
    if (playingIndex === index) {
      setPlayingIndex(null);
      return;
    }
    try {
      setPlayingIndex(index);
      const audioBlob = await fetchTtsAudio(text);
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      audioRef.current = audio;
      audio.play();
      audio.onended = () => {
        setPlayingIndex(null);
      };
    } catch (error) {
      console.error("Failed to play audio:", error);
      setPlayingIndex(null);
    }
  };

  const handleImageClick = (imageUrl: string) => {
    setModalImageUrl(imageUrl);
  };
  const handleCloseModal = () => {
    setModalImageUrl(null);
  };

  const handleGenerateImage = async (messageIndex: number) => {
    const targetMessage = messages[messageIndex];
    if (!targetMessage || !targetMessage.bookTitle) return;

    setMessages(prevMessages => 
      prevMessages.map((msg, idx) => 
        idx === messageIndex ? { ...msg, isImageLoading: true } : msg
      )
    );
    try {
      const imageResponse = await generateImage(targetMessage.bookTitle, targetMessage.text);
      setMessages(prevMessages => 
        prevMessages.map((msg, idx) => 
          idx === messageIndex ? { ...msg, imageUrl: imageResponse.image_url, isImageLoading: false } : msg
        )
      );
    } catch (error) {
      console.error("Failed to generate image:", error);
      setMessages(prevMessages => 
        prevMessages.map((msg, idx) => 
          idx === messageIndex ? { ...msg, isImageLoading: false } : msg
        )
      );
    }
  };

  return (
    <main className="app-container">
      <div className="chat-container">
        <h1>Book Recommendation Chatbot</h1>
        <div className="chat-window-wrapper">
          <ChatWindow 
            messages={messages}
            onPlayAudio={handlePlayAudio}
            playingIndex={playingIndex}
            onGenerateImage={handleGenerateImage}
            onImageClick={handleImageClick}
          />
        </div>
        <MessageInput 
          onSendMessage={handleSendMessage} 
          onAudioStop={handleAudioStop}
          isLoading={isLoading}
        />
      </div>
      {modalImageUrl && <ImageModal imageUrl={modalImageUrl} onClose={handleCloseModal} />}
    </main>
  );
}

export default App;