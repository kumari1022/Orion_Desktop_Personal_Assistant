# core/command_router.py

from typing import Optional
import datetime
import logging
import re

from online.general.general_chat import GeneralChat
from online.web_agent.runner import WebAgentRunner
from offline.offline_handler import OfflineHandler

logger = logging.getLogger("orion_Router")

from core.conversation_state import state_manager
from online.web_agent.agents.email_agent import EmailAgent

_chat_engine = GeneralChat()
_web_runner = WebAgentRunner()
_offline_handler = OfflineHandler()
_email_agent = EmailAgent(_web_runner.actor.browser)

def normalize_command(command: str) -> str:
    """Normalize input command to handle variations, remove conversational filler words, and strip punctuation."""
    print(f"[DEBUG] Raw Command: {command}")
    logger.info(f"[DEBUG] Raw Command: {command}")
    
    # Pre-clean markdown email links (e.g., [email](mailto:email) or [email](email))
    command = re.sub(r"\[([^\]]+)\]\(mailto:([^)]+)\)", r"\2", command)
    command = re.sub(r"mailto:", "", command)
    
    # Use regex email extraction BEFORE punctuation cleanup.
    email_regex = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    emails = re.findall(email_regex, command)
    
    # Temporarily replace email addresses with placeholders
    temp_command = command
    placeholders = {}
    for i, email in enumerate(emails):
        placeholder = f"__EMAIL_PLACEHOLDER_{i}__"
        placeholders[placeholder] = email
        temp_command = temp_command.replace(email, placeholder)
        
    cmd = temp_command.lower().strip()
    
    # Strip specified punctuation characters: . , ! ? : ; ' " ( ) [ ]
    cmd = re.sub(r"[.,!\?:;'\(\)\[\]\"]", "", cmd)
    
    # Replace multiple internal spaces with a single space
    cmd = re.sub(r"\s+", " ", cmd).strip()
    
    # Restore the email addresses
    for placeholder, original_email in placeholders.items():
        cmd = cmd.replace(placeholder.lower(), original_email)
        
    # 1. Clean up conversational prefixes / filler words
    filler_prefixes = [
        "can you ", "could you ", "would you ", "hey jarvis ", "hey orion ", 
        "go ahead and ", "please ", "i want to ", "want to "
    ]
    for prefix in filler_prefixes:
        if cmd.startswith(prefix):
            cmd = cmd[len(prefix):]
            
    # 2. Clean up conversational suffixes
    filler_suffixes = [
        " please", " jarvis", " orion", " now"
    ]
    for suffix in filler_suffixes:
        if cmd.endswith(suffix):
            cmd = cmd[:-len(suffix)]
            
    cmd = cmd.strip()
    
    print(f"[DEBUG] Sanitized Command: {cmd}")
    logger.info(f"[DEBUG] Sanitized Command: {cmd}")
    return cmd

def classify_intent(command: str) -> Optional[str]:
    cmd = command.strip().lower()
    
    if any(exit_phrase in cmd for exit_phrase in ["exit", "quit", "shutdown", "close system", "bye", "stop", "goodbye"]):
        return "exit"
    
    if any(time_kw in cmd for time_kw in ["time", "what time", "current time"]):
        return "time"
    
    if any(date_kw in cmd for date_kw in ["date", "what date", "today", "current date"]):
        return "date"
    
    return None

async def route_command(command: str) -> Optional[str]:
    if not command:
        return None

    # Normalize command to handle command-first mapping cleanly
    normalized_cmd = normalize_command(command)
    logger.info(f"[ROUTE] Normalized command: '{normalized_cmd}' (Original: '{command}')")

    # Prioritize active conversational email state
    active_state = state_manager.get_state()
    if active_state and active_state.get("action") == "composing_email":
        # Support cancel command at any step in the flow
        if normalized_cmd == "cancel":
            res = await _email_agent.cancel_compose()
            state_manager.clear_state()
            return res
            
        if active_state.get("awaiting_email_body"):
            # Capture body (retains original casing/punctuation for email content)
            res = await _email_agent.type_body(command)
            state_manager.update_state(message_body=command, awaiting_email_body=False, awaiting_send_confirmation=True)
            return res
            
        elif active_state.get("awaiting_send_confirmation"):
            if normalized_cmd == "send":
                res = await _email_agent.send_email()
                state_manager.clear_state()
                return res
            else:
                return "Please say send to deliver the email, or cancel to abort."

    # 1. Quick local intents (fast path)
    quick_intent = classify_intent(normalized_cmd)
    if quick_intent == "exit":
        logger.info("[ROUTE] Offline command detected: Exit")
        return "EXIT"
    elif quick_intent == "time":
        logger.info("[ROUTE] Offline command detected: Time Query")
        return datetime.datetime.now().strftime("%I:%M %p")
    elif quick_intent == "date":
        logger.info("[ROUTE] Offline command detected: Date Query")
        return datetime.datetime.now().strftime("%A, %B %d, %Y")

    # Email Automation Commands
    if normalized_cmd in ["open email", "open gmail"]:
        res = await _email_agent.open_gmail()
        return res

    # Match direct email automation commands to route directly to EmailAgent
    email_match = re.match(
        r"^(?:compose\s+email\s+to\s+|send\s+email\s+to\s+|email\s+)([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})$", 
        normalized_cmd
    )
    if email_match:
        print("[EMAIL ROUTE] Valid email detected")
        logger.info("[EMAIL ROUTE] Valid email detected")
        recipient = email_match.group(1)
        state_manager.set_state(action="composing_email", recipient=recipient, awaiting_email_body=True, awaiting_send_confirmation=False)
        res = await _email_agent.start_compose(recipient)
        return res

    # 2. Command-first Web Automation Bypass (Online Commands)
    # Checks for direct site opening
    # Pattern: "open youtube", "open google", "open instagram", "open facebook", etc.
    open_site_match = re.match(r"^open\s+(youtube|google|instagram|facebook|github|gmail|linkedin|twitter|reddit|wikipedia)(\.com)?$", normalized_cmd)
    if open_site_match:
        site = open_site_match.group(1)
        url = f"{site}.com"
        logger.info(f"[ROUTE] Online command detected: Opening site '{url}'")
        action = {"type": "open_site", "parameters": {"url": url}}
        web_result = await _web_runner.handle_action(action)
        return web_result or f"Opened {site.title()}"

    # Pattern: "open website <url>" or "open <url>" (if url ends in .com, .org, etc.)
    open_url_match = re.match(r"^(?:open\s+website\s+|open\s+)([\w\-]+\.(?:com|org|net|in|edu|gov|io))$", normalized_cmd)
    if open_url_match:
        url = open_url_match.group(1)
        logger.info(f"[ROUTE] Online command detected: Opening custom URL '{url}'")
        action = {"type": "open_site", "parameters": {"url": url}}
        web_result = await _web_runner.handle_action(action)
        return web_result or f"Opened {url}"

    # Play video/music on YouTube
    # Patterns: "play music", "play a song", "play songs on youtube", "play <query> on youtube", "play <query>"
    if normalized_cmd.startswith("play "):
        query = normalized_cmd[5:].strip()
        # Remove common trailing terms like "on youtube" or "music"
        query = re.sub(r"\s+on\s+youtube$", "", query)
        query = re.sub(r"\s+music$", "", query)
        query = query.strip()
        
        # If the user just said "play", default to a pleasant search term or "lofi"
        if not query or query in ["a song", "music", "songs"]:
            query = "lofi music"
            
        logger.info(f"[ROUTE] Online command detected: Playing '{query}' on YouTube")
        action = {"type": "play_video", "parameters": {"query": query}}
        web_result = await _web_runner.handle_action(action)
        return web_result or f"Playing {query} on YouTube"

    # Search Google
    # Patterns: "search google for <query>", "search google <query>", "search <query> on google", "search <query>"
    search_query = None
    if normalized_cmd.startswith("search google for "):
        search_query = normalized_cmd[18:].strip()
    elif normalized_cmd.startswith("search google "):
        search_query = normalized_cmd[14:].strip()
    elif normalized_cmd.startswith("search ") and normalized_cmd.endswith(" on google"):
        search_query = normalized_cmd[7:-10].strip()
    elif normalized_cmd.startswith("search "):
        search_query = normalized_cmd[7:].strip()

    if search_query:
        logger.info(f"[ROUTE] Online command detected: Searching Google for '{search_query}'")
        action = {"type": "search", "parameters": {"query": search_query, "engine": "google"}}
        web_result = await _web_runner.handle_action(action)
        return web_result or f"Searched Google for '{search_query}'"

    # WhatsApp Handling
    if "open whatsapp" in normalized_cmd or "open web whatsapp" in normalized_cmd:
        logger.info("[ROUTE] Online command detected: Opening WhatsApp")
        if any(word in normalized_cmd for word in ["desktop", "installed", "native", "application"]):
            action = {"type": "whatsapp_open", "parameters": {"mode": "desktop"}}
        else:
            action = {"type": "whatsapp_open", "parameters": {"mode": "web"}}
        web_result = await _web_runner.handle_action(action)
        return web_result or "WhatsApp opened"

    # Dynamic Website Opener
    if normalized_cmd.startswith("open "):
        site_candidate = normalized_cmd[5:].strip()
        
        # Avoid routing offline applications or folder/file creations
        known_offline_apps = ["notepad", "calculator", "chrome", "paint", "cmd", "explorer", "taskmgr", "spotify", "code", "word", "excel", "powerpoint"]
        
        if site_candidate not in known_offline_apps and not any(kw in site_candidate for kw in ["folder", "file", "code", "document", "desktop"]):
            logger.info(f"[ROUTE] Dynamic website request detected for '{site_candidate}'")
            action = {"type": "open_dynamic_site", "parameters": {"name": site_candidate}}
            web_result = await _web_runner.handle_action(action)
            return web_result or f"Opened {site_candidate.title()}"

    # 3. Offline Commands (Apps/Files/Folders)
    # Patterns: "open notepad", "open calculator", "open chrome", "open paint", "open cmd", etc.
    offline_keywords = [
        "launch ", "start ", "run ", "open ",            # apps
        "create folder", "make folder", "new folder", "folder ",  # folders
        "create file", "make file", "new file", "file ",          # files
        "create ", "make ", "add file",                           # broader
        "write ", "add code", "generate code", "program ",        # code writing
        "in desktop", "on desktop", "in documents", "on documents", # locations
        "in file", "into file", "to file"                         # file phrases
    ]
    
    if any(kw in normalized_cmd for kw in offline_keywords):
        logger.info(f"[ROUTE] Offline command detected: '{normalized_cmd}'")
        offline_result = await _offline_handler.process(normalized_cmd)
        logger.info(f"Offline handler result: {offline_result}")
        return offline_result

    # 4. Unknown/Conversational queries -> Ollama (LLM Fallback)
    logger.info(f"[ROUTE] Sending to LLM: '{normalized_cmd}'")
    result = await _chat_engine.process(normalized_cmd)

    if not result:
        return "Sorry, I didn't understand that."

    if result.get("type") == "general":
        return result.get("response")

    elif result.get("type") == "web_task":
        action = result.get("action")
        if action:
            web_result = await _web_runner.handle_action(action)
            return web_result or "Task executed."

    return "Command processed, but no clear response."