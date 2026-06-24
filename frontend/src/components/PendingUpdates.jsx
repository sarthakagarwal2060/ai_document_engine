import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { CheckCircle, XCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api";

// Styles for rendered markdown inside the dark cards
const markdownContainerStyle = {
  background: 'rgba(0,0,0,0.2)',
  padding: '1rem',
  borderRadius: '8px',
  minHeight: '100px',
  overflow: 'auto',
  fontSize: '0.9rem',
  lineHeight: '1.7',
};

function PendingUpdates() {
  const [updates, setUpdates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchUpdates();
  }, []);

  const fetchUpdates = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/pending_updates`);
      setUpdates(response.data);
    } catch (err) {
      setError("Failed to fetch pending updates. Ensure backend is running.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (index, update) => {
    try {
      const doc_id = `${update.filename}::${update.unit_name}`;
      const metadata = {
        unit_type: "function",
        name: update.unit_name,
        file_path: update.filename
      };

      await axios.post(`${API_URL}/upsert`, {
        doc_id,
        text: update.new_doc_draft,
        metadata
      });

      await axios.delete(`${API_URL}/pending_updates/${index}`);
      
      // Update local state
      setUpdates(updates.filter((_, i) => i !== index));
      alert("Draft approved and saved to database!");
    } catch (err) {
      alert("Failed to approve draft.");
      console.error(err);
    }
  };

  const handleReject = async (index) => {
    try {
      await axios.delete(`${API_URL}/pending_updates/${index}`);
      setUpdates(updates.filter((_, i) => i !== index));
    } catch (err) {
      alert("Failed to reject draft.");
      console.error(err);
    }
  };

  if (loading) return <p>Loading updates...</p>;
  if (error) return <p style={{color: 'var(--danger)'}}>{error}</p>;

  return (
    <div>
      <h2 style={{ marginBottom: '1.5rem' }}>Pending Documentation Updates</h2>
      
      {updates.length === 0 ? (
        <div className="glass-card" style={{ borderLeft: '4px solid var(--success)' }}>
          <p>🎉 All caught up! No pending documentation updates.</p>
        </div>
      ) : (
        <div className="glass-card" style={{ borderLeft: '4px solid var(--warning)' }}>
          <p>⚠️ You have <strong>{updates.length}</strong> code units requiring documentation review.</p>
        </div>
      )}

      {updates.map((update, index) => (
        <div key={index} className="glass-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h3 style={{ fontSize: '1.2rem', color: 'var(--text-primary)' }}>
              📄 {update.filename} ➡️ {update.unit_name}
            </h3>
            <span className={`badge ${update.severity === 'DELETED' ? 'deleted' : 'warning'}`}>{update.severity}</span>
          </div>

          <div style={{ display: 'flex', gap: '2rem', marginBottom: '1.5rem' }}>
            <div style={{ flex: 1 }}>
              <h4 style={{ color: 'var(--danger)', marginBottom: '0.5rem' }}>🛑 Old Documentation</h4>
              <div className="markdown-body" style={markdownContainerStyle}>
                {update.old_doc ? (
                  <ReactMarkdown>{update.old_doc}</ReactMarkdown>
                ) : (
                  <span style={{color: 'var(--text-secondary)'}}>No previous documentation existed.</span>
                )}
              </div>
            </div>
            
            <div style={{ flex: 1 }}>
              <h4 style={{ color: 'var(--success)', marginBottom: '0.5rem' }}>✅ AI Drafted Documentation</h4>
              <div className="markdown-body" style={markdownContainerStyle}>
                {update.new_doc_draft ? (
                  <ReactMarkdown>{update.new_doc_draft}</ReactMarkdown>
                ) : (
                  <span style={{color: 'var(--text-secondary)'}}>No draft generated.</span>
                )}
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '1rem' }}>
            <button className="btn btn-success" onClick={() => handleApprove(index, update)}>
              <CheckCircle size={18} /> Approve Draft
            </button>
            <button className="btn btn-danger" onClick={() => handleReject(index)}>
              <XCircle size={18} /> Reject
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}

export default PendingUpdates;
