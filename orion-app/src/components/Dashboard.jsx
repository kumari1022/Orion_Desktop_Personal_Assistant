import React, { useMemo, useState } from 'react';
import './Dashboard.css';

function Dashboard({
  messages = [],
  isListening = false,
  onMicToggle,
  onSendMessage,
  isAuthenticated = false,
  chatMode = false,
  setChatMode
}) {
  const [input, setInput] = useState('');

  const placeholder = useMemo(() => {
    if (!isAuthenticated) return 'Authenticate first...';
    return chatMode ? 'Type your command...' : 'Voice mode active...';
  }, [isAuthenticated, chatMode]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!chatMode) return;
    if (!input.trim()) return;

    onSendMessage(input.trim());
    setInput('');
  };

  return (
    <div className="dashboard-panel">
      <div className="messages-container">
        {messages.map((msg, index) => (
          <div key={index} className={`message-row ${msg.sender}`}>
            <div className={`message-bubble ${msg.sender}`}>
              {msg.text}
            </div>
            <div className="message-label">
              {msg.sender === 'user'
                ? 'USER'
                : msg.sender === 'system'
                ? 'SYSTEM'
                : 'ORION'}
            </div>
          </div>
        ))}
      </div>

      <div className="command-bar-wrapper">
        <div className="command-bar compact">
          <button
            type="button"
            className={`icon-btn mic-btn ${isListening ? 'active' : ''}`}
            onClick={onMicToggle}
            title="Voice Command"
          >
            🎤
          </button>

          <button
            type="button"
            className={`chat-toggle-btn ${chatMode ? 'active' : ''}`}
            onClick={() => setChatMode(!chatMode)}
            title="Toggle Chat Mode"
          >
            {chatMode ? 'Close Chat' : 'Open Chat'}
          </button>

          {chatMode && (
            <form className="chat-input-form" onSubmit={handleSubmit}>
              <input
                type="text"
                className="command-input"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={placeholder}
                disabled={!isAuthenticated}
              />
              <button
                type="submit"
                className="send-btn"
                disabled={!isAuthenticated || !input.trim()}
                title="Send Command"
              >
                ➤
              </button>
            </form>
          )}

          {!chatMode && (
            <div className="voice-mode-text">
              {isListening ? 'Listening...' : 'Voice mode'}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;