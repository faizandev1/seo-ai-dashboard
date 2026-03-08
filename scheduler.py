import schedule
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def run_fetch():
    print("\n" + "=" * 50)
    print(f"AUTO FETCH: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    try:
        from fetchers.fetch_gsc import fetch_gsc_data
        fetch_gsc_data()
    except Exception as e:
        print(f"GSC Error: {e}")
    try:
        from fetchers.fetch_ga4 import fetch_ga4_data
        fetch_ga4_data()
    except Exception as e:
        print(f"GA4 Error: {e}")
    print(f"Auto fetch complete: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Run every day at 8:00 AM
schedule.every().day.at("08:00").do(run_fetch)

print("=" * 50)
print("SEO AUTO SCHEDULER RUNNING")
print("Fetches fresh data every day at 08:00 AM")
print("Press Ctrl+C to stop")
print("=" * 50)

# Run once immediately
run_fetch()

while True:
    schedule.run_pending()
    time.sleep(60)
