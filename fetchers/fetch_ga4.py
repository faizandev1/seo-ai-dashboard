import os
import json
from datetime import datetime, timedelta
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric, Dimension
from google.oauth2 import service_account
from dotenv import load_dotenv

load_dotenv()

SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY', 'service-account-key.json')
GA4_PROPERTY_ID = os.getenv('GA4_PROPERTY_ID')

def get_ga4_client():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=['https://www.googleapis.com/auth/analytics.readonly']
    )
    return BetaAnalyticsDataClient(credentials=credentials)

def fetch_ga4_data():
    print("Connecting to Google Analytics 4...")
    client = get_ga4_client()

    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    print(f"Fetching GA4 data from {start_date} to {end_date}")

    # Traffic by channel
    channel_response = client.run_report(RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimensions=[Dimension(name="sessionDefaultChannelGroup")],
        metrics=[
            Metric(name="sessions"),
            Metric(name="totalUsers"),
            Metric(name="bounceRate"),
            Metric(name="averageSessionDuration"),
        ]
    ))

    # Top pages
    pages_response = client.run_report(RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimensions=[Dimension(name="pagePath")],
        metrics=[
            Metric(name="sessions"),
            Metric(name="totalUsers"),
            Metric(name="bounceRate"),
            Metric(name="averageSessionDuration"),
        ]
    ))

    channels = []
    for row in channel_response.rows:
        channels.append({
            'channel': row.dimension_values[0].value,
            'sessions': row.metric_values[0].value,
            'users': row.metric_values[1].value,
            'bounce_rate': row.metric_values[2].value,
            'avg_session_duration': row.metric_values[3].value,
        })

    pages = []
    for row in pages_response.rows:
        pages.append({
            'page': row.dimension_values[0].value,
            'sessions': row.metric_values[0].value,
            'users': row.metric_values[1].value,
            'bounce_rate': row.metric_values[2].value,
            'avg_session_duration': row.metric_values[3].value,
        })

    os.makedirs('data/ga4', exist_ok=True)

    channel_data = {
        'fetched_at': datetime.now().isoformat(),
        'date_range': {'start': start_date, 'end': end_date},
        'channels': channels
    }
    pages_data = {
        'fetched_at': datetime.now().isoformat(),
        'date_range': {'start': start_date, 'end': end_date},
        'pages': pages
    }

    with open('data/ga4/channels.json', 'w') as f:
        json.dump(channel_data, f, indent=2)
    print(f"Saved {len(channels)} channels to data/ga4/channels.json")

    with open('data/ga4/pages.json', 'w') as f:
        json.dump(pages_data, f, indent=2)
    print(f"Saved {len(pages)} pages to data/ga4/pages.json")

    return channel_data, pages_data

if __name__ == "__main__":
    fetch_ga4_data()
