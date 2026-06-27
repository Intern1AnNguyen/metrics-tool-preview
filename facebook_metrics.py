"""
facebook_metrics.py
Studio Kula — Automated Metrics Tool
US-04: Facebook Page Metrics — CS.Us Page

Author: An Nguyen (Intern)
Supervised by: Danielle Busko (CEO)

Usage:
    python facebook_metrics.py
    python facebook_metrics.py --start 2026-01-01 --end 2026-06-26

Requirements:
    pip install requests python-dotenv

Note:
    Requires Meta Graph API access via a Meta Developer App.
    App must be created under Danielle's account and a Page Access Token generated.
    Tokens expire every 60 days and must be refreshed.
    Built alongside US-03 (Instagram) — same Meta Graph API, separate permissions.
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
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
FB_PAGE_ID_CSUS   = os.getenv("FB_PAGE_ID_CSUS")   # CS.Us Facebook Page ID

MOCK_MODE = not META_ACCESS_TOKEN or not FB_PAGE_ID_CSUS

# ─────────────────────────────────────────
# ARGUMENT PARSER
# ─────────────────────────────────────────
parser = argparse.ArgumentParser(description="Pull Facebook page metrics via Meta Graph API")
parser.add_argument("--start", type=str, help="Start date YYYY-MM-DD")
parser.add_argument("--end",   type=str, help="End date YYYY-MM-DD")
args, _ = parser.parse_known_args()

end_date   = date.fromisoformat(args.end)   if args.end   else date.today()
start_date = date.fromisoformat(args.start) if args.start else end_date - timedelta(days=27)

# ─────────────────────────────────────────
# MOCK DATA
# ─────────────────────────────────────────
MOCK_DATA = {
    "page_name":       "Community, Serve Us",
    "page_likes":      111,
    "followers":       111,
    "new_likes":       3,
    "reach":           6210,
    "impressions":     15330,
    "post_engagements":743,
    "link_clicks":     73,
    "page_views":      284,
    "top_post_reach":  2840,
}

# ─────────────────────────────────────────
# PULL METRICS
# ─────────────────────────────────────────
def pull_metrics(start, end):
    if MOCK_MODE:
        print("\n⚠️  Running in MOCK MODE — Meta API credentials not configured.\n")
        return MOCK_DATA

    import requests

    base_url = "https://graph.facebook.com/v19.0"

    try:
        # Page basic info
        info_url = f"{base_url}/{FB_PAGE_ID_CSUS}?fields=name,fan_count,followers_count&access_token={META_ACCESS_TOKEN}"
        info_resp = requests.get(info_url)

        if info_resp.status_code != 200:
            print(f"\n[ALERT] Meta API error: {info_resp.status_code}")
            print(info_resp.json())
            return MOCK_DATA

        info = info_resp.json()

        # Page insights
        metrics = "page_impressions,page_reach,page_engaged_users,page_views_total"
        insights_url = (
            f"{base_url}/{FB_PAGE_ID_CSUS}/insights"
            f"?metric={metrics}"
            f"&period=day&since={start}&until={end}"
            f"&access_token={META_ACCESS_TOKEN}"
        )
        insights_resp = requests.get(insights_url)
        insights_data = insights_resp.json().get("data", [])

        impressions = reach = engaged_users = page_views = 0
        for metric in insights_data:
            total = sum(v["value"] for v in metric.get("values", []))
            if metric["name"] == "page_impressions":
                impressions = total
            elif metric["name"] == "page_reach":
                reach = total
            elif metric["name"] == "page_engaged_users":
                engaged_users = total
            elif metric["name"] == "page_views_total":
                page_views = total

        return {
            "page_name":       info.get("name", "CS.Us"),
            "page_likes":      info.get("fan_count", 0),
            "followers":       info.get("followers_count", 0),
            "new_likes":       "N/A",
            "reach":           reach,
            "impressions":     impressions,
            "post_engagements":engaged_users,
            "link_clicks":     "N/A",
            "page_views":      page_views,
            "top_post_reach":  "N/A",
        }

    except Exception as e:
        print(f"\n[ALERT] Facebook API call failed: {e}")
        print("Falling back to mock data.\n")
        return MOCK_DATA

# ─────────────────────────────────────────
# PRINT REPORT
# ─────────────────────────────────────────
def print_report(data, start, end):
    print("=" * 60)
    print("  STUDIO KULA — FACEBOOK METRICS REPORT")
    print(f"  Page: {data['page_name']}")
    print(f"  Period: {start} to {end}")
    print("  Source: Meta Graph API")
    print("=" * 60)
    print(f"  {'Page Likes:':<25} {data['page_likes']}")
    print(f"  {'Followers:':<25} {data['followers']}")
    print(f"  {'New Likes (28d):':<25} {data['new_likes']}")
    print(f"  {'Reach:':<25} {data['reach']}")
    print(f"  {'Impressions:':<25} {data['impressions']}")
    print(f"  {'Post Engagements:':<25} {data['post_engagements']}")
    print(f"  {'Link Clicks:':<25} {data['link_clicks']}")
    print(f"  {'Page Views:':<25} {data['page_views']}")
    print(f"  {'Top Post Reach:':<25} {data['top_post_reach']}")
    print("=" * 60)

# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
if __name__ == "__main__":
    data = pull_metrics(start_date, end_date)
    print_report(data, start_date, end_date)