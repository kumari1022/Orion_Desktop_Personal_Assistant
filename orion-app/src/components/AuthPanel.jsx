import React from 'react';
import './AuthPanel.css';

function AuthPanel({
  faceStatus = 'Not verified',
  voiceStatus = 'Waiting',
  onFaceAuth,
  onVoiceAuth,
  isFaceVerified = false,
  isVoiceVerified = false,
  isAuthenticated = false
}) {
  return (
    <div className="auth-panel">
      <div className="auth-panel-header">
        <h2>Authentication Panel</h2>
        <p>Run biometric verification before issuing commands.</p>
      </div>

      <div className="auth-section">
        {!isFaceVerified && (
          <div className="auth-card">
            <div className="auth-card-top">
              <h3>Face Recognition</h3>
              <span className="auth-status">{faceStatus}</span>
            </div>

            <p className="auth-description">
              Uses your camera to verify the registered administrator face.
            </p>

            <button className="auth-btn" onClick={onFaceAuth} type="button">
              Verify Face
            </button>
          </div>
        )}

        {!isVoiceVerified && (
          <div className="auth-card">
            <div className="auth-card-top">
              <h3>Voice Recognition</h3>
              <span className="auth-status">{voiceStatus}</span>
            </div>

            <p className="auth-description">
              Uses your microphone to verify the registered administrator voice.
            </p>

            <button className="auth-btn" onClick={onVoiceAuth} type="button">
              Verify Voice
            </button>
          </div>
        )}

        {isAuthenticated && (
          <div className="auth-card auth-complete-card">
            <div className="auth-card-top">
              <h3>Authentication Complete</h3>
              <span className="auth-status">Access Granted</span>
            </div>

            <p className="auth-description">
              All required verifications are complete. ORION command access is now enabled.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default AuthPanel;