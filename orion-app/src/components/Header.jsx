import React from 'react';
import './Header.css';

function Header({ backendStatus = 'Checking backend...' }) {
  const handleMinimize = () => {
    if (window.orionAPI?.minimize) {
      window.orionAPI.minimize();
    }
  };

  const handleMaximize = () => {
    if (window.orionAPI?.maximize) {
      window.orionAPI.maximize();
    }
  };

  const handleClose = () => {
    if (window.orionAPI?.close) {
      window.orionAPI.close();
    }
  };

  return (
    <header className="header">
      <div className="header-left">
        <div className="logo-block">
          <h1 className="logo-title">ORION</h1>
          <span className="logo-subtitle">Desktop AI Assistant</span>
        </div>
      </div>

      <div className="header-center">
        <div className="status-pill">
          <span className="status-label">Backend:</span>
          <span className="status-value">{backendStatus}</span>
        </div>
      </div>

      <div className="header-right">
        <button
          className="window-btn"
          onClick={handleMinimize}
          title="Minimize"
          type="button"
        >
          _
        </button>

        <button
          className="window-btn"
          onClick={handleMaximize}
          title="Maximize"
          type="button"
        >
          □
        </button>

        <button
          className="window-btn close-btn"
          onClick={handleClose}
          title="Close"
          type="button"
        >
          ✕
        </button>
      </div>
    </header>
  );
}

export default Header;