import React from 'react';
import { Routes, Route, NavLink } from 'react-router-dom';
import { Bell, MessageSquare, Settings as SettingsIcon } from 'lucide-react';

import PendingUpdates from './components/PendingUpdates';
import ChatWithDocs from './components/ChatWithDocs';
import Settings from './components/Settings';
// 
function App() {
  return (
    <div className="app-container">
      {/* Premium Glassmorphism Sidebar */}
      <aside className="sidebar">
        <h2 className="sidebar-title">Navigation</h2>
        
        <NavLink 
          to="/" 
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <Bell className="nav-icon" size={20} />
          Pending Updates
        </NavLink>
        
        <NavLink 
          to="/chat" 
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <MessageSquare className="nav-icon" size={20} />
          Chat with Docs
        </NavLink>
        
        <NavLink 
          to="/settings" 
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <SettingsIcon className="nav-icon" size={20} />
          Settings
        </NavLink>
      </aside>

      {/* Main Content Area */}
      <main className="main-content">
        <h1 className="premium-header">AI Document Engine</h1>
        <p className="premium-subtitle">Your self-updating codebase knowledge graph.</p>
        
        <Routes>
          <Route path="/" element={<PendingUpdates />} />
          <Route path="/chat" element={<ChatWithDocs />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
