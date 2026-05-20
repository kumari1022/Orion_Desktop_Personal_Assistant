from online.web_agent.runner import run_web_agent

def classify_intent(command):
    return "HYBRID"

def route_intent(command):
    return run_web_agent(command)