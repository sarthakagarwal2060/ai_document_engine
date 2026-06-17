import React, { useState } from 'react';
import axios from 'axios';
import { Rocket } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api";

function Settings() {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  const handleIngest = async () => {
    if (!window.confirm("Running a full ingestion will scan your entire repository and overwrite existing documentation. Continue?")) {
      return;
    }

    try {
      setLoading(true);
      setMessage(null);
      const res = await axios.post(`${API_URL}/ingest_repo`);
      
      if (res.status === 200) {
        setMessage({ type: 'success', text: "✅ Full repository ingestion task has been started in the background! Check backend logs for progress." });
      }
    } catch (err) {
      console.error(err);
      setMessage({ type: 'error', text: "❌ Failed to start ingestion task on internal API." });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="glass-card">
        <h2 style={{ marginBottom: '1rem' }}>Repository Settings</h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
          Use this panel to manage your Documentation Engine's global state.
        </p>
        
        <div style={{ borderTop: '1px solid var(--border-light)', paddingTop: '2rem' }}>
          <h3 style={{ marginBottom: '1rem' }}>🔄 Full Manual Ingestion</h3>
          
          <div className="glass-card" style={{ borderLeft: '4px solid var(--warning)', marginBottom: '1.5rem' }}>
            <p><strong>Warning:</strong> Running a full ingestion will scan your entire repository and overwrite existing documentation.</p>
          </div>

          <button 
            className="btn btn-primary" 
            onClick={handleIngest}
            disabled={loading}
          >
            <Rocket size={18} />
            {loading ? 'Starting Ingestion...' : 'Run Full Repository Ingestion'}
          </button>

          {message && (
            <div style={{ marginTop: '1.5rem', color: message.type === 'error' ? 'var(--danger)' : 'var(--success)' }}>
              {message.text}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Settings;
