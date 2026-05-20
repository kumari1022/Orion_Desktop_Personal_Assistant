import React from 'react';
import './Settings.css';

const Settings = ({ resetAuth, theme, setTheme }) => {
    return (
        <div className="settings-container">
            <h2 className="settings-title glow-text-blue">System Settings</h2>

            <div className="settings-card glass-panel">
                <div className="settings-group">
                    <div className="settings-label">
                        <h3>Theme</h3>
                        <p>Modify the interface appearance</p>
                    </div>
                    <div className="settings-action">
                        <button 
                            className={`toggle-btn ${theme === 'dark' ? 'active' : ''}`}
                            onClick={() => setTheme('dark')}
                        >
                            [ Dark Mode ]
                        </button>
                        <button 
                            className={`toggle-btn ${theme === 'light' ? 'active' : ''}`}
                            onClick={() => setTheme('light')}
                        >
                            [ Light Mode ]
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Settings;
