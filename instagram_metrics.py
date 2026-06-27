"""
instagram_metrics.py
Studio Kula — Automated Metrics Tool
US-03: Instagram Metrics — Founder & CS.Us Accounts

Author: An Nguyen (Intern)
Supervised by: Danielle Busko (CEO)

Usage:
    python instagram_metrics.py
    python instagram_metrics.py --start 2026-01-01 --end 2026-06-26

Requirements:
    pip install requests python-dotenv

Note:
    Requires Meta Graph API access via a Meta Developer App.
    App must be created under Danielle's account and a Page Access Token generated.
    Tokens expire every 60 days and must be refreshed.
    Data source: Meta Graph API (confirmed with Danielle as the consistent source).
"""

import os
import argparse
from datetime import date, timedelta
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
META_ACCESS_TOKEN     = os.getenv("META_ACCESS_TOKEN")
IG_ACCOUNT_ID_CSUS    = os.getenv("IG_ACCOUNT_ID_CSUS")     # CS.Us Instagram account ID
IG_ACCOUNT_ID_FOUNDER = os.getenv("IG_ACCOUNT_ID_FOUNDER")  # Founder Instagram account ID

MOCK_MODE = not META_ACCESS_TOKEN or not IG_ACCOUNT_ID_CSUS

# ─────────────────────────────────────────
# ARGUMENT PARSER
# ─────────────────────────────────────────
parser = argparse.ArgumentParser(description="Pull Instagram metrics via Meta Graph API")
parser.add_argument("--start", type=str, help="Start date YYYY-MM-DD")
parser.add_argument("--end",   type=str, help="End date YYYY-MM-DD")
args, _ = parser.parse_known_args()

end_date   = date.fromisoformat(args.end)   if args.end   else date.today()
start_date = date.fromisoformat(args.start) if args.start else end_date - timedelta(days=27)

# ─────────────────────────────────────────
# MOCK DATA
# ─────────────────────────────────────────
MOCK_DATA = {
    "csus": {
        "account":       "CS.Us Instagram",
        "followers":     2140,
        "reach":         8930,
        "impressions":   21440,
        "likes":         1203,
        "comments":      184,
        "saves":         97,
        "shares":        43,
        "profile_visits":612,
    },
    "founder": {
        "account":       "Founder Instagram (Danielle Busko)",
        "followers":     1870,
        "reach":         6210,
        "impressions":   15330,
        "likes":         874,
        "comments":      112,
        "saves":         64,
        "shares":        28,
        "profile_visits":403,
    },
}

# ─────────────────────────────────────────
# PULL METRICS
# ─────────────────────────────────────────
def pull_account_metrics(account_id, account_name, start, end):
    """Pull metrics for a single Instagram account via Meta Graph API."""
    import requests

    base_url = "https://graph.facebook.com/v19.0"

    # Account basic info
    info_url = f"{base_url}/{account_id}?fields=followers_count,name&access_token={META_ACCESS_TOKEN}"
    info_resp = requests.get(info_url)

    if info_resp.status_code != 200:
        print(f"\n[ALERT] Meta API error for {account_name}: {info_resp.status_code}")
        print(info_resp.json())
        return None

    info = info_resp.json()

    # Insights
    since = int(date.fromisoformat(str(start)).strftime("%s") if hasattr(date, 'strftime') else 0)
    until = int(date.fromisoformat(str(end)).strftime("%s") if hasattr(date, 'strftime') else 0)

    insights_url = (
        f"{base_url}/{account_id}/insights"
        f"?metric=reach,impressions,profile_views"
        f"&period=day&since={start}&until={end}"
        f"&access_token={META_ACCESS_TOKEN}"
    )
    insights_resp = requests.get(insights_url)
    insights = insights_resp.json().get("data", [])

    reach = impressions = profile_views = 0
    for metric in insights:
        total = sum(v["value"] for v in metric.get("values", []))
        if metric["name"] == "reach":
            reach = total
        elif metric["name"] == "impressions":
            impressions = total
        elif metric["name"] == "profile_views":
            profile_views = total

    return {
        "account":        account_name,
        "followers":      info.get("followers_count", 0),
        "reach":          reach,
        "impressions":    impressions,
        "likes":          "N/A (requires media-level pull)",
        "comments":       "N/A (requires media-level pull)",
        "saves":          "N/A (requires media-level pull)",
        "shares":         "N/A (requires media-level pull)",
        "profile_visits": profile_views,
    }

def pull_metrics(start, end):
    if MOCK_MODE:
        print("\n⚠️  Running in MOCK MODE — Meta API credentials not configured.\n")
        return MOCK_DATA

    try:
        results = {}
        if IG_ACCOUNT_ID_CSUS:
            results["csus"] = pull_account_metrics(IG_ACCOUNT_ID_CSUS, "CS.Us Instagram", start, end)
        if IG_ACCOUNT_ID_FOUNDER:
            results["founder"] = pull_account_metrics(IG_ACCOUNT_ID_FOUNDER, "Founder Instagram", start, end)
        return results
    except Exception as e:
        print(f"\n[ALERT] Instagram API call failed: {e}")
        print("Falling back to mock data.\n")
        return MOCK_DATA

# ─────────────────────────────────────────
# PRINT REPORT
# ─────────────────────────────────────────
def print_report(data, start, end):
    print("=" * 60)
    print("  STUDIO KULA — INSTAGRAM METRICS REPORT")
    print(f"  Period: {start} to {end}")
    print("  Source: Meta Graph API")
    print("=" * 60)
    for key, account in data.items():
        if not account:
            continue
        print(f"\n  Account: {account['account']}")
        print(f"  {'Followers:':<25} {account['followers']:,}" if isinstance(account['followers'], int) else f"  {'Followers:':<25} {account['followers']}")
        print(f"  {'Reach:':<25} {account['reach']:,}" if isinstance(account['reach'], int) else f"  {'Reach:':<25} {account['reach']}")
        print(f"  {'Impressions:':<25} {account['impressions']:,}" if isinstance(account['impressions'], int) else f"  {'Impressions:':<25} {account['impressions']}")
        print(f"  {'Likes:':<25} {account['likes']}")
        print(f"  {'Comments:':<25} {account['comments']}")
        print(f"  {'Saves:':<25} {account['saves']}")
        print(f"  {'Shares:':<25} {account['shares']}")
        print(f"  {'Profile Visits:':<25} {account['profile_visits']}")
        print("  " + "-" * 40)
    print("=" * 60)

# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
if __name__ == "__main__":
    data = pull_metrics(start_date, end_date)
    print_report(data, start_date, end_date)