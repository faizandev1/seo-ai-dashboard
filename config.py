import os
from dotenv import load_dotenv

load_dotenv()

# Google Credentials
SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY', 'service-account-key.json')

# Search Console
GSC_PROPERTY_URL = os.getenv('GSC_PROPERTY_URL')

# Google Analytics 4
GA4_PROPERTY_ID = os.getenv('GA4_PROPERTY_ID')

# Google Ads (Optional)
GOOGLE_ADS_CUSTOMER_ID = os.getenv('GOOGLE_ADS_CUSTOMER_ID')

# Anthropic AI
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# Date Settings
DEFAULT_DATE_RANGE_DAYS = 90

# Data Paths
DATA_DIR = 'data'
REPORTS_DIR = 'reports'
GSC_DIR = f'{DATA_DIR}/gsc'
GA4_DIR = f'{DATA_DIR}/ga4'
ADS_DIR = f'{DATA_DIR}/ads'

# Fetch Settings
GSC_ROW_LIMIT = 1000
GA4_ROW_LIMIT = 1000

def validate_config():
    errors = []
    if not SERVICE_ACCOUNT_FILE:
        errors.append("GOOGLE_SERVICE_ACCOUNT_KEY missing in .env")
    if not GSC_PROPERTY_URL:
        errors.append("GSC_PROPERTY_URL missing in .env")
    if not GA4_PROPERTY_ID:
        errors.append("GA4_PROPERTY_ID missing in .env")
    if not ANTHROPIC_API_KEY:
        errors.append("ANTHROPIC_API_KEY missing in .env")
    if not os.path.exists(SERVICE_ACCOUNT_FILE or ''):
        errors.append(f"service-account-key.json not found in project folder")

    if errors:
        print("CONFIG ERRORS:")
        for e in errors:
            print(f"  - {e}")
        return False

    print("Config OK - All settings loaded!")
    return True

if __name__ == "__main__":
    validate_config()
