import time, requests, os

API_BASE = os.getenv("NEXUS_API_BASE", "http://localhost:8080")
API_KEY = os.getenv("DESKTOP_AGENT_KEY", "")

def send_heartbeat():
    try:
        res = requests.post(f"{API_BASE}/api/v1/agents/heartbeat",
                           headers={"X-Agent-Key": API_KEY}, timeout=5)
        print(f"Heartbeat enviado: {res.status_code}")
    except Exception as e:
        print(f"Error enviando heartbeat: {e}")

if __name__ == "__main__":
    print("Agente Desktop-Automation iniciado. Enviando heartbeats...")
    while True:
        send_heartbeat()
        time.sleep(60)
