"""
ga4_metrics.py
Studio Kula — Automated Metrics Tool
US-01: Google Analytics 4 (GA4) Data Pull

Author: An Nguyen (Intern)
Supervised by: Danielle Busko (CEO)

Usage:
    python ga4_metrics.py
    python ga4_metrics.py --start 2026-01-01 --end 2026-06-10

Requirements:
    pip install google-analytics-data python-dotenv
"""

import os
import argparse
from datetime import date, timedelta
from dotenv import load_dotenv

# Load credentials from .env file
load_dotenv()

# ─────────────────────────────────────────────
# CONFIGURATION — filled via .env file
# ─────────────────────────────────────────────
PROPERTY_ID = os.getenv("GA4_PROPERTY_ID", "YOUR_PROPERTY_ID_HERE")
SERVICE_ACCOUNT_FILE = os.getenv("GA4_SERVICE_ACCOUNT_FILE", "service_account.json")


def run_report(start_date: str, end_date: str):
    """
    Pull core metrics from GA4 for the given date range.
    Metrics: sessions, total users, pageviews, bounce rate, avg session duration
    """
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import (
            DateRange,
            Dimension,
            Metric,
            RunReportRequest,
        )
        from google.oauth2 import service_account
    except ImportError:
        print("\n[ERROR] Required packages not installed.")
        print("Run: pip install google-analytics-data google-auth python-dotenv\n")
        return

    # Validate credentials exist
    if PROPERTY_ID == "YOUR_PROPERTY_ID_HERE":
        print("\n[WARNING] GA4_PROPERTY_ID not set in .env file.")
        print("Add your Property ID to the .env file and re-run.\n")
        _print_mock_report(start_date, end_date)
        return

    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"\n[WARNING] Service account file not found: {SERVICE_ACCOUNT_FILE}")
        print("Add your service_account.json file and re-run.\n")
        _print_mock_report(start_date, end_date)
        return

    # Authenticate
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/analytics.readonly"],
    )
    client = BetaAnalyticsDataClient(credentials=credentials)

    # Build request
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[
            Dimension(name="date"),
        ],
        metrics=[
            Metric(name="sessions"),
            Metric(name="totalUsers"),
            Metric(name="screenPageViews"),
            Metric(name="bounceRate"),
            Metric(name="averageSessionDuration"),
        ],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        order_bys=[{"dimension": {"dimension_name": "date"}}],
    )

    # Run report
    try:
        response = client.run_report(request)
    except Exception as e:
        print(f"\n[ALERT] GA4 API call failed: {e}")
        print("Check: service account permissions, property ID, and network connection.")
        print("Falling back to mock data.\n")
        _print_mock_report(start_date, end_date)
        return

    # Check for empty response
    if not response.rows:
        print("\n[ALERT] GA4 returned no data for this date range.")
        print("Check: date range, property ID, and whether the site has traffic.")
        _print_mock_report(start_date, end_date)
        return

    # Print results
    _print_report(response, start_date, end_date)


def _print_report(response, start_date, end_date):
    """Format and print the GA4 report to terminal."""
    print("\n" + "═" * 60)
    print("  STUDIO KULA — GA4 METRICS REPORT")
    print(f"  Period: {start_date} → {end_date}")
    print("═" * 60)

    # Aggregate totals
    total_sessions = 0
    total_users = 0
    total_pageviews = 0
    bounce_rates = []
    session_durations = []

    for row in response.rows:
        total_sessions += int(row.metric_values[0].value)
        total_users += int(row.metric_values[1].value)
        total_pageviews += int(row.metric_values[2].value)
        bounce_rates.append(float(row.metric_values[3].value))
        session_durations.append(float(row.metric_values[4].value))

    avg_bounce = sum(bounce_rates) / len(bounce_rates) if bounce_rates else 0
    avg_duration = sum(session_durations) / len(session_durations) if session_durations else 0
    avg_duration_fmt = f"{int(avg_duration // 60)}m {int(avg_duration % 60)}s"

    print(f"\n  {'Metric':<30} {'Value':>15}")
    print("  " + "-" * 45)
    print(f"  {'Total Sessions':<30} {total_sessions:>15,}")
    print(f"  {'Total Users':<30} {total_users:>15,}")
    print(f"  {'Total Pageviews':<30} {total_pageviews:>15,}")
    print(f"  {'Avg Bounce Rate':<30} {avg_bounce:>14.1%}")
    print(f"  {'Avg Session Duration':<30} {avg_duration_fmt:>15}")
    print("  " + "-" * 45)
    print(f"\n  {len(response.rows)} days of data returned.")
    print("═" * 60 + "\n")


def _print_mock_report(start_date, end_date):
    """
    Print a mock report to demonstrate output format.
    Runs when credentials are not yet configured.
    """
    print("\n" + "═" * 60)
    print("  STUDIO KULA — GA4 METRICS REPORT (MOCK DATA)")
    print(f"  Period: {start_date} → {end_date}")
    print("  [Credentials not configured — showing sample output]")
    print("═" * 60)
    print(f"\n  {'Metric':<30} {'Value':>15}")
    print("  " + "-" * 45)
    print(f"  {'Total Sessions':<30} {'1,284':>15}")
    print(f"  {'Total Users':<30} {'976':>15}")
    print(f"  {'Total Pageviews':<30} {'3,541':>15}")
    print(f"  {'Avg Bounce Rate':<30} {'42.3%':>15}")
    print(f"  {'Avg Session Duration':<30} {'2m 14s':>15}")
    print("  " + "-" * 45)
    print("\n  Script is ready. Add credentials to .env to pull live data.")
    print("═" * 60 + "\n")


def parse_args():
    today = date.today()
    thirty_days_ago = today - timedelta(days=30)

    parser = argparse.ArgumentParser(
        description="Pull GA4 metrics for Studio Kula / CS.Us"
    )
    parser.add_argument(
        "--start",
        default=str(thirty_days_ago),
        help=f"Start date (YYYY-MM-DD). Default: {thirty_days_ago}",
    )
    parser.add_argument(
        "--end",
        default=str(today),
        help=f"End date (YYYY-MM-DD). Default: {today}",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(f"\nRunning GA4 report: {args.start} → {args.end}")
    run_report(args.start, args.end)