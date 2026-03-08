import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def run_all_fetchers():
    print("=" * 50)
    print("SEO AI DASHBOARD - STARTING DATA FETCH")
    print("=" * 50)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Site: {os.getenv('GSC_PROPERTY_URL')}")
    print("=" * 50)

    # Run GSC
    print("\n[1/2] Fetching Search Console Data...")
    try:
        from fetchers.fetch_gsc import fetch_gsc_data
        gsc_queries, gsc_pages = fetch_gsc_data()
        gsc_ok = gsc_queries is not None
    except Exception as e:
        print(f"GSC Error: {e}")
        gsc_ok = False
        gsc_queries = {'queries': []}
        gsc_pages = {'pages': []}

    # Run GA4
    print("\n[2/2] Fetching Google Analytics Data...")
    try:
        from fetchers.fetch_ga4 import fetch_ga4_data
        ga4_channels, ga4_pages = fetch_ga4_data()
        ga4_ok = ga4_channels is not None
    except Exception as e:
        print(f"GA4 Error: {e}")
        ga4_ok = False
        ga4_channels = {'channels': []}
        ga4_pages = {'pages': []}

    print("\n" + "=" * 50)
    print("FETCH COMPLETE - SUMMARY")
    print("=" * 50)
    if gsc_ok:
        print(f"GSC Queries : {len(gsc_queries.get('queries', []))}")
        print(f"GSC Pages   : {len(gsc_pages.get('pages', []))}")
    else:
        print("GSC         : FAILED - check permissions")
    if ga4_ok:
        print(f"GA4 Channels: {len(ga4_channels.get('channels', []))}")
        print(f"GA4 Pages   : {len(ga4_pages.get('pages', []))}")
    else:
        print("GA4         : FAILED - check permissions")
    print("=" * 50)
    print("All data saved in /data folder")
    print("Now run: python dashboard.py")

if __name__ == "__main__":
    run_all_fetchers()
