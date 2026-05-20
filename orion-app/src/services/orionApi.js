export const orionApi = {
  async health() {
    return window.orionAPI.health();
  },

  async sendCommand(command) {
    return window.orionAPI.sendCommand(command);
  },

  async verifyFace() {
    return window.orionAPI.verifyFace();
  },

  async verifyVoice() {
    return window.orionAPI.verifyVoice();
  },

  async listenOnce() {
    return window.orionAPI.listenOnce();
  },

  minimize() {
    window.orionAPI.minimize();
  },

  maximize() {
    window.orionAPI.maximize();
  },

  close() {
    window.orionAPI.close();
  }
};