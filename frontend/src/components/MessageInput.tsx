import { useState } from 'react';
import { useReactMediaRecorder } from 'react-media-recorder';
import { Mic, Send } from 'lucide-react';
interface MessageInputProps {
  onSendMessage: (message: string) => void;
  onAudioStop: (audioUrl: string) => void;
  isLoading: boolean;
}

const AudioRecorder = ({ onStop, onStart }: { onStop: (audioUrl: string) => void, onStart: () => void }) => {
    const [isRecording, setIsRecording] = useState(false);
    
    // Extragem start/stop din hook
    const { startRecording, stopRecording } = useReactMediaRecorder({ 
        audio: true,
        onStop: (blobUrl) => {
            onStop(blobUrl);
            setIsRecording(false); // Oprim starea de inregistrare in UI
        }
    });

    const handleMicClick = () => {
        if (isRecording) {
            stopRecording();
        } else {
            onStart(); // Notificam parintele ca a inceput inregistrarea
            startRecording();
            setIsRecording(true);
        }
    };

    return (
        <button 
            className={`mic-button ${isRecording ? 'recording' : ''}`}
            onClick={handleMicClick}
        >
          <Mic size={18} />
        </button>
    );
};


export const MessageInput = ({ onSendMessage, onAudioStop, isLoading }: MessageInputProps) => {
  const [currentInput, setCurrentInput] = useState('');

  const handleSendClick = () => {
    if (currentInput.trim() === '') return;
    onSendMessage(currentInput);
    setCurrentInput(''); // Golim input-ul aici
  };

  const handleAudioStart = () => {
      setCurrentInput('');
  }

  return (
    <div className="chat-input-area">
      <AudioRecorder onStop={onAudioStop} onStart={handleAudioStart} />
      <input
        type="text"
        value={currentInput}
        onChange={(e) => setCurrentInput(e.target.value)}
        onKeyPress={(e) => e.key === 'Enter' && handleSendClick()}
        placeholder={isLoading ? 'The bot is thinking...' : 'Ask for a book recommendation...'}
        disabled={isLoading}
      />
      <button onClick={handleSendClick} disabled={isLoading}>
        {isLoading ? '...' : <Send size={18} />}
      </button>
    </div>
  );
};