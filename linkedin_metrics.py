"""
linkedin_metrics.py
Studio Kula — Automated Metrics Tool
US-05: LinkedIn Page Metrics — Founder, CS.Us & Studio Kula

Author: An Nguyen (Intern)
Supervised by: Danielle Busko (CEO)

Usage:
    python linkedin_metrics.py
    python linkedin_metrics.py --start 2026-01-01 --end 2026-06-26

Requirements:
    pip install requests python-dotenv

Note:
    LinkedIn page analytics require the Community Management API product.
    This product requires LinkedIn's manual approval before live data can be pulled.
    Script runs in mock mode until approval is granted and credentials are configured.
"""

import os
import argparse
from datetime import date, timedelta
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
CLIENT_ID     = os.getenv("LINKEDIN_CLIENT_ID")
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
ACCESS_TOKEN  = os.getenv("LINKEDIN_ACCESS_TOKEN")  # set after OAuth flow

# Organization IDs (URNs) — fill in once access is granted
ORG_ID_CSUS = os.getenv("LINKEDIN_ORG_ID_CSUS")       # Community, Serve Us
ORG_ID_SK   = os.getenv("LINKEDIN_ORG_ID_SK")         # Studio Kula
ORG_ID_FOUNDER = os.getenv("LINKEDIN_ORG_ID_FOUNDER") # Founder (Danielle) — TBD

MOCK_MODE = not ACCESS_TOKEN or not ORG_ID_CSUS

# ─────────────────────────────────────────
# ARGUMENT PARSER
# ─────────────────────────────────────────
parser = argparse.ArgumentParser(description="Pull LinkedIn page metrics")
parser.add_argument("--start", type=str, help="Start date YYYY-MM-DD")
parser.add_argument("--end",   type=str, help="End date YYYY-MM-DD")
args, _ = parser.parse_known_args()

end_date   = date.fromisoformat(args.end)   if args.end   else date.today()
start_date = date.fromisoformat(args.start) if args.start else end_date - timedelta(days=27)

# ─────────────────────────────────────────
# MOCK DATA — all 3 accounts
# ─────────────────────────────────────────
MOCK_DATA = {
    "csus": {
        "account":        "Community, Serve Us",
        "followers":      54,
        "new_followers":  2,
        "impressions":    1240,
        "clicks":         38,
        "engagement_rate":"3.1%",
        "top_post_impressions": 412,
    },
    "studio_kula": {
        "account":        "Studio Kula",
        "followers":      210,
        "new_followers":  7,
        "impressions":    3840,
        "clicks":         112,
        "engagement_rate":"4.2%",
        "top_post_impressions": 987,
    },
    "founder": {
        "account":        "Danielle Busko (Founder)",
        "followers":      890,
        "new_followers":  14,
        "impressions":    6200,
        "clicks":         203,
        "engagement_rate":"5.8%",
        "top_post_impressions": 1834,
    },
}

# ─────────────────────────────────────────
# PULL METRICS
# ─────────────────────────────────────────
def pull_org_metrics(org_id, account_name, start, end):
    """Pull metrics for a single LinkedIn organization page."""
    import requests

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "LinkedIn-Version": "202401",
    }

    # Convert dates to timestamps (milliseconds)
    start_ts = int(date.fromisoformat(str(start)).strftime("%s")) * 1000 if hasattr(date.fromisoformat(str(start)), 'strftime') else 0

    # Follower stats
    follower_url = f"https://api.linkedin.com/v2/organizationalEntityFollowerStatistics?q=organizationalEntity&organizationalEntity=urn:li:organization:{org_id}"
    follower_resp = requests.get(follower_url, headers=headers)

    # Page statistics
    stats_url = f"https://api.linkedin.com/v2/organizationPageStatistics?q=organization&organization=urn:li:organization:{org_id}"
    stats_resp = requests.get(stats_url, headers=headers)

    if follower_resp.status_code != 200 or stats_resp.status_code != 200:
        print(f"\n[ALERT] LinkedIn API error for {account_name}: {follower_resp.status_code}")
        return None

    follower_data = follower_resp.json()
    stats_data    = stats_resp.json()

    total_followers = follower_data.get("elements", [{}])[0].get("totalFollowerCounts", {}).get("organicFollowerCount", 0)
    page_views      = stats_data.get("elements", [{}])[0].get("totalPageStatistics", {}).get("views", {}).get("allPageViews", {}).get("pageViews", 0)

    return {
        "account":        account_name,
        "followers":      total_followers,
        "new_followers":  "N/A",
        "impressions":    page_views,
        "clicks":         "N/A",
        "engagement_rate":"N/A",
        "top_post_impressions": "N/A",
    }

def pull_metrics(start, end):
    if MOCK_MODE:
        print("\n⚠️  Running in MOCK MODE — LinkedIn Community Management API pending approval.\n")
        return MOCK_DATA

    try:
        results = {}
        if ORG_ID_CSUS:
            results["csus"] = pull_org_metrics(ORG_ID_CSUS, "Community, Serve Us", start, end)
        if ORG_ID_SK:
            results["studio_kula"] = pull_org_metrics(ORG_ID_SK, "Studio Kula", start, end)
        if ORG_ID_FOUNDER:
            results["founder"] = pull_org_metrics(ORG_ID_FOUNDER, "Danielle Busko (Founder)", start, end)
        return results
    except Exception as e:
        print(f"\n[ALERT] LinkedIn API call failed: {e}")
        print("Falling back to mock data.\n")
        return MOCK_DATA

# ─────────────────────────────────────────
# PRINT REPORT
# ─────────────────────────────────────────
def print_report(data, start, end):
    print("=" * 60)
    print("  STUDIO KULA — LINKEDIN METRICS REPORT")
    print(f"  Period: {start} to {end}")
    print("=" * 60)
    for key, account in data.items():
        if not account:
            continue
        print(f"\n  Account: {account['account']}")
        print(f"  {'Followers:':<25} {account['followers']}")
        print(f"  {'New Followers (28d):':<25} {account['new_followers']}")
        print(f"  {'Impressions:':<25} {account['impressions']}")
        print(f"  {'Clicks:':<25} {account['clicks']}")
        print(f"  {'Engagement Rate:':<25} {account['engagement_rate']}")
        print(f"  {'Top Post Impressions:':<25} {account['top_post_impressions']}")
        print("  " + "-" * 40)
    print("=" * 60)

# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
if __name__ == "__main__":
    data = pull_metrics(start_date, end_date)
    print_report(data, start_date, end_date)