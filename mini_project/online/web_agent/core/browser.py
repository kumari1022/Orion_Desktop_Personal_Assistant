import os
import logging
import time
import urllib.parse
import sys
import subprocess

# Ensure selenium is installed automatically if missing
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
except ImportError:
    print("[SYSTEM] selenium is missing, installing automatically...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium"])
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

# Ensure webdriver_manager is installed automatically if missing
try:
    from webdriver_manager.chrome import ChromeDriverManager
except Exception:
    print("[SYSTEM] webdriver-manager is missing, attempting to install automatically...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "webdriver-manager"])
        from webdriver_manager.chrome import ChromeDriverManager
    except Exception as install_err:
        print(f"[SYSTEM] Failed to install/import webdriver-manager: {install_err}")
        ChromeDriverManager = None

from config import settings

logger = logging.getLogger("JARVIS_Browser")

class BrowserEngine:
    def __init__(self):
        self.driver = None
        self.current_url = ""
        
    def initialize(self, headless: bool = False):
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        
        # Crash prevention (must-have on Windows)
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--remote-debugging-pipe")
        options.add_argument("--remote-debugging-port=9222")
        options.add_argument("--disable-extensions")
        
        # Disable automation detection as much as possible
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        # Persistent profile
        profile_dir = r"C:\orion_chrome_profile"
        if not os.path.exists(profile_dir):
            try:
                os.makedirs(profile_dir, exist_ok=True)
            except:
                pass # Fallback if restricted
        options.add_argument(f"--user-data-dir={profile_dir}")
        print("[SYSTEM] Using persistent Chrome profile")

        if headless:
            options.add_argument("--headless=new")

        driver_initialized = False

        # Try webdriver-manager first
        if ChromeDriverManager is not None:
            try:
                print("[SYSTEM] Installing compatible ChromeDriver")
                # Using ChromeDriverManager to install/get Chrome driver matching local version
                driver_path = ChromeDriverManager().install()
                service = Service(driver_path)
                self.driver = webdriver.Chrome(
                    service=service,
                    options=options
                )
                self.driver.implicitly_wait(10)
                print("[SYSTEM] ChromeDriver initialized successfully")
                logger.info("Browser initialized successfully via webdriver-manager")
                driver_initialized = True
            except Exception as e:
                print("[SYSTEM] webdriver-manager failed")
                logger.warning(f"webdriver-manager failed to install/start ChromeDriver: {e}")
        else:
            print("[SYSTEM] webdriver-manager failed")
            logger.warning("webdriver-manager is not available")

        # Fallback to local ChromeDriver
        if not driver_initialized:
            print("[SYSTEM] Falling back to local ChromeDriver")
            logger.info("Falling back to local ChromeDriver")
            
            # Paths to search for the local chromedriver.exe
            potential_paths = [
                # Hardcoded path requested by user
                r"D:\miniproject\workspace\workspace\mini_project\chromedriver.exe",
                # Dynamic relative path (3 levels up from online/web_agent/core/browser.py)
                os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "chromedriver.exe")),
                # Alternate search paths
                os.path.abspath(os.path.join(os.getcwd(), "chromedriver.exe")),
                os.path.abspath(os.path.join(os.getcwd(), "mini_project", "chromedriver.exe")),
            ]
            
            local_driver_path = None
            for p in potential_paths:
                if os.path.exists(p):
                    local_driver_path = p
                    break
            
            if not local_driver_path:
                local_driver_path = r"D:\miniproject\workspace\workspace\mini_project\chromedriver.exe"
                
            print(f"[SYSTEM] Using local ChromeDriver path: {local_driver_path}")
            logger.info(f"Using local ChromeDriver path: {local_driver_path}")
            
            try:
                service = Service(local_driver_path)
                self.driver = webdriver.Chrome(
                    service=service,
                    options=options
                )
                self.driver.implicitly_wait(10)
                print("[SYSTEM] ChromeDriver initialized successfully (via local fallback)")
                logger.info("Browser initialized successfully via local ChromeDriver fallback")
                driver_initialized = True
            except Exception as e:
                print(f"[SYSTEM] Local ChromeDriver fallback failed: {e}")
                logger.error(f"Local ChromeDriver fallback failed: {e}")
                
        # Prevent application startup crash by ensuring we do not raise an exception
        if not driver_initialized:
            print("[SYSTEM] CRITICAL: Both webdriver-manager and local ChromeDriver fallback failed. Web automation is disabled.")
            logger.critical("Both webdriver-manager and local ChromeDriver fallback failed. Web automation is disabled.")
            self.driver = None

    def get_driver(self, headless: bool = False):
        """Centralized helper to check session health and recreate the driver on-demand."""
        from selenium.common.exceptions import (
            InvalidSessionIdException, 
            WebDriverException, 
            NoSuchWindowException
        )

        if self.driver is None:
            print("[SYSTEM] Creating new Chrome session")
            self.initialize(headless)
            return self.driver

        try:
            # Active session validation checks
            _ = self.driver.current_url
            if not self.driver.window_handles:
                raise NoSuchWindowException("All windows were closed by user")
            
            print("[SYSTEM] Reusing existing Chrome session")
            return self.driver
        except (InvalidSessionIdException, WebDriverException, NoSuchWindowException) as e:
            print("[SYSTEM] Chrome session invalid, recreating driver")
            logger.warning(f"Driver session invalid ({type(e).__name__}). Recreating Chrome session...")
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None
            self.initialize(headless)
            return self.driver
        
    async def open_site(self, url: str, new_tab: bool = False) -> dict:
        try:
            driver = self.get_driver()
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            if new_tab:
                driver.execute_script("window.open();")
                driver.switch_to.window(driver.window_handles[-1])
            driver.get(url)
            self.current_url = url
            return {"status": "success", "url": url, "title": driver.title}
        except Exception as e:
            logger.error(f"Open site failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def search(self, query: str, engine: str = "google", site: str = None) -> dict:
        try:
            driver = self.get_driver()
            if engine.lower() in ["amazon", "amazon.in", "amazon.com"]:
                base = "https://www.amazon.in" if "in" in engine.lower() else "https://www.amazon.com"
                url = f"{base}/s?k={urllib.parse.quote(query)}"
                logger.info(f"Opening Amazon search URL: {url}")
                result = await self.open_site(url)
                
                if result["status"] != "success":
                    logger.error(f"Failed to open Amazon URL: {result}")
                    return result
                
                start_url = driver.current_url
                
                # Step 1: Cookie consent
                try:
                    accept_btn = WebDriverWait(driver, 8).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept') or contains(@id, 'accept') or @aria-label='Accept cookies']"))
                    )
                    accept_btn.click()
                    logger.info("Handled cookie consent popup")
                    time.sleep(2)
                except:
                    pass
 
                # Step 2: Query search box
                try:
                    logger.info("Waiting for Amazon search box...")
                    search_box = WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((By.ID, "twotabsearchtextbox"))
                    )
                    logger.info("Search box found → typing query")
                    
                    search_box.clear()
                    search_box.send_keys(query)
                    search_box.send_keys(Keys.RETURN)
                    logger.info("Submitted search with ENTER")
                    
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div.s-result-item, span.a-size-medium"))
                    )
                    logger.info("Amazon search results detected")
                except Exception as ex:
                    logger.warning(f"Normal interaction failed: {ex}")
                    # JS fallback
                    try:
                        logger.warning("Trying JS fallback...")
                        escaped_query = query.replace("'", "\\'").replace('"', '\\"')
                        driver.execute_script(f"""
                            var box = document.getElementById('twotabsearchtextbox');
                            if (box) {{
                                box.value = '{escaped_query}';
                                box.dispatchEvent(new Event('input', {{bubbles: true}}));
                                var form = box.closest('form') || document.querySelector('form');
                                if (form) form.submit();
                                else {{
                                    var btn = document.querySelector('input[type="submit"], button[type="submit"], [aria-label*="Search"]');
                                    if (btn) btn.click();
                                }}
                            }}
                        """)
                        time.sleep(5)
                        if "/s?k=" in driver.current_url or driver.find_elements(By.CSS_SELECTOR, "div.s-result-item"):
                            logger.info("Fallback search succeeded")
                        else:
                            return {"status": "error", "message": "Amazon search failed (no results)"}
                    except Exception as js_err:
                        logger.error(f"JS fallback failed: {js_err}")
                        return {"status": "error", "message": "Amazon search failed (JS error)"}
                
                return {"status": "success", "url": driver.current_url, "title": driver.title}
            else:
                # General search
                base_url = settings.SEARCH_ENGINES.get(engine.lower(), settings.SEARCH_ENGINES["google"])
                url = base_url + urllib.parse.quote(query)
                if site:
                    url += f"+site:{site}"
                logger.info(f"Opening general search: {url}")
                return await self.open_site(url)
        except Exception as e:
            logger.error(f"Search failed completely: {e}")
            return {"status": "error", "message": str(e)}
    
    async def play_video(self, query: str = None, url: str = None) -> dict:
        try:
            driver = self.get_driver()
            if url:
                await self.open_site(url)
            elif query:
                search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
                logger.info(f"Opening YouTube search: {search_url}")
                await self.open_site(search_url)
                
                logger.info("Waiting for first video to load...")
                first_video = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "ytd-video-renderer a#thumbnail, ytd-video-renderer a#video-title"))
                )
                logger.info("Clicking first video...")
                try:
                    first_video.click()
                except:
                    driver.execute_script("arguments[0].click();", first_video)
                time.sleep(2)
            else:
                driver.execute_script("""
                    var video = document.querySelector('video');
                    if (video) video.play();
                """)
            return {"status": "success", "action": "play_video"}
        except Exception as e:
            logger.error(f"Failed to play video: {e}")
            return {"status": "error", "message": str(e)}
    
    async def navigate(self, instruction: str) -> dict:
        inst = instruction.lower()
        try:
            driver = self.get_driver()
            if "scroll down" in inst:
                driver.execute_script("window.scrollBy(0, 500);")
            elif "scroll up" in inst:
                driver.execute_script("window.scrollBy(0, -500);")
            elif "go back" in inst:
                driver.back()
            elif "go forward" in inst:
                driver.forward()
            elif "refresh" in inst:
                driver.refresh()
            else:
                return {"status": "unknown", "instruction": instruction}
            return {"status": "success", "action": inst}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def get_info(self) -> dict:
        try:
            driver = self.get_driver()
            return {"status": "success", "url": driver.current_url, "title": driver.title}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def open_dynamic_site(self, name: str) -> dict:
        import httpx
        
        name_clean = name.strip().lower()
        print(f"[ROUTE] Dynamic website request detected for '{name_clean}'")
        logger.info(f"[ROUTE] Dynamic website request detected for '{name_clean}'")
        
        candidates = [
            f"https://{name_clean}.com",
            f"https://www.{name_clean}.com",
            f"https://www.{name_clean}.org",
            f"https://{name_clean}.org",
        ]
        
        valid_url = None
        
        for url in candidates:
            print(f"[DEBUG] Constructed URL: Checking '{url}'...")
            logger.info(f"[DEBUG] Constructed URL: Checking '{url}'...")
            try:
                async with httpx.AsyncClient(timeout=3.0) as client:
                    res = await client.head(url, follow_redirects=True)
                    if res.status_code < 400:
                        valid_url = url
                        break
            except Exception:
                pass
            
            try:
                async with httpx.AsyncClient(timeout=3.0) as client:
                    res = await client.get(url, follow_redirects=True)
                    if res.status_code < 400:
                        valid_url = url
                        break
            except Exception:
                pass
                
        if valid_url:
            print(f"[DEBUG] Constructed URL: Success with '{valid_url}'")
            logger.info(f"[DEBUG] Constructed URL: Success with '{valid_url}'")
            return await self.open_site(valid_url)
            
        print(f"[DEBUG] Falling back to Google Search for '{name_clean}'")
        logger.info(f"[DEBUG] Falling back to Google Search for '{name_clean}'")
        
        await self.search(name_clean, engine="google")
        
        try:
            driver = self.get_driver()
            first_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div.g a h3, div#search a h3, a h3"))
            )
            parent_a = first_link.find_element(By.XPATH, "./..")
            url = parent_a.get_attribute("href")
            print(f"[DEBUG] Dynamic website fallback URL: '{url}'")
            logger.info(f"[DEBUG] Dynamic website fallback URL: '{url}'")
            
            try:
                parent_a.click()
            except:
                driver.execute_script("arguments[0].click();", parent_a)
                
            return {"status": "success", "url": url, "message": f"Opened fallback URL: {url}"}
        except Exception as e:
            logger.error(f"Fallback search click failed: {e}")
            return {"status": "error", "message": f"Fallback search click failed: {str(e)}"}
            
    def is_session_valid(self) -> bool:
        try:
            if not self.driver:
                return False
            _ = self.driver.current_url
            return True
        except:
            return False
    
    def close(self):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None