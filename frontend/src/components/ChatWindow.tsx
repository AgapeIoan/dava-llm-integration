import type { Message } from '../types';
import { Volume2, Image as ImageIcon, LoaderCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

interface ChatWindowProps {
  messages: Message[];
  onPlayAudio: (text: string, index: number) => void;
  playingIndex: number | null;
  onGenerateImage: (messageIndex: number) => void;
  onImageClick: (imageUrl: string) => void;
}

export const ChatWindow = ({ messages, onPlayAudio, playingIndex, onGenerateImage, onImageClick }: ChatWindowProps) => {
  return (
    <div className="chat-window">
      {messages.map((msg, index) => (
        <div key={index} className={`message-container ${msg.sender}`}>
          <div className="message-content">
            <div className="message-bubble">
              <div className="prose prose-sm max-w-none">
                <ReactMarkdown>
                  {msg.text}
                </ReactMarkdown>
              </div>

              {msg.sender === 'bot' && (
                <div className="message-actions">
                  <button className="action-btn" onClick={() => onPlayAudio(msg.text, index)} title="Play audio">
                    <Volume2 size={16} className={playingIndex === index ? 'text-blue-500' : ''} />
                  </button>
                  {msg.bookTitle && !msg.imageUrl && !msg.isImageLoading && (
                    <button className="action-btn" onClick={() => onGenerateImage(index)} title="Generate cover image">
                      <ImageIcon size={16} />
                    </button>
                  )}
                  {msg.isImageLoading && <LoaderCircle size={16} className="animate-spin" />}
                </div>
              )}
            </div>
            
            {msg.imageUrl && (
              <div className="message-image-container">
                <img 
                  src={msg.imageUrl} 
                  alt={`Cover for ${msg.bookTitle}`} 
                  className="message-image" 
                  onClick={() => onImageClick(msg.imageUrl!)}
                />
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};