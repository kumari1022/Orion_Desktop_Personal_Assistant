const { contextBridge, ipcRenderer } = require('electron');

const API_BASE = 'http://127.0.0.1:8000';

async function post(path, body = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: Object.keys(body).length ? JSON.stringify(body) : undefined
  });

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  return response.json();
}

async function get(path) {
  const response = await fetch(`${API_BASE}${path}`);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

contextBridge.exposeInMainWorld('orionAPI', {
  minimize: () => ipcRenderer.send('window-minimize'),
  maximize: () => ipcRenderer.send('window-maximize'),
  close: () => ipcRenderer.send('window-close'),

  health: () => get('/health'),
  sendCommand: (command) => post('/command', { command }),
  verifyFace: () => post('/auth/face'),
  verifyVoice: () => post('/auth/voice'),
  listenOnce: () => post('/voice/listen')
});