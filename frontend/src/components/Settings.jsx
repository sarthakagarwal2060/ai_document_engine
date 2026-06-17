import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Rocket } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api";

function Settings() {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    // We use a functional approach to avoid stale closures with setInterval
    const interval = setInterval(async () => {
      try {
        const res = await axios.get(`${API_URL}/ingestion_status`);
        const isIngesting = res.data.is_ingesting;
        
        setLoading((currentLoading) => {
          if (isIngesting) {
            setMessage({ type: 'warning', text: "⏳ Ingestion is currently running in the background..." });
            return true;
          } else {
            // If it WAS loading, but now it's not, we just finished!
            if (currentLoading) {
              setMessage({ type: 'success', text: "✅ Ingestion complete!" });
            }
            return false;
          }
        });
      } catch (err) {
        console.error("Status check failed", err);
      }
    }, 3000);
    
    // Initial check
    axios.get(`${API_URL}/ingestion_status`).then(res => {
      if (res.data.is_ingesting) {
        setLoading(true);
        setMessage({ type: 'warning', text: "⏳ Ingestion is currently running in the background..." });
      }
    });

    return () => clearInterval(interval);
  }, []);

  const handleIngest = async () => {
    if (!window.confirm("Running a full ingestion will scan your entire repository and overwrite existing documentation. Continue?")) {
      return;
    }

    try {
      setLoading(true);
      setMessage({ type: 'warning', text: "⏳ Starting ingestion..." });
      await axios.post(`${API_URL}/ingest_repo`);
    } catch (err) {
      console.error(err);
      setMessage({ type: 'error', text: "❌ Failed to start ingestion task on internal API." });
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
            {loading ? 'Ingestion in Progress...' : 'Run Full Repository Ingestion'}
          </button>

          {message && (
            <div style={{ marginTop: '1.5rem', color: message.type === 'error' ? 'var(--danger)' : message.type === 'warning' ? 'var(--warning)' : 'var(--success)' }}>
              {message.text}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Settings;
