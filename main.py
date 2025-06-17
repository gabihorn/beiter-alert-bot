import requests
import time
import json
import logging
import os
from datetime import datetime

# הגדרות מ-Environment Variables
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
CHECK_INTERVAL = 10  # 10 שניות

# הגדרת לוגים
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class RealTimeAlertMonitor:
    def __init__(self):
        self.last_alert_id = None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'he-IL,he;q=0.9,en;q=0.8'
        })
        
        logging.info("🚀 בוט התראות זמן אמת - ביתר עילית")
        
    def get_alerts(self):
        """מחזיר התראות מפיקוד העורף"""
        urls = [
            "https://www.oref.org.il/WarningMessages/alert/alerts.json",
            "https://www.oref.org.il/WarningMessages/alert/Alerts.json"
        ]
        
        for url in urls:
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data:
                        return data
            except Exception as e:
                logging.warning(f"שגיאה ב-{url}: {e}")
                continue
        
        return []
    
    def is_beiter_alert(self, alert):
        """בודק אם ההתראה רלוונטית לביתר עילית"""
        data = alert.get('data', '').strip()
        
        beiter_patterns = [
            "ביתר עילית",
            "ביתר-עילית", 
            "בית״ר עילית",
            "בית"ר עילית"
        ]
        
        return any(pattern in data for pattern in beiter_patterns)
    
    def check_new_alert(self, alerts):
        """בודק התראות חדשות לביתר עילית"""
        for alert in alerts:
            if self.is_beiter_alert(alert):
                alert_id = f"{alert.get('alertDate', '')}_{alert.get('data', '')}"
                
                if alert_id != self.last_alert_id:
                    self.last_alert_id = alert_id
                    return alert
        
        return None
    
    def trigger_webhook(self, alert_data):
        """מפעיל וובהוק"""
        if not WEBHOOK_URL:
            logging.error("❌ WEBHOOK_URL לא הוגדר!")
            return False
            
        payload = {
            "alert_type": "beiter_illit",
            "timestamp": datetime.now().isoformat(),
            "alert_date": alert_data.get('alertDate', ''),
            "alert_data": alert_data.get('data', ''),
            "source": "render_monitor"
        }
        
        try:
            response = self.session.post(WEBHOOK_URL, json=payload, timeout=10)
            if response.status_code in [200, 201, 202]:
                logging.info("✅ וובהוק הופעל בהצלחה!")
                return True
            else:
                logging.error(f"וובהוק החזיר סטטוס {response.status_code}")
        except Exception as e:
            logging.error(f"שגיאה בוובהוק: {e}")
        
        return False
    
    def run(self):
        """לולאת הבדיקה הראשית"""
        logging.info(f"🎯 מעקב זמן אמת - בדיקה כל {CHECK_INTERVAL} שניות")
        
        while True:
            try:
                alerts = self.get_alerts()
                
                if alerts:
                    new_alert = self.check_new_alert(alerts)
                    if new_alert:
                        logging.info("🚨 אזעקה בביתר עילית!")
                        logging.info(f"פרטים: {new_alert.get('data', '')}")
                        self.trigger_webhook(new_alert)
                
                time.sleep(CHECK_INTERVAL)
                
            except Exception as e:
                logging.error(f"שגיאה: {e}")
                time.sleep(30)

if __name__ == "__main__":
    if not WEBHOOK_URL:
        print("❌ חובה להגדיר WEBHOOK_URL!")
        exit(1)
    
    monitor = RealTimeAlertMonitor()
    monitor.run()