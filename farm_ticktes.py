import os
from datetime import datetime
from logger import FileLogger, get_latest_tickets_iso_date

collect_tickets_btn = '.get-pieces-btn'
file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs", "farm_tickets_logs.csv")


def collect_tickets(page):
    page.goto("https://csgofast.com/tickets")
    page.wait_for_timeout(1000)
    try:
        page.wait_for_selector(collect_tickets_btn)
        collect_btn = page.query_selector(collect_tickets_btn)
        if collect_btn and ':' not in collect_btn.inner_text():
            print(f"Clicking collect tickets button!")
            collect_btn.click()
            logger = FileLogger(file_path)
            logger.log_event("logs/collect_tickets", details="clicked collect tickets button")
    except Exception as e:
        print(f"Error clicking collect tickets button: {e}")
        
def collect_tickets_routine(page):
    last_tickets_iso_date = get_latest_tickets_iso_date()

    if last_tickets_iso_date is None or (datetime.now() - datetime.fromisoformat(last_tickets_iso_date)).total_seconds() > 3600:
        collect_tickets(page)
        return True
    return False
    