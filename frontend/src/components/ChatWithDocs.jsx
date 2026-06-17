import React, { useState } from 'react';
import axios from 'axios';
import { Send } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api";

function ChatWithDocs() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! I am your AI Document Engine. Ask me anything about your codebase!' }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      // 1. Search Vector Database
      const searchRes = await axios.post(`${API_URL}/search_citations`, {
        query: input,
        n_results: 10
      });
      
      const { docs, metas } = searchRes.data;
      const context = docs && docs.length > 0 ? docs.join("\n\n") : "No relevant documentation found.";

      // We cannot securely call Groq directly from the frontend without exposing the API key!
      // In a real Vercel app, we would make a backend endpoint for chat.
      // But since we want to migrate quickly, let's add a /api/chat endpoint to FastAPI!
      
      const chatRes = await axios.post(`${API_URL}/chat`, {
        prompt: input,
        context: context
      });

      const assistantMessage = { 
        role: 'assistant', 
        content: chatRes.data.response,
        sources: metas 
      };
      
      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error. Is the backend running?' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="messages glass-card">
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            <div className="markdown" dangerouslySetInnerHTML={{ __html: msg.content.replace(/\n/g, '<br/>') }} />
            
            {msg.sources && msg.sources.length > 0 && (
              <div style={{ marginTop: '1rem', borderTop: '1px solid var(--border-light)', paddingTop: '1rem' }}>
                <strong style={{ fontSize: '0.9rem' }}>📚 Sources:</strong>
                <ul style={{ listStyle: 'none', marginTop: '0.5rem' }}>
                  {msg.sources.map((meta, idx) => (
                    <li key={idx} style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                      🔹 <code>{meta.file_path || "Unknown"}</code> ➡️ <code>{meta.name || "Unnamed"}</code>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
        {loading && <div className="message assistant">Thinking...</div>}
      </div>

      <form className="chat-input-wrapper" onSubmit={handleSend}>
        <input 
          type="text" 
          className="chat-input" 
          placeholder="Ask a question about your code..." 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
        />
        <button type="submit" className="btn btn-primary" disabled={loading || !input.trim()}>
          <Send size={18} />
        </button>
      </form>
    </div>
  );
}

export default ChatWithDocs;
