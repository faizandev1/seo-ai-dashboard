import os
import json
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY', 'service-account-key.json')
GSC_PROPERTY_URL = os.getenv('GSC_PROPERTY_URL')
SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']

def get_gsc_service():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build('searchconsole', 'v1', credentials=credentials)

def fetch_gsc_data():
    print("Connecting to Google Search Console...")

    # Auto-detect correct property URL format
    service = get_gsc_service()
    sites = service.sites().list().execute()
    available = [s['siteUrl'] for s in sites.get('siteEntry', [])]

    if not available:
        print("ERROR: No sites found. Make sure service account was added to GSC.")
        return None, None

    print(f"Available GSC properties: {available}")

    # Use configured URL or auto-pick first available
    site_url = GSC_PROPERTY_URL
    if site_url not in available:
        # Try variations
        variations = [
            site_url,
            site_url.replace('http://', 'https://'),
            site_url.replace('https://', 'http://'),
            site_url.rstrip('/'),
            site_url.rstrip('/') + '/',
        ]
        for v in variations:
            if v in available:
                site_url = v
                print(f"Auto-corrected property URL to: {site_url}")
                break
        else:
            # Use first available
            site_url = available[0]
            print(f"Using first available property: {site_url}")

    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    print(f"Fetching data from {start_date} to {end_date}")

    # Fetch queries
    queries_response = service.searchanalytics().query(
        siteUrl=site_url,
        body={
            'startDate': start_date,
            'endDate': end_date,
            'dimensions': ['query'],
            'rowLimit': 1000
        }
    ).execute()

    # Fetch pages
    pages_response = service.searchanalytics().query(
        siteUrl=site_url,
        body={
            'startDate': start_date,
            'endDate': end_date,
            'dimensions': ['page'],
            'rowLimit': 1000
        }
    ).execute()

    queries_data = {
        'fetched_at': datetime.now().isoformat(),
        'site': site_url,
        'date_range': {'start': start_date, 'end': end_date},
        'queries': queries_response.get('rows', [])
    }

    pages_data = {
        'fetched_at': datetime.now().isoformat(),
        'site': site_url,
        'date_range': {'start': start_date, 'end': end_date},
        'pages': pages_response.get('rows', [])
    }

    os.makedirs('data/gsc', exist_ok=True)

    with open('data/gsc/queries.json', 'w') as f:
        json.dump(queries_data, f, indent=2)
    print(f"Saved {len(queries_data['queries'])} queries to data/gsc/queries.json")

    with open('data/gsc/pages.json', 'w') as f:
        json.dump(pages_data, f, indent=2)
    print(f"Saved {len(pages_data['pages'])} pages to data/gsc/pages.json")

    return queries_data, pages_data

if __name__ == "__main__":
    fetch_gsc_data()
