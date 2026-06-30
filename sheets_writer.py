"""
sheets_writer.py
Studio Kula — Automated Metrics Tool
US-09: Auto-Populate Monthly Reporting Spreadsheet

Author: An Nguyen (Intern)
Supervised by: Danielle Busko (CEO)

Usage:
    python sheets_writer.py
    python sheets_writer.py --start 2026-06-03 --end 2026-06-30

Requirements:
    pip install google-api-python-client google-auth python-dotenv

Note:
    Writes to a new 'Auto-Report' tab in Danielle's existing Google Sheet.
    Never overwrites existing tabs or prior period data.
    Requires Google Sheets API to be enabled on project 512540103005 (Danielle's project).
"""

import os
import argparse
from datetime import date, timedelta
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
SPREADSHEET_ID   = "1VEaVPUeipKQcDOUP5ewcPUVKWg57sfSHd6LXyIWI0TA"
SERVICE_ACCOUNT_FILE = os.getenv("GA4_SERVICE_ACCOUNT_FILE")
MOCK_MODE = not SERVICE_ACCOUNT_FILE or not os.path.exists(SERVICE_ACCOUNT_FILE or "")

# ─────────────────────────────────────────
# ARGUMENT PARSER
# ─────────────────────────────────────────
parser = argparse.ArgumentParser(description="Write metrics to Google Sheet")
parser.add_argument("--start", type=str, help="Start date YYYY-MM-DD")
parser.add_argument("--end",   type=str, help="End date YYYY-MM-DD")
args, _ = parser.parse_known_args()

end_date   = date.fromisoformat(args.end)   if args.end   else date.today()
start_date = date.fromisoformat(args.start) if args.start else end_date - timedelta(days=27)

PERIOD_LABEL = f"{start_date} to {end_date}"

# ─────────────────────────────────────────
# BUILD CREDENTIALS
# ─────────────────────────────────────────
def get_credentials():
    from google.oauth2 import service_account
    import streamlit as st

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/analytics.readonly",
    ]

    try:
        sa_info = dict(st.secrets["gcp_service_account"])
        return service_account.Credentials.from_service_account_info(sa_info, scopes=scopes)
    except Exception:
        pass

    if SERVICE_ACCOUNT_FILE and os.path.exists(SERVICE_ACCOUNT_FILE):
        return service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=scopes
        )
    return None

# ─────────────────────────────────────────
# PULL ALL PLATFORM DATA
# ─────────────────────────────────────────
def pull_all_metrics(start, end, creds):
    """Pull live data from all available platforms."""
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric

    results = {}

    # GA4 — CS.Us
    cs_property = os.getenv("GA4_PROPERTY_ID")
    if cs_property:
        try:
            client = BetaAnalyticsDataClient(credentials=creds)
            req = RunReportRequest(
                property=f"properties/{cs_property}",
                date_ranges=[DateRange(start_date=str(start), end_date=str(end))],
                metrics=[
                    Metric(name="sessions"), Metric(name="totalUsers"),
                    Metric(name="screenPageViews"), Metric(name="bounceRate"),
                    Metric(name="averageSessionDuration"),
                ],
            )
            resp = client.run_report(req)
            row = resp.rows[0].metric_values
            results["csus_ga4"] = {
                "Sessions":             row[0].value,
                "Unique Users":         row[1].value,
                "Pageviews":            row[2].value,
                "Bounce Rate":          f"{float(row[3].value) * 100:.2f}%",
                "Avg Session Duration": f"{float(row[4].value) / 60:.1f} min",
            }
        except Exception as e:
            results["csus_ga4"] = {"Error": str(e)}

    # GA4 — Studio Kula
    sk_property = os.getenv("GA4_PROPERTY_ID_SK")
    if sk_property:
        try:
            client = BetaAnalyticsDataClient(credentials=creds)
            req = RunReportRequest(
                property=f"properties/{sk_property}",
                date_ranges=[DateRange(start_date=str(start), end_date=str(end))],
                metrics=[
                    Metric(name="sessions"), Metric(name="totalUsers"),
                    Metric(name="screenPageViews"), Metric(name="bounceRate"),
                    Metric(name="averageSessionDuration"),
                ],
            )
            resp = client.run_report(req)
            row = resp.rows[0].metric_values
            results["sk_ga4"] = {
                "Sessions":             row[0].value,
                "Unique Users":         row[1].value,
                "Pageviews":            row[2].value,
                "Bounce Rate":          f"{float(row[3].value) * 100:.2f}%",
                "Avg Session Duration": f"{float(row[4].value) / 60:.1f} min",
            }
        except Exception as e:
            results["sk_ga4"] = {"Error": str(e)}

    # YouTube
    yt_key = os.getenv("YOUTUBE_API_KEY")
    yt_channel = os.getenv("YOUTUBE_CHANNEL_ID")
    if yt_key and yt_channel:
        try:
            from googleapiclient.discovery import build
            youtube = build("youtube", "v3", developerKey=yt_key)
            ch = youtube.channels().list(part="statistics", id=yt_channel).execute()
            stats = ch["items"][0]["statistics"]
            results["youtube"] = {
                "Subscribers":       stats.get("subscriberCount", "N/A"),
                "Total Views":       stats.get("viewCount", "N/A"),
                "Videos Published":  stats.get("videoCount", "N/A"),
            }
        except Exception as e:
            results["youtube"] = {"Error": str(e)}

    # LinkedIn, Instagram, Facebook — mock for now
    results["linkedin"]  = {"Status": "Mock mode — API approval pending"}
    results["instagram"] = {"Status": "Mock mode — Meta Developer access pending"}
    results["facebook"]  = {"Status": "Mock mode — Meta Developer access pending"}

    return results

# ─────────────────────────────────────────
# BUILD SHEET ROWS
# ─────────────────────────────────────────
def build_rows(data, period):
    rows = []

    # Header
    rows.append(["Studio Kula — Auto-Generated Metrics Report"])
    rows.append([f"Period: {period}"])
    rows.append([f"Generated: {date.today()}"])
    rows.append([])

    sections = {
        "csus_ga4":  "CS.Us Website — GA4 (US-01)",
        "sk_ga4":    "Studio Kula Website — GA4 (US-02)",
        "youtube":   "YouTube — Studio Kula Channel (US-06)",
        "linkedin":  "LinkedIn (US-05)",
        "instagram": "Instagram (US-03)",
        "facebook":  "Facebook (US-04)",
    }

    for key, label in sections.items():
        rows.append([label])
        rows.append(["Metric", "Value"])
        platform_data = data.get(key, {})
        for metric, value in platform_data.items():
            rows.append([metric, str(value)])
        rows.append([])

    return rows

# ─────────────────────────────────────────
# WRITE TO SHEET
# ─────────────────────────────────────────
def write_to_sheet(rows, creds):
    from googleapiclient.discovery import build

    service = build("sheets", "v4", credentials=creds)
    sheets  = service.spreadsheets()

    # Check if Auto-Report tab exists, create if not
    spreadsheet = sheets.get(spreadsheetId=SPREADSHEET_ID).execute()
    sheet_names = [s["properties"]["title"] for s in spreadsheet["sheets"]]

    if "Auto-Report" not in sheet_names:
        body = {"requests": [{"addSheet": {"properties": {"title": "Auto-Report"}}}]}
        sheets.batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()
        print("✅ Created new 'Auto-Report' tab")

    # Clear existing content and write fresh
    sheets.values().clear(
        spreadsheetId=SPREADSHEET_ID,
        range="Auto-Report!A1:Z1000"
    ).execute()

    sheets.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range="Auto-Report!A1",
        valueInputOption="RAW",
        body={"values": rows}
    ).execute()

    print(f"✅ Written {len(rows)} rows to Auto-Report tab")
    print(f"   Sheet: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}")

# ─────────────────────────────────────────
# MOCK PRINT
# ─────────────────────────────────────────
def print_mock(rows):
    print("\n⚠️  MOCK MODE — Google Sheets API not available. Showing what would be written:\n")
    for row in rows:
        if row:
            print("\t".join(str(c) for c in row))
        else:
            print()

# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
if __name__ == "__main__":
    print(f"\nRunning sheets writer for period: {start_date} → {end_date}")

    if MOCK_MODE:
        # Build mock data for preview
        mock_data = {
            "csus_ga4":  {"Sessions": "902", "Unique Users": "821", "Pageviews": "1124", "Bounce Rate": "77.16%", "Avg Session Duration": "1.2 min"},
            "sk_ga4":    {"Sessions": "5", "Unique Users": "5", "Pageviews": "5", "Bounce Rate": "100.00%", "Avg Session Duration": "0.0 min"},
            "youtube":   {"Subscribers": "584", "Total Views": "121,755", "Videos Published": "19"},
            "linkedin":  {"Status": "Mock mode — API approval pending"},
            "instagram": {"Status": "Mock mode — Meta Developer access pending"},
            "facebook":  {"Status": "Mock mode — Meta Developer access pending"},
        }
        rows = build_rows(mock_data, PERIOD_LABEL)
        print_mock(rows)
    else:
        try:
            creds = get_credentials()
            if not creds:
                print("[ERROR] Could not load credentials.")
            else:
                data = pull_all_metrics(start_date, end_date, creds)
                rows = build_rows(data, PERIOD_LABEL)
                write_to_sheet(rows, creds)
                print("\n✅ Report successfully written to Google Sheet!")
        except Exception as e:
            print(f"\n[ALERT] sheets_writer failed: {e}")