import { useState } from 'react';
import type { Message } from './types';
import { postChatMessage } from './services/apiService';

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentInput, setCurrentInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async () => {
    if (currentInput.trim() === '' || isLoading) return;

    const userMessage: Message = { sender: 'user', text: currentInput };
    setMessages(prev => [...prev, userMessage]);
    setCurrentInput('');
    setIsLoading(true);

    try {
      const chatResponse = await postChatMessage(userMessage.text);
      const botMessage: Message = { sender: 'bot', text: chatResponse.response };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error(error);
      const errorMessage: Message = { 
        sender: 'bot', 
        text: 'Oops! Something went wrong. Please try again later.' 
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-window">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.sender}`}>
            <p>{msg.text}</p>
          </div>
        ))}
      </div>
      <div className="chat-input-area">
        <input
          type="text"
          value={currentInput}
          onChange={(e) => setCurrentInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
          placeholder={isLoading ? 'The bot is thinking...' : 'Ask for a book recommendation...'}
          disabled={isLoading}
        />
        <button onClick={handleSendMessage} disabled={isLoading}>
          {isLoading ? '...' : 'Send'} {/* <-- Schimba textul/starea butonului */}
        </button>
      </div>
    </div>
  );
}

export default App;