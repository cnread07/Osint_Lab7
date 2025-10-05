# run_scheduler.py
import schedule
import time
from main import run_pipeline

# Run once immediately
run_pipeline()

# Then schedule every hour (can set to every 30 minutes)
schedule.every(1).hours.do(run_pipeline)

print("Scheduler started. Press Ctrl+C to stop.")
while True:
    schedule.run_pending()
    time.sleep(10)
