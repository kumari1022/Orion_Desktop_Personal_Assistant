import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger("orion_EmailAgent")

class EmailAgent:
    def __init__(self, browser_engine):
        self.browser = browser_engine
        
    async def open_gmail(self) -> str:
        print("[EMAIL] Opening Gmail")
        logger.info("[EMAIL] Opening Gmail")
        await self.browser.open_site("https://mail.google.com")
        return "Gmail opened successfully."
        
    async def start_compose(self, recipient: str) -> str:
        print(f"[EMAIL] Compose mode activated for recipient: {recipient}")
        logger.info(f"[EMAIL] Compose mode activated for recipient: {recipient}")
        
        driver = self.browser.get_driver()
        if "mail.google.com" not in driver.current_url:
            await self.open_gmail()
            time.sleep(4)
            
        # Try composing
        try:
            compose_btn = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//div[text()='Compose' or contains(text(),'Compose') or @role='button' and contains(@class,'T-I-KE')]"))
            )
            compose_btn.click()
        except Exception as e:
            logger.warning(f"Compose button element click failed: {e}. Trying JS fallback.")
            driver.execute_script("""
                var divs = document.querySelectorAll('div[role="button"]');
                for (var d of divs) {
                    if (d.innerText.includes('Compose')) {
                        d.click();
                        break;
                    }
                }
            """)
            
        time.sleep(2)
        
        # Enter recipient
        try:
            to_field = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//input[contains(@aria-label, 'To') or @name='to' or contains(@peoplekit-id, 'To')] | //textarea[contains(@aria-label, 'To')]"))
            )
            to_field.clear()
            to_field.send_keys(recipient)
            to_field.send_keys(Keys.ENTER)
        except Exception as e:
            logger.error(f"To field standard entry failed: {e}. Trying JS fallback.")
            driver.execute_script(f"""
                var inputs = document.querySelectorAll('input, textarea');
                for (var inp of inputs) {{
                    var label = inp.getAttribute('aria-label') || '';
                    if (label.includes('To') || inp.name === 'to') {{
                        inp.value = '{recipient}';
                        inp.dispatchEvent(new Event('input', {{bubbles: true}}));
                        break;
                    }}
                }}
            """)
            
        print("[EMAIL] Waiting for message body")
        logger.info("[EMAIL] Waiting for message body")
        return "Please tell me the email message."
        
    async def type_body(self, content: str) -> str:
        print("[EMAIL] Typing message body")
        logger.info("[EMAIL] Typing message body")
        driver = self.browser.get_driver()
        
        try:
            body_field = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Message Body' or @role='textbox' or contains(@class,'Am Al editable')]"))
            )
            body_field.click()
            body_field.send_keys(content)
        except Exception as e:
            logger.error(f"Body field typing failed: {e}. Trying JS fallback.")
            safe_content = content.replace("'", "\\'")
            driver.execute_script(f"""
                var body = document.querySelector('div[aria-label="Message Body"], div[role="textbox"], .Am.Al.editable');
                if (body) {{
                    body.focus();
                    body.innerText = '{safe_content}';
                    body.dispatchEvent(new Event('input', {{bubbles: true}}));
                }}
            """)
            
        print("[EMAIL] Waiting for send confirmation")
        logger.info("[EMAIL] Waiting for send confirmation")
        return "Message added. Say send to deliver the email."
        
    async def send_email(self) -> str:
        print("[EMAIL] Sending email")
        logger.info("[EMAIL] Sending email")
        driver = self.browser.get_driver()
        
        try:
            send_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and (text()='Send' or contains(@aria-label, 'Send'))]"))
            )
            send_btn.click()
        except Exception as e:
            logger.error(f"Send button click failed: {e}. Trying JS fallback.")
            driver.execute_script("""
                var divs = document.querySelectorAll('div[role="button"]');
                for (var d of divs) {
                    if (d.innerText.includes('Send') || (d.getAttribute('aria-label') || '').includes('Send')) {
                        d.click();
                        break;
                    }
                }
            """)
            
        time.sleep(2)
        print("[EMAIL] Email workflow completed")
        logger.info("[EMAIL] Email workflow completed")
        return "Email sent successfully."

    async def cancel_compose(self) -> str:
        print("[EMAIL] Email composition cancelled.")
        logger.info("[EMAIL] Email composition cancelled.")
        driver = self.browser.get_driver()
        try:
            # Click the discard button (trash can) in Gmail
            discard_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and @aria-label='Discard draft']"))
            )
            discard_btn.click()
        except Exception as e:
            logger.warning(f"Discard button click failed: {e}. Trying JS fallback.")
            try:
                driver.execute_script("""
                    var discard = document.querySelector('div[role="button"][aria-label="Discard draft"]');
                    if (discard) discard.click();
                """)
            except:
                pass
        return "Email composition cancelled."
