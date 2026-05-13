import React from 'react'
import { Download, FileSpreadsheet } from 'lucide-react'

export default function ChatMessage({ message }) {
  const isUser = message.role === 'user'

  return (
    <div className={`message ${message.role}`}>
      <div className="message-avatar">
        {isUser ? 'U' : 'X'}
      </div>
      <div className="message-content">
        <div style={{ whiteSpace: 'pre-wrap' }}>{message.content}</div>

        {message.file_url && message.file_name && (
          <a
            href={message.file_url}
            download={message.file_name}
            className="file-download"
          >
            <div className="file-icon">
              <FileSpreadsheet size={20} />
            </div>
            <div className="file-info">
              <div className="file-name">{message.file_name}</div>
              <div className="file-action">Click to download</div>
            </div>
            <Download size={18} />
          </a>
        )}

        {message.walkthrough_steps && message.walkthrough_steps.length > 0 && (
          <div className="walkthrough">
            <h4>Step-by-Step Guide</h4>
            <ol>
              {message.walkthrough_steps.map((step, i) => (
                <li key={i}>{step}</li>
              ))}
            </ol>
          </div>
        )}
      </div>
    </div>
  )
}
