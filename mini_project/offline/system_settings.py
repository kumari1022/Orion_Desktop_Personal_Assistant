import logging
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
import pythoncom

logger = logging.getLogger("JARVIS_SystemSettings")

class SystemSettings:
    def __init__(self):
        # Initialize COM for pycaw
        pythoncom.CoInitialize()

    def volume_up(self, amount: int = 10) -> str:
        try:
            amount = max(1, min(50, amount))  # Limit step size to avoid too big jumps
            sessions = AudioUtilities.GetAllSessions()
            changed = False

            for session in sessions:
                volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                current = volume.GetMasterVolume()
                new = min(1.0, current + amount / 100.0)
                volume.SetMasterVolume(new, None)
                changed = True

            if changed:
                logger.info(f"Volume increased by {amount}% across sessions")
                return f"Volume increased by {amount}%"
            else:
                return "No active audio sessions found to adjust."
        except Exception as e:
            logger.error(f"Volume up failed: {e}")
            return "Could not increase volume. Run as administrator."

    def volume_down(self, amount: int = 10) -> str:
        try:
            amount = max(1, min(50, amount))
            sessions = AudioUtilities.GetAllSessions()
            changed = False

            for session in sessions:
                volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                current = volume.GetMasterVolume()
                new = max(0.0, current - amount / 100.0)
                volume.SetMasterVolume(new, None)
                changed = True

            if changed:
                logger.info(f"Volume decreased by {amount}% across sessions")
                return f"Volume decreased by {amount}%"
            else:
                return "No active audio sessions found to adjust."
        except Exception as e:
            logger.error(f"Volume down failed: {e}")
            return "Could not decrease volume. Run as administrator."