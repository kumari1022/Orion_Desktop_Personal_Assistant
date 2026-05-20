import React, { useEffect, useState } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import AuthPanel from './components/AuthPanel';
import Dashboard from './components/Dashboard';
import Settings from './pages/Settings';
import { orionApi } from './services/orionApi';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [theme, setTheme] = useState(localStorage.getItem('orion-theme') || 'dark');

  const [faceStatus, setFaceStatus] = useState('Not verified');
  const [voiceStatus, setVoiceStatus] = useState('Waiting');
  const [backendStatus, setBackendStatus] = useState('Checking backend...');
  const [isListening, setIsListening] = useState(false);

  const [isFaceVerified, setIsFaceVerified] = useState(false);
  const [isVoiceVerified, setIsVoiceVerified] = useState(false);

  const [chatMode, setChatMode] = useState(false);

  // Require only face for easier testing (or both if you prefer)
  const isAuthenticated = isFaceVerified;

  const [messages, setMessages] = useState([
    { sender: 'system', text: 'Initializing ORION core modules...' },
    { sender: 'orion', text: 'Frontend connected. Please complete authentication before issuing commands.' }
  ]);

  useEffect(() => {
    localStorage.setItem('orion-theme', theme);
    if (theme === 'light') {
      document.body.classList.add('light-theme');
    } else {
      document.body.classList.remove('light-theme');
    }
  }, [theme]);

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const res = await orionApi.health();
        if (res.status === 'ok') {
          setBackendStatus('Backend connected');
          setMessages(prev => [
            ...prev,
            { sender: 'system', text: 'Python ORION backend connected successfully.' }
          ]);
        } else {
          setBackendStatus('Backend unavailable');
        }
      } catch (err) {
        setBackendStatus('Backend unavailable');
        setMessages(prev => [
          ...prev,
          { sender: 'system', text: `Backend connection failed: ${err.message}` }
        ]);
      }
    };

    checkBackend();
  }, []);

  const pushFirstAuthenticateMessage = () => {
    setMessages(prev => [
      ...prev,
      { sender: 'system', text: 'First authenticate to use ORION commands.' }
    ]);
  };

  const handleMicToggle = async () => {
    if (!isAuthenticated) {
      pushFirstAuthenticateMessage();
      return;
    }

    try {
      setIsListening(true);
      setMessages(prev => [...prev, { sender: 'system', text: 'Listening for voice command...' }]);

      const listenRes = await orionApi.listenOnce();
      const heardText = listenRes.status?.trim();

      setIsListening(false);

      if (!heardText) {
        setMessages(prev => [...prev, { sender: 'orion', text: 'No voice command detected.' }]);
        return;
      }

      setMessages(prev => [...prev, { sender: 'user', text: heardText }]);

      const cmdRes = await orionApi.sendCommand(heardText);
      setMessages(prev => [...prev, { sender: 'orion', text: cmdRes.response }]);
    } catch (err) {
      setIsListening(false);
      setMessages(prev => [...prev, { sender: 'orion', text: `Voice error: ${err.message}` }]);
    }
  };

  const handleSendMessage = async (text) => {
    if (!text?.trim()) return;

    if (!isAuthenticated) {
      setMessages(prev => [
        ...prev,
        { sender: 'user', text },
        { sender: 'system', text: 'First authenticate to use ORION commands.' }
      ]);
      return;
    }

    setMessages(prev => [...prev, { sender: 'user', text }]);

    try {
      const res = await orionApi.sendCommand(text);
      setMessages(prev => [...prev, { sender: 'orion', text: res.response }]);
    } catch (err) {
      setMessages(prev => [...prev, { sender: 'orion', text: `Request failed: ${err.message}` }]);
    }
  };

  const handleFaceAuth = async () => {
    try {
      setFaceStatus('Scanning...');
      const res = await orionApi.verifyFace();
      setFaceStatus(res.status);
      setIsFaceVerified(!!res.success);
      setMessages(prev => [...prev, { sender: 'system', text: res.status }]);
    } catch (err) {
      setFaceStatus('Face auth failed');
      setIsFaceVerified(false);
      setMessages(prev => [...prev, { sender: 'system', text: `Face auth error: ${err.message}` }]);
    }
  };

  const handleVoiceAuth = async () => {
    if (voiceStatus === 'Verifying...') return; // Prevent duplicate concurrent clicks
    try {
      setVoiceStatus('Verifying...');
      const res = await orionApi.verifyVoice();
      setVoiceStatus(res.status);
      setIsVoiceVerified(!!res.success);
      setMessages(prev => [...prev, { sender: 'system', text: res.status }]);
    } catch (err) {
      setVoiceStatus('Voice auth failed');
      setIsVoiceVerified(false);
      setMessages(prev => [...prev, { sender: 'system', text: `Voice auth error: ${err.message}` }]);
    }
  };

  const resetAuth = () => {
    setFaceStatus('Not verified');
    setVoiceStatus('Waiting');
    setIsFaceVerified(false);
    setIsVoiceVerified(false);
    setChatMode(false);
    setMessages([
      { sender: 'system', text: 'Security override initiated. Authentications reset.' }
    ]);
  };

  return (
    <div className="app-layout">
      <Header backendStatus={backendStatus} />
      <div className="main-content">
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
        <div className="content-area">
          {activeTab === 'dashboard' ? (
            <div className="dashboard-layout">
              <AuthPanel
                faceStatus={faceStatus}
                voiceStatus={voiceStatus}
                onFaceAuth={handleFaceAuth}
                onVoiceAuth={handleVoiceAuth}
                isFaceVerified={isFaceVerified}
                isVoiceVerified={isVoiceVerified}
                isAuthenticated={isAuthenticated}
              />

              <div className="dashboard-divider"></div>

              <Dashboard
                messages={messages}
                isListening={isListening}
                onMicToggle={handleMicToggle}
                onSendMessage={handleSendMessage}
                isAuthenticated={isAuthenticated}
                chatMode={chatMode}
                setChatMode={setChatMode}
              />
            </div>
          ) : (
            <Settings resetAuth={resetAuth} theme={theme} setTheme={setTheme} />
          )}
        </div>
      </div>
    </div>
  );
}

export default App;