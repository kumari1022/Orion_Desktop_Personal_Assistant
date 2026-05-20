import React, { useState } from 'react';
import './CommandInput.css';

const CommandInput = ({ isListening, onMicToggle, onSendMessage }) => {
    const [text, setText] = useState('');

    const handleSend = () => {
        if (text.trim() === '') return;
        if (onSendMessage) {
            onSendMessage(text);
        }
        setText('');
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div className="command-input-container">
            <button
                className={`mic-btn ${isListening ? 'listening' : ''}`}
                onClick={onMicToggle}
                title={isListening ? 'Stop Listening' : 'Start Listening'}
            >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"></path>
                    <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                    <line x1="12" y1="19" x2="12" y2="22"></line>
                </svg>
                {isListening && <div className="pulse-ring"></div>}
            </button>

            <input
                type="text"
                className="text-input"
                placeholder="Awaiting command..."
                value={text}
                onChange={(e) => setText(e.target.value)}
                onKeyDown={handleKeyDown}
            />

            <button className="send-btn" onClick={handleSend} title="Send Command">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="22" y1="2" x2="11" y2="13"></line>
                    <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                </svg>
            </button>
        </div>
    );
};

export default CommandInput;
