import { useState } from 'react';

type Message = {
  sender: 'user' | 'bot';
  text: string;
};

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  
  const [currentInput, setCurrentInput] = useState('');

  const handleSendMessage = () => {
    if (currentInput.trim() === '') return;

    const userMessage: Message = { sender: 'user', text: currentInput };
    setMessages([...messages, userMessage]);

    // TODO: Aici vom adauga logica pentru a apela backend-ul
    // Pentru moment, simulam un raspuns de la bot
    setTimeout(() => {
      const botResponse: Message = { sender: 'bot', text: "This is a placeholder response." };
      setMessages(prevMessages => [...prevMessages, botResponse]);
    }, 1000); // Asteptam 1 secunda pentru a simula un delay

    setCurrentInput('');
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
          placeholder="Ask for a book recommendation..."
        />
        <button onClick={handleSendMessage}>Send</button>
      </div>
    </div>
  );
}

export default App;