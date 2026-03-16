import React, { useState, useEffect, useRef } from 'react';
import { conversationsAPI } from '../../services/api';
import ReactMarkdown from 'react-markdown';
import { FiSend, FiPlus, FiTrash2, FiMessageSquare, FiCpu } from 'react-icons/fi';
import './Chatbot.css';

export default function Chatbot() {
  const [conversations, setConversations] = useState([]);
  const [activeConv, setActiveConv] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    fetchConversations();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const fetchConversations = async () => {
    try {
      const { data } = await conversationsAPI.list();
      setConversations(data.results || data || []);
    } catch (err) {
      console.error('Fetch conversations error:', err);
    }
  };

  const selectConversation = async (conv) => {
    setActiveConv(conv);
    try {
      const { data } = await conversationsAPI.get(conv.id);
      setMessages(data.messages || []);
    } catch (err) {
      console.error('Fetch messages error:', err);
    }
  };

  const createNewConversation = async () => {
    try {
      const { data } = await conversationsAPI.create({ title: 'Nouvelle conversation' });
      setConversations([data, ...conversations]);
      setActiveConv(data);
      setMessages([]);
    } catch (err) {
      console.error('Create conversation error:', err);
    }
  };

  const deleteConversation = async (e, convId) => {
    e.stopPropagation();
    try {
      await conversationsAPI.delete(convId);
      setConversations(conversations.filter((c) => c.id !== convId));
      if (activeConv?.id === convId) {
        setActiveConv(null);
        setMessages([]);
      }
    } catch (err) {
      console.error('Delete conversation error:', err);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || sending) return;

    let conv = activeConv;
    if (!conv) {
      try {
        const { data } = await conversationsAPI.create({ title: input.slice(0, 50) });
        conv = data;
        setActiveConv(data);
        setConversations([data, ...conversations]);
      } catch (err) {
        console.error('Auto-create conversation error:', err);
        return;
      }
    }

    const userMsg = { id: Date.now(), sender: 'user', content: input, timestamp: new Date().toISOString() };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setSending(true);

    try {
      const { data } = await conversationsAPI.sendMessage(conv.id, input);
      setMessages((prev) => [
        ...prev.filter((m) => m.id !== userMsg.id),
        data.user_message,
        data.assistant_message,
      ]);
      fetchConversations(); // refresh titles
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { id: Date.now() + 1, sender: 'assistant', content: "Désolé, une erreur s'est produite. Réessayez.", timestamp: new Date().toISOString() },
      ]);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="chatbot-page">
      {/* Conversation Sidebar */}
      <div className="chat-sidebar">
        <button className="btn btn-primary btn-full" onClick={createNewConversation}>
          <FiPlus /> Nouvelle conversation
        </button>
        <div className="conversation-list">
          {conversations.map((conv) => (
            <div
              key={conv.id}
              className={`conversation-item ${activeConv?.id === conv.id ? 'active' : ''}`}
              onClick={() => selectConversation(conv)}
            >
              <FiMessageSquare />
              <span className="conv-title">{conv.title}</span>
              <button
                className="conv-delete"
                onClick={(e) => deleteConversation(e, conv.id)}
              >
                <FiTrash2 />
              </button>
            </div>
          ))}
          {conversations.length === 0 && (
            <p className="no-conversations">Aucune conversation</p>
          )}
        </div>
      </div>

      {/* Chat Area */}
      <div className="chat-main">
        {messages.length === 0 && !activeConv ? (
          <div className="chat-welcome">
            <FiCpu className="welcome-icon" />
            <h2>Assistant Smart PFE</h2>
            <p>Discutez avec l'IA pour trouver votre projet de PFE idéal</p>
            <div className="welcome-suggestions">
              {[
                "Je cherche un PFE en intelligence artificielle",
                "Quels projets web sont populaires ?",
                "Suggestions pour un stage en cybersécurité",
                "J'ai des compétences en Python et React",
              ].map((suggestion, i) => (
                <button
                  key={i}
                  className="suggestion-chip"
                  onClick={() => { setInput(suggestion); }}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="chat-messages">
            {messages.map((msg, i) => (
              <div key={msg.id || i} className={`message ${msg.sender}`}>
                <div className="message-avatar">
                  {msg.sender === 'user' ? '👤' : '🤖'}
                </div>
                <div className="message-content">
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                </div>
              </div>
            ))}
            {sending && (
              <div className="message assistant">
                <div className="message-avatar">🤖</div>
                <div className="message-content typing">
                  <span className="dot"></span>
                  <span className="dot"></span>
                  <span className="dot"></span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}

        {/* Input */}
        <form className="chat-input-form" onSubmit={sendMessage}>
          <input
            type="text"
            className="chat-input"
            placeholder="Décrivez votre projet idéal..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={sending}
          />
          <button type="submit" className="btn btn-primary btn-icon" disabled={!input.trim() || sending}>
            <FiSend />
          </button>
        </form>
      </div>
    </div>
  );
}
