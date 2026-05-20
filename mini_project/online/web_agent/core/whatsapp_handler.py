"""WhatsApp Handler for JARVIS"""

import logging
import time
import subprocess
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger("JARVIS_WhatsApp")

class WhatsAppHandler:
    def __init__(self, browser):
        self.browser = browser
        self.is_open = False  # for web version only

    async def open_whatsapp(self, mode: str = "web") -> dict:
        """
        Opens WhatsApp in the requested mode.
        
        mode:
          - "web" (default)     → opens https://web.whatsapp.com
          - "desktop"/"app"     → launches the installed WhatsApp desktop app
        """
        mode = mode.lower().strip()

        if mode in ["desktop", "app", "installed", "native"]:
            try:
                # Preferred method: Use WhatsApp URI scheme (works for both Microsoft Store and direct install)
                subprocess.Popen(["start", "whatsapp:"], shell=True)
                time.sleep(3)  # give the app a moment to launch

                # Alternative (if URI doesn't work on your system):
                # Adjust the path to your actual WhatsApp.exe location
                # subprocess.Popen(r"C:\Users\YourUsername\AppData\Local\WhatsApp\WhatsApp.exe")

                logger.info("Launched WhatsApp Desktop application")
                return {
                    "status": "success",
                    "type": "desktop",
                    "message": "WhatsApp Desktop app opened"
                }
            except FileNotFoundError:
                return {
                    "status": "error",
                    "message": "WhatsApp desktop app not found. Make sure it is installed."
                }
            except Exception as e:
                logger.error(f"Desktop WhatsApp launch failed: {e}")
                return {
                    "status": "error",
                    "message": f"Failed to open WhatsApp Desktop: {str(e)}"
                }

        else:  # web (default)
            try:
                result = await self.browser.open_site("https://web.whatsapp.com")
                if result["status"] == "success":
                    # Prompt only if needed (you can remove input() after first login if cookies are saved)
                    print("WhatsApp Web opened. If QR code appears, scan it with your phone.")
                    print("Press Enter in the terminal when you're ready to continue...")
                    input()  # blocks until user presses Enter (useful for first time)
                    self.is_open = True
                    logger.info("WhatsApp Web opened successfully")
                return {
                    **result,
                    "type": "web",
                    "message": "WhatsApp Web opened"
                }
            except Exception as e:
                logger.error(f"Web WhatsApp open failed: {e}")
                return {"status": "error", "message": str(e)}

    async def search_contact(self, contact_name: str) -> dict:
        if not self.is_open:
            open_result = await self.open_whatsapp("web")
            if open_result["status"] != "success":
                return open_result

        try:
            # Search box selector (WhatsApp Web - quite stable)
            search_box = WebDriverWait(self.browser.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='3']"))
            )
            search_box.clear()
            search_box.send_keys(contact_name)
            time.sleep(1.5)
            search_box.send_keys(Keys.ENTER)
            time.sleep(2)

            # Check if chat actually opened
            try:
                WebDriverWait(self.browser.driver, 8).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'message-in')] | //div[contains(@class, 'message-out')]"))
                )
                return {"status": "success", "contact": contact_name}
            except:
                return {"status": "not_found", "contact": contact_name, "message": "Contact chat not loaded"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def send_message(self, message: str, contact: str = None) -> dict:
        if not self.is_open:
            open_result = await self.open_whatsapp("web")
            if open_result["status"] != "success":
                return open_result

        try:
            if contact:
                contact_result = await self.search_contact(contact)
                if contact_result["status"] != "success":
                    return contact_result

            # Message input box (data-tab=10 is usually the main input)
            msg_box = WebDriverWait(self.browser.driver, 12).until(
                EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='10']"))
            )
            msg_box.send_keys(message)
            msg_box.send_keys(Keys.ENTER)
            time.sleep(1)

            return {
                "status": "success",
                "message": message,
                "recipient": contact or "current chat"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # Optional: send_media method (if you use it) can stay as is or be updated similarly