"""
youtube_metrics.py
Studio Kula — Automated Metrics Tool
US-06: YouTube Channel Metrics

Author: An Nguyen (Intern)
Supervised by: Danielle Busko (CEO)

Usage:
    python youtube_metrics.py
    python youtube_metrics.py --start 2026-01-01 --end 2026-06-22

Requirements:
    pip install google-api-python-client python-dotenv
"""

import os
import argparse
from datetime import date, timedelta
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
API_KEY    = os.getenv("YOUTUBE_API_KEY")
CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")
MOCK_MODE  = not API_KEY or not CHANNEL_ID

# ─────────────────────────────────────────
# ARGUMENT PARSER
# ─────────────────────────────────────────
parser = argparse.ArgumentParser(description="Pull Studio Kula YouTube metrics")
parser.add_argument("--start", type=str, help="Start date YYYY-MM-DD")
parser.add_argument("--end",   type=str, help="End date YYYY-MM-DD")
args, _ = parser.parse_known_args()

end_date   = date.fromisoformat(args.end)   if args.end   else date.today()
start_date = date.fromisoformat(args.start) if args.start else end_date - timedelta(days=27)

# ─────────────────────────────────────────
# MOCK DATA
# ─────────────────────────────────────────
MOCK_DATA = {
    "channel_name":        "Studio Kula",
    "subscribers":         "1,204",
    "total_views":         "18,432",
    "watch_time_hours":    "941",
    "avg_view_duration":   "3m 52s",
    "videos_published":    3,
    "top_videos": [
        {"title": "Community Storytelling Workshop Recap", "views": "2,318"},
        {"title": "Mental Health Awareness Panel",         "views": "1,874"},
        {"title": "CS.Us Platform Demo",                  "views": "1,203"},
        {"title": "Founder Interview — Season 2",         "views": "987"},
        {"title": "Behind the Scenes: Studio Kula",       "views": "743"},
    ]
}

# ─────────────────────────────────────────
# PULL METRICS
# ─────────────────────────────────────────
def pull_metrics(start, end):
    if MOCK_MODE:
        print("\n⚠️  Running in MOCK MODE — no credentials found for YouTube.\n")
        return MOCK_DATA

    try:
        from googleapiclient.discovery import build
    except ImportError:
        print("\n[ERROR] Required package not installed.")
        print("Run: pip install google-api-python-client\n")
        return MOCK_DATA

    try:
        youtube = build("youtube", "v3", developerKey=API_KEY)

        # Channel stats
        channel_response = youtube.channels().list(
            part="snippet,statistics",
            id=CHANNEL_ID
        ).execute()

        if not channel_response.get("items"):
            print("\n[ALERT] No channel data returned. Check YOUTUBE_CHANNEL_ID.")
            return MOCK_DATA

        channel = channel_response["items"][0]
        stats   = channel["statistics"]
        name    = channel["snippet"]["title"]

        subscribers = int(stats.get("subscriberCount", 0))
        total_views = int(stats.get("viewCount", 0))
        video_count = int(stats.get("videoCount", 0))

        # Top 5 videos by view count
        search_response = youtube.search().list(
            part="snippet",
            channelId=CHANNEL_ID,
            order="viewCount",
            type="video",
            maxResults=5,
            publishedAfter=f"{start}T00:00:00Z",
            publishedBefore=f"{end}T23:59:59Z",
        ).execute()

        top_videos = []
        for item in search_response.get("items", []):
            video_id = item["id"]["videoId"]
            title    = item["snippet"]["title"]

            # Get view count for each video
            vid_stats = youtube.videos().list(
                part="statistics",
                id=video_id
            ).execute()

            views = "N/A"
            if vid_stats.get("items"):
                views = f"{int(vid_stats['items'][0]['statistics'].get('viewCount', 0)):,}"

            top_videos.append({"title": title, "views": views})

        return {
            "channel_name":      name,
            "subscribers":       f"{subscribers:,}",
            "total_views":       f"{total_views:,}",
            "watch_time_hours":  "N/A (requires YouTube Analytics API OAuth)",
            "avg_view_duration": "N/A (requires YouTube Analytics API OAuth)",
            "videos_published":  video_count,
            "top_videos":        top_videos,
        }

    except Exception as e:
        print(f"\n[ALERT] YouTube API call failed: {e}")
        print("Falling back to mock data.\n")
        return MOCK_DATA

# ─────────────────────────────────────────
# PRINT REPORT
# ─────────────────────────────────────────
def print_report(data, start, end):
    print("=" * 55)
    print(f"  STUDIO KULA — YOUTUBE METRICS REPORT")
    print(f"  Channel: {data['channel_name']}")
    print(f"  Period:  {start} to {end}")
    print("=" * 55)
    print(f"  Subscribers:         {data['subscribers']}")
    print(f"  Total Views:         {data['total_views']}")
    print(f"  Watch Time (hrs):    {data['watch_time_hours']}")
    print(f"  Avg View Duration:   {data['avg_view_duration']}")
    print(f"  Videos Published:    {data['videos_published']}")
    print("-" * 55)
    print("  Top 5 Videos by Views:")
    for i, v in enumerate(data["top_videos"], 1):
        title = v["title"][:40] + "..." if len(v["title"]) > 40 else v["title"]
        print(f"  {i}. {title:<43} {v['views']:>8}")
    print("=" * 55)

# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
if __name__ == "__main__":
    data = pull_metrics(start_date, end_date)
    print_report(data, start_date, end_date)