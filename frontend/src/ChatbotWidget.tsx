import { useState, useRef, useEffect } from 'react';
import { MessageCircle, X, Send, Bot } from 'lucide-react';
import './ChatbotWidget.css';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

// Use environment variable for the backend URL when deployed on Vercel
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001/api/chat';

export default function ChatbotWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      text: 'Hi! I am your AI Expense Tracker Assistant. Ask me about your highest spend, top categories, or total expenses!',
      sender: 'bot',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  
  // Replace this with the active user ID from your auth system in LEDGER_AI
  const userId = "8db8b2ef-1ccb-49aa-8321-599f69d140b2";

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const toggleChat = () => setIsOpen(!isOpen);

  const sendMessage = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim()) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      text: input,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setIsTyping(true);

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: userMsg.text,
          user_id: userId,
        }),
      });

      const data = await response.json();

      const botMsg: Message = {
        id: (Date.now() + 1).toString(),
        text: data.response || "Sorry, I couldn't process that.",
        sender: 'bot',
        timestamp: new Date(),
      };
      
      setMessages((prev) => [...prev, botMsg]);
    } catch (error) {
      console.error("Chatbot API Error:", error);
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        text: "Error connecting to the chatbot server. Is the backend running?",
        sender: 'bot',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="chatbot-wrapper">
      {/* Floating Action Button */}
      <button 
        className={`chatbot-fab ${isOpen ? 'open' : ''}`}
        onClick={toggleChat}
      >
        {isOpen ? <X size={24} /> : <MessageCircle size={28} />}
      </button>

      {/* Chat Window */}
      <div className={`chatbot-window ${isOpen ? 'active' : ''}`}>
        <div className="chatbot-header">
          <div className="chatbot-header-info">
            <div className="bot-avatar">
              <Bot size={20} />
            </div>
            <div>
              <h3>AI Assistant</h3>
              <span className="online-status">Online</span>
            </div>
          </div>
          <button className="close-btn" onClick={toggleChat}>
            <X size={20} />
          </button>
        </div>

        <div className="chatbot-body">
          {messages.map((msg) => (
            <div 
              key={msg.id} 
              className={`chat-bubble-container ${msg.sender === 'user' ? 'user' : 'bot'}`}
            >
              {msg.sender === 'bot' && (
                <div className="chat-avatar bot-bubble-avatar"><Bot size={14} /></div>
              )}
              <div className={`chat-bubble ${msg.sender === 'user' ? 'user' : 'bot'}`}>
                {/* Parse line breaks safely */}
                {msg.text.split('\n').map((str, idx) => (
                  <span key={idx}>
                    {str}
                    <br />
                  </span>
                ))}
                <span className="msg-timestamp">
                  {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
            </div>
          ))}

          {isTyping && (
            <div className="chat-bubble-container bot">
              <div className="chat-avatar bot-bubble-avatar"><Bot size={14} /></div>
              <div className="chat-bubble bot typing-indicator">
                <span></span><span></span><span></span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="chatbot-footer">
          <form onSubmit={sendMessage} className="chat-input-form">
            <input
              type="text"
              placeholder="Ask about your expenses..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
            />
            <button 
              type="submit" 
              className="send-btn"
              disabled={!input.trim() || isTyping}
            >
              <Send size={18} />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
