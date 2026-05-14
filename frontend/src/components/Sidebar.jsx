import React from 'react'
import { Plus, MessageSquare } from 'lucide-react'

export default function Sidebar({ conversations, activeId, onSelect, onNewChat, isOpen }) {
  return (
    <div className={`sidebar ${isOpen ? 'open' : ''}`}>
      <div className="sidebar-header">
        <h1>
          <span className="logo-icon">X</span>
          Excel Master
        </h1>
        <p>AI-Powered Excel & Macro Creator</p>
      </div>

      <button className="new-chat-btn" onClick={onNewChat}>
        <Plus size={16} />
        New Chat
      </button>

      <div className="chat-history">
        {conversations.map((conv) => (
          <div
            key={conv.id}
            className={`chat-history-item ${conv.id === activeId ? 'active' : ''}`}
            onClick={() => onSelect(conv)}
          >
            <MessageSquare size={14} style={{ display: 'inline', marginRight: 8, verticalAlign: 'middle' }} />
            {conv.title}
          </div>
        ))}
        {conversations.length === 0 && (
          <div style={{ padding: '20px 12px', color: 'rgba(255,255,255,0.3)', fontSize: 13, textAlign: 'center' }}>
            No conversations yet
          </div>
        )}
      </div>

      <div className="sidebar-footer">
        Excel Master Worker v1.0
      </div>
    </div>
  )
}
