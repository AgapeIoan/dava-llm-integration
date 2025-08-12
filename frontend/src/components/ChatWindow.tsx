import type { Message } from '../types';

interface ChatWindowProps {
  messages: Message[];
  onPlayAudio: (text: string, index: number) => void;
  playingIndex: number | null;
  onGenerateImage: (messageIndex: number) => void;
}

export const ChatWindow = ({ messages, onPlayAudio, playingIndex, onGenerateImage }: ChatWindowProps) => {
  return (
    <div className="chat-window">
      {messages.map((msg, index) => (
        <div 
          key={index} 
          className={`message ${msg.sender} ${playingIndex === index ? 'playing' : ''}`}
        >
          <p>{msg.text}</p>
          {msg.sender === 'bot' && msg.bookTitle && (
            <div className="book-actions">
              {!msg.isImageLoading && !msg.imageUrl && (
                <button className="generate-image-btn" onClick={() => onGenerateImage(index)}>
                  Generate Cover
                </button>
              )}
              {msg.isImageLoading && <div className="spinner"></div>}
              {msg.imageUrl && <img src={msg.imageUrl} alt={`Cover for ${msg.bookTitle}`} className="book-cover" />}
            </div>
          )}
          {msg.sender === 'bot' && (
            <button className="play-audio-btn" onClick={() => onPlayAudio(msg.text, index)}>
              🔊
            </button>
          )}
        </div>
      ))}
    </div>
  );
};