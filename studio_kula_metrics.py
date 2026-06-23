"""
studio_kula_metrics.py
Studio Kula — Automated Metrics Tool
US-02: Google Analytics 4 (GA4) Data Pull — Studio Kula Website

Author: An Nguyen (Intern)
Supervised by: Danielle Busko (CEO)

Usage:
    python studio_kula_metrics.py
    python studio_kula_metrics.py --start 2026-01-01 --end 2026-06-12
"""

import os
import argparse
from datetime import date, timedelta
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
PROPERTY_ID = os.getenv("GA4_PROPERTY_ID_SK")
SERVICE_ACCOUNT_FILE = os.getenv("GA4_SERVICE_ACCOUNT_FILE")
MOCK_MODE = not PROPERTY_ID or not SERVICE_ACCOUNT_FILE

# ─────────────────────────────────────────
# ARGUMENT PARSER
# ─────────────────────────────────────────
parser = argparse.ArgumentParser(description="Pull Studio Kula GA4 metrics")
parser.add_argument("--start", type=str, help="Start date YYYY-MM-DD")
parser.add_argument("--end", type=str, help="End date YYYY-MM-DD")
args = parser.parse_args()

end_date = date.fromisoformat(args.end) if args.end else date.today()
start_date = date.fromisoformat(args.start) if args.start else end_date - timedelta(days=27)

# ─────────────────────────────────────────
# MOCK DATA
# ─────────────────────────────────────────
MOCK_DATA = {
    "total_visits": 200,
    "unique_visitors": 198,
    "pageviews": 243,
    "bounce_rate": "93.3%",
    "avg_session_duration": "4m 38s",
}

# ─────────────────────────────────────────
# PULL DATA
# ─────────────────────────────────────────
def pull_metrics(start, end):
    if MOCK_MODE:
        print("\n⚠️  Running in MOCK MODE — no credentials found for Studio Kula GA4.\n")
        return MOCK_DATA

    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import (
        RunReportRequest, DateRange, Metric
    )
    from google.oauth2 import service_account

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/analytics.readonly"]
    )
    client = BetaAnalyticsDataClient(credentials=credentials)

    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        date_ranges=[DateRange(start_date=str(start), end_date=str(end))],
        metrics=[
            Metric(name="sessions"),
            Metric(name="totalUsers"),
            Metric(name="screenPageViews"),
            Metric(name="bounceRate"),
            Metric(name="averageSessionDuration"),
        ]
    )

    response = client.run_report(request)
    row = response.rows[0].metric_values

    return {
        "total_visits": row[0].value,
        "unique_visitors": row[1].value,
        "pageviews": row[2].value,
        "bounce_rate": f"{float(row[3].value) * 100:.2f}%",
        "avg_session_duration": f"{float(row[4].value) / 60:.1f} min",
    }

# ─────────────────────────────────────────
# PRINT REPORT
# ─────────────────────────────────────────
def print_report(data, start, end):
    print("=" * 50)
    print("  STUDIO KULA — GA4 METRICS REPORT")
    print(f"  Period: {start} to {end}")
    print("=" * 50)
    print(f"  Total Visits:          {data['total_visits']}")
    print(f"  Unique Visitors:       {data['unique_visitors']}")
    print(f"  Pageviews:             {data['pageviews']}")
    print(f"  Bounce Rate:           {data['bounce_rate']}")
    print(f"  Avg Session Duration:  {data['avg_session_duration']}")
    print("=" * 50)

# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
if __name__ == "__main__":
    data = pull_metrics(start_date, end_date)
    print_report(data, start_date, end_date)