const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

const isDev = !app.isPackaged && process.env.NODE_ENV !== 'production';

let mainWindow;
let pythonProcess = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 900,
    minHeight: 650,
    frame: false,
    backgroundColor: '#0B0F1A',
    show: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });
}

function startPythonBackend() {
  const backendDir = path.join(__dirname, '../../mini_project');
  const script = 'api_server.py';

  pythonProcess = spawn('python', [script], {
    cwd: backendDir,
    shell: true
  });

  pythonProcess.stdout.on('data', (data) => {
    console.log(`[PYTHON]: ${data}`);
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`[PYTHON ERROR]: ${data}`);
  });

  pythonProcess.on('close', (code) => {
    console.log(`Python backend exited with code ${code}`);
    pythonProcess = null;
  });
}

function stopPythonBackend() {
  if (pythonProcess) {
    pythonProcess.kill();
    pythonProcess = null;
  }
}

ipcMain.on('window-minimize', () => mainWindow?.minimize());

ipcMain.on('window-maximize', () => {
  if (!mainWindow) return;
  if (mainWindow.isMaximized()) {
    mainWindow.unmaximize();
  } else {
    mainWindow.maximize();
  }
});

ipcMain.on('window-close', () => {
  if (mainWindow) mainWindow.close();
});

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });

  // Optional:
  // startPythonBackend();
});

app.on('before-quit', () => {
  stopPythonBackend();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    stopPythonBackend();
    app.quit();
  }
});