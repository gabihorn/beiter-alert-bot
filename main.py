import requests
import time
import logging
import os
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

WEBHOOK_URL = os.getenv('WEBHOOK_URL')
PORT = int(os.getenv('PORT', 10000))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is running!')
    def log_message(self, format, *args): return

def check_alerts():
    while True:
        try:
            response = requests.get("https://www.oref.org.il/WarningMessages/alert/alerts.json", timeout=10)
            if response.status_code == 200:
                alerts = response.json()
                if alerts:
                    for alert in alerts:
                        data = alert.get('data', '')
                        if 'ביתר עילית' in data or 'ביתר-עילית' in data:
                            logging.info(f"🚨 התראה: {data}")
                            if WEBHOOK_URL:
                                requests.post(WEBHOOK_URL, json={
                                    "alert": data,
                                    "timestamp": datetime.now().isoformat()
                                })
            time.sleep(10)
        except:
            time.sleep(30)

def main():
    threading.Thread(target=lambda: HTTPServer(('0.0.0.0', PORT), HealthHandler).serve_forever(), daemon=True).start()
    logging.info("🚀 Bot started")
    check_alerts()

if __name__ == "__main__": main()
