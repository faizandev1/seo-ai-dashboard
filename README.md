# SEO AI Dashboard

Real-time SEO stats from Google Search Console + GA4 with AI analysis.

## SETUP (5 steps)

### Step 1 - Add your secret key file
Copy your Google service account JSON file into this folder.
Rename it to: service-account-key.json

### Step 2 - Create your .env file
Copy .env.example and rename to .env
Fill in your real values:
- GSC_PROPERTY_URL = your website URL exactly as shown in Search Console
- GA4_PROPERTY_ID = numbers only (e.g. 500557472)
- ANTHROPIC_API_KEY = get from console.anthropic.com

### Step 3 - Install dependencies
Open terminal in this folder and run:
pip install -r requirements.txt

### Step 4 - Fetch your data
python main.py

### Step 5 - Run the dashboard
python dashboard.py
Then open browser: http://localhost:5000

## DAILY USE

Fetch fresh data:
python main.py

Ask AI questions about your SEO:
python analyze.py

Auto-refresh every day at 8am:
python scheduler.py

## IMPORTANT - GSC Permission Fix
Make sure you added this email to your Search Console property:
Go to Search Console > Settings > Users and Permissions > Add User

## FILE STRUCTURE
service-account-key.json  <- YOUR SECRET KEY (never share)
.env                      <- YOUR SECRETS (never share)
main.py                   <- Fetches all data
dashboard.py              <- Visual dashboard
analyze.py                <- AI question engine
scheduler.py              <- Auto daily refresh
fetchers/
  fetch_gsc.py            <- Search Console fetcher
  fetch_ga4.py            <- GA4 fetcher
data/
  gsc/                    <- Keyword + page data
  ga4/                    <- Traffic data
reports/                  <- Saved AI analyses
