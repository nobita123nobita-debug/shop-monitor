#!/usr/bin/env python3
import schedule
import time
import subprocess
from datetime import datetime

def run_monitor():
    """Execute the shop monitor script."""
    print(f"Running monitor at {datetime.now().strftime('%H:%M:%S')}")
    subprocess.run(["python3", "shop_monitor.py"], check=False)

# Schedule monitoring at 20:00 and 20:01
schedule.every().day.at("20:00").do(run_monitor)
schedule.every().day.at("20:01").do(run_monitor)

print("Shop monitor scheduler started")
print("Scheduled checks: 20:00 and 20:01 daily")

while True:
    schedule.run_pending()
    time.sleep(60)
