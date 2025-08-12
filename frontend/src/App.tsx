import { useState, useRef } from 'react';
import type { Message } from './types';
import { ChatWindow } from './components/ChatWindow';
import { MessageInput } from './components/MessageInput';
import { postChatMessage, transcribeAudio, fetchTtsAudio } from './services/apiService';
import { generateImage } from './services/apiService';
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
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const chatResponse = await postChatMessage(text);
      const botMessage: Message = { 
        sender: 'bot', 
        text: chatResponse.response,
        bookTitle: chatResponse.book_title || undefined
      };      
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error("Error sending message:", error);
      const errorMessage: Message = { 
        sender: 'bot', 
        text: 'Oops! Something went wrong. Please try again later.' 
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
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