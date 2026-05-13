import React, { useState, useRef, useEffect, useCallback } from 'react'
import Sidebar from './components/Sidebar'
import ChatMessage from './components/ChatMessage'
import WelcomeScreen from './components/WelcomeScreen'
import FileUploadIndicator from './components/FileUploadIndicator'
import { Send, Paperclip, Image } from 'lucide-react'

const API_BASE = '/api'

export default function App() {
  const [conversations, setConversations] = useState([])
  const [activeConversation, setActiveConversation] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [uploadedFile, setUploadedFile] = useState(null)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const messagesEndRef = useRef(null)
  const textareaRef = useRef(null)
  const fileInputRef = useRef(null)
  const imageInputRef = useRef(null)

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  useEffect(() => { scrollToBottom() }, [messages, scrollToBottom])

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 120) + 'px'
    }
  }, [input])

  const startNewChat = useCallback(() => {
    setActiveConversation(null)
    setMessages([])
    setUploadedFile(null)
    setSidebarOpen(false)
  }, [])

  const handleSend = useCallback(async () => {
    if (!input.trim() && !uploadedFile) return
    if (loading) return

    const userMessage = input.trim()
    setInput('')
    setLoading(true)

    const userMsg = { role: 'user', content: userMessage }
    setMessages(prev => [...prev, userMsg])

    const history = messages.map(m => ({ role: m.role, content: m.content }))

    try {
      const body = {
        message: userMessage,
        conversation_id: activeConversation,
        history,
        uploaded_file_id: uploadedFile?.file_id || null,
      }

      const res = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })

      if (!res.ok) throw new Error('Failed to get response')

      const data = await res.json()

      if (!activeConversation) {
        const convId = data.conversation_id
        setActiveConversation(convId)
        setConversations(prev => [
          { id: convId, title: userMessage.slice(0, 50), timestamp: new Date() },
          ...prev,
        ])
      }

      const assistantMsg = {
        role: 'assistant',
        content: data.message,
        action: data.action,
        file_url: data.file_url,
        file_name: data.file_name,
        walkthrough_steps: data.walkthrough_steps,
      }

      setMessages(prev => [...prev, assistantMsg])
    } catch (err) {
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.',
          action: 'error',
        },
      ])
      console.error('Chat error:', err)
    } finally {
      setLoading(false)
      setUploadedFile(null)
    }
  }, [input, loading, messages, activeConversation, uploadedFile])

  const handleKeyDown = useCallback((e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }, [handleSend])

  const handleFileUpload = useCallback(async (e) => {
    const file = e.target.files?.[0]
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await fetch(`${API_BASE}/files/upload`, {
        method: 'POST',
        body: formData,
      })

      if (!res.ok) {
        const err = await res.json()
        alert(err.detail || 'Upload failed')
        return
      }

      const data = await res.json()
      setUploadedFile(data)

      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: `File "${data.file_name}" uploaded successfully!\n\nSheets: ${data.sheet_names.join(', ')}\n\n${data.summary}\n\nWhat would you like me to do with this file?`,
          action: 'info',
        },
      ])
    } catch {
      alert('Failed to upload file')
    }

    e.target.value = ''
  }, [])

  const handleImageUpload = useCallback(async (e) => {
    const file = e.target.files?.[0]
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await fetch(`${API_BASE}/files/upload-image`, {
        method: 'POST',
        body: formData,
      })

      if (!res.ok) {
        const err = await res.json()
        alert(err.detail || 'Upload failed')
        return
      }

      const data = await res.json()
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: data.message,
          action: 'info',
        },
      ])
    } catch {
      alert('Failed to upload image')
    }

    e.target.value = ''
  }, [])

  const handleQuickAction = useCallback((prompt) => {
    setInput(prompt)
    textareaRef.current?.focus()
  }, [])

  const loadConversation = useCallback((conv) => {
    setActiveConversation(conv.id)
    setSidebarOpen(false)
  }, [])

  const hasMessages = messages.length > 0

  return (
    <div className="app">
      <div className={`sidebar-overlay ${sidebarOpen ? 'open' : ''}`} onClick={() => setSidebarOpen(false)} />
      <Sidebar
        conversations={conversations}
        activeId={activeConversation}
        onSelect={loadConversation}
        onNewChat={startNewChat}
        isOpen={sidebarOpen}
      />

      <div className="main">
        <div className="mobile-header">
          <button className="menu-btn" onClick={() => setSidebarOpen(true)}>&#9776;</button>
          <span style={{ fontWeight: 600 }}>Excel Master Worker</span>
        </div>

        <div className="chat-header">
          <h2>Excel Master Worker</h2>
          <div className="status">Ready</div>
        </div>

        {!hasMessages ? (
          <WelcomeScreen onAction={handleQuickAction} />
        ) : (
          <div className="messages">
            {messages.map((msg, i) => (
              <ChatMessage key={i} message={msg} />
            ))}
            {loading && (
              <div className="message assistant">
                <div className="message-avatar">X</div>
                <div className="message-content">
                  <div className="typing-indicator">
                    <span /><span /><span />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}

        <div className="input-area">
          {uploadedFile && (
            <FileUploadIndicator
              fileName={uploadedFile.file_name}
              onRemove={() => setUploadedFile(null)}
            />
          )}
          <div className="input-wrapper">
            <div className="input-actions">
              <button
                className="input-action-btn"
                onClick={() => fileInputRef.current?.click()}
                title="Upload Excel file"
              >
                <Paperclip size={18} />
              </button>
              <button
                className="input-action-btn"
                onClick={() => imageInputRef.current?.click()}
                title="Upload screenshot"
              >
                <Image size={18} />
              </button>
            </div>
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Describe the Excel file you need..."
              rows={1}
            />
            <button
              className="send-btn"
              onClick={handleSend}
              disabled={loading || (!input.trim() && !uploadedFile)}
            >
              <Send size={18} />
            </button>
          </div>
          <input
            ref={fileInputRef}
            type="file"
            accept=".xlsx,.xlsm,.xls,.csv"
            onChange={handleFileUpload}
            style={{ display: 'none' }}
          />
          <input
            ref={imageInputRef}
            type="file"
            accept="image/*"
            onChange={handleImageUpload}
            style={{ display: 'none' }}
          />
        </div>
      </div>
    </div>
  )
}
