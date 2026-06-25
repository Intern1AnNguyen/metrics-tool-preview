"""
dashboard.py
Studio Kula — Automated Metrics Tool
All-platform metrics dashboard (mock mode for unconnected platforms)

Author: An Nguyen (Intern)
Supervised by: Danielle Busko (CEO)

Usage:
    Local:  python -m streamlit run dashboard.py
    Cloud:  Deployed via Streamlit Community Cloud
"""

import os
import json
import argparse
from datetime import date, timedelta
from dotenv import load_dotenv
import streamlit as st

# ─────────────────────────────────────────
# PAGE CONFIG (must be first Streamlit call)
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Studio Kula — Metrics Dashboard",
    page_icon="📊",
    layout="wide",
)

load_dotenv()

# ─────────────────────────────────────────
# CREDENTIALS — Streamlit secrets (cloud)
# with .env fallback (local)
# ─────────────────────────────────────────
def get_secret(key, fallback_env=None):
    """Read from Streamlit secrets first, fall back to env var."""
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(fallback_env or key)

CS_PROPERTY_ID = get_secret("GA4_PROPERTY_ID")
SK_PROPERTY_ID = get_secret("GA4_PROPERTY_ID_SK")
YT_API_KEY     = get_secret("YOUTUBE_API_KEY")
YT_CHANNEL_ID  = get_secret("YOUTUBE_CHANNEL_ID")

# Service account — from Streamlit secrets (cloud) or JSON file (local)
def get_ga4_credentials():
    """Build GA4 credentials from Streamlit secrets or local JSON file."""
    from google.oauth2 import service_account

    # Try Streamlit secrets first (cloud deployment)
    try:
        sa_info = dict(st.secrets["gcp_service_account"])
        return service_account.Credentials.from_service_account_info(
            sa_info,
            scopes=["https://www.googleapis.com/auth/analytics.readonly"],
        )
    except Exception:
        pass

    # Fall back to local JSON file
    sa_file = os.getenv("GA4_SERVICE_ACCOUNT_FILE", "service_account.json")
    if os.path.exists(sa_file):
        return service_account.Credentials.from_service_account_file(
            sa_file,
            scopes=["https://www.googleapis.com/auth/analytics.readonly"],
        )

    return None

# Check if GA4 credentials are available
def has_ga4_creds():
    try:
        st.secrets["gcp_service_account"]
        return True
    except Exception:
        sa_file = os.getenv("GA4_SERVICE_ACCOUNT_FILE", "service_account.json")
        return os.path.exists(sa_file)

CS_MOCK = not CS_PROPERTY_ID or not has_ga4_creds()
SK_MOCK = not SK_PROPERTY_ID or not has_ga4_creds()
YT_MOCK = not YT_API_KEY or not YT_CHANNEL_ID

# ─────────────────────────────────────────
# DATE RANGE
# ─────────────────────────────────────────
parser = argparse.ArgumentParser()
parser.add_argument("--start", type=str)
parser.add_argument("--end", type=str)
args, _ = parser.parse_known_args()

default_end   = date.today()
default_start = default_end - timedelta(days=27)

# ─────────────────────────────────────────
# MOCK DATA
# ─────────────────────────────────────────
MOCK_CS = {
    "total_visits": 312, "unique_visitors": 289,
    "pageviews": 874, "bounce_rate": "58.2%",
    "avg_session_duration": "2m 14s",
}
MOCK_SK = {
    "total_visits": 200, "unique_visitors": 198,
    "pageviews": 243, "bounce_rate": "93.3%",
    "avg_session_duration": "4m 38s",
}
MOCK_YOUTUBE = {
    "subscribers": "1,204", "total_views": "18,432",
    "watch_time_hours": "941", "avg_view_duration": "3m 52s",
    "top_video": "Community Storytelling Workshop Recap",
    "top_video_views": "2,318",
}
MOCK_LINKEDIN = {
    "followers": "863", "impressions": "14,210",
    "clicks": "392", "engagement_rate": "4.7%",
    "top_post_impressions": "3,104", "new_followers": "47",
}
MOCK_INSTAGRAM = {
    "followers": "2,140", "reach": "8,930",
    "impressions": "21,440", "likes": "1,203",
    "comments": "184", "profile_visits": "612",
}
MOCK_FACEBOOK = {
    "page_likes": "1,872", "reach": "6,210",
    "impressions": "15,330", "post_engagements": "743",
    "new_likes": "28", "top_post_reach": "2,840",
}

# ─────────────────────────────────────────
# GA4 PULL
# ─────────────────────────────────────────
def pull_ga4(property_id, start, end):
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric

    credentials = get_ga4_credentials()
    client = BetaAnalyticsDataClient(credentials=credentials)
    request = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=str(start), end_date=str(end))],
        metrics=[
            Metric(name="sessions"),
            Metric(name="totalUsers"),
            Metric(name="screenPageViews"),
            Metric(name="bounceRate"),
            Metric(name="averageSessionDuration"),
        ],
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
# HELPERS
# ─────────────────────────────────────────
def mock_banner(platform):
    st.warning(f"⚠️ **Mock mode** — no live credentials for {platform}. Showing sample data.", icon="⚠️")

def section(label):
    st.markdown(f"**{label}**")

# ─────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────
st.markdown("## 📊 Studio Kula — Metrics Dashboard")
st.markdown("Automated 28-day metrics across all platforms · Intern: An Nguyen")
st.divider()

with st.sidebar:
    st.markdown("### Reporting period")
    start_date = st.date_input("Start date", value=default_start)
    end_date   = st.date_input("End date",   value=default_end)
    st.caption(f"{start_date} → {end_date}")
    st.divider()
    st.markdown("### Platform status")
    st.markdown("✅ CS.Us GA4 (US-01)")
    st.markdown("✅ Studio Kula GA4 (US-02)")
    st.markdown("✅ YouTube (US-06)")
    st.markdown("⏳ LinkedIn (US-05)")
    st.markdown("⚠️ Instagram (US-03)")
    st.markdown("⚠️ Facebook (US-04)")
    st.divider()
    st.caption("Studio Kula — Automated Metrics Tool\nSupervisor: Danielle Busko")

# ─────────────────────────────────────────
# TABS
# ─────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🌐 CS.Us (GA4)", "🌐 Studio Kula (GA4)", "📺 YouTube",
    "💼 LinkedIn", "📷 Instagram", "👤 Facebook",
])

# ── TAB 1: CS.Us ──
with tab1:
    st.markdown("### CS.Us Website — GA4 (US-01)")
    st.caption("communityserve.us · Google Analytics 4")
    if CS_MOCK:
        mock_banner("CS.Us GA4")
        data = MOCK_CS
    else:
        try:
            data = pull_ga4(CS_PROPERTY_ID, start_date, end_date)
        except Exception as e:
            st.error(f"Error fetching live data: {e}")
            data = MOCK_CS
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Visits", data["total_visits"])
    c2.metric("Unique Visitors", data["unique_visitors"])
    c3.metric("Pageviews", data["pageviews"])
    c4, c5 = st.columns(2)
    c4.metric("Bounce Rate", data["bounce_rate"])
    c5.metric("Avg Session Duration", data["avg_session_duration"])
    with st.expander("Raw data"):
        st.json(data)

# ── TAB 2: Studio Kula ──
with tab2:
    st.markdown("### Studio Kula Website — GA4 (US-02)")
    st.caption("studiokulamedia.com · Google Analytics 4")
    if SK_MOCK:
        mock_banner("Studio Kula GA4")
        data = MOCK_SK
    else:
        try:
            data = pull_ga4(SK_PROPERTY_ID, start_date, end_date)
        except Exception as e:
            st.error(f"Error fetching live data: {e}")
            data = MOCK_SK
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Visits", data["total_visits"])
    c2.metric("Unique Visitors", data["unique_visitors"])
    c3.metric("Pageviews", data["pageviews"])
    c4, c5 = st.columns(2)
    c4.metric("Bounce Rate", data["bounce_rate"])
    c5.metric("Avg Session Duration", data["avg_session_duration"])
    with st.expander("Raw data"):
        st.json(data)

# ── TAB 3: YouTube ──
with tab3:
    st.markdown("### YouTube — US-06")
    st.caption("YouTube Data API v3 · Studio Kula Channel")
    if YT_MOCK:
        mock_banner("YouTube")
        data = MOCK_YOUTUBE
    else:
        try:
            from googleapiclient.discovery import build
            youtube = build("youtube", "v3", developerKey=YT_API_KEY)
            channel_response = youtube.channels().list(
                part="snippet,statistics", id=YT_CHANNEL_ID
            ).execute()
            channel = channel_response["items"][0]
            stats   = channel["statistics"]
            search_response = youtube.search().list(
                part="snippet", channelId=YT_CHANNEL_ID,
                order="viewCount", type="video", maxResults=1,
                publishedAfter=f"{start_date}T00:00:00Z",
                publishedBefore=f"{end_date}T23:59:59Z",
            ).execute()
            top_video = "No videos this period"
            top_views = "—"
            if search_response.get("items"):
                vid = search_response["items"][0]
                top_video = vid["snippet"]["title"]
                vid_stats = youtube.videos().list(
                    part="statistics", id=vid["id"]["videoId"]
                ).execute()
                if vid_stats.get("items"):
                    top_views = f"{int(vid_stats['items'][0]['statistics'].get('viewCount', 0)):,}"
            data = {
                "subscribers":       f"{int(stats.get('subscriberCount', 0)):,}",
                "total_views":       f"{int(stats.get('viewCount', 0)):,}",
                "watch_time_hours":  "N/A (requires OAuth)",
                "avg_view_duration": "N/A (requires OAuth)",
                "top_video":         top_video,
                "top_video_views":   top_views,
            }
        except Exception as e:
            st.error(f"YouTube API error: {e}")
            data = MOCK_YOUTUBE
    c1, c2, c3 = st.columns(3)
    c1.metric("Subscribers", data["subscribers"])
    c2.metric("Total Views", data["total_views"])
    c3.metric("Watch Time (hrs)", data["watch_time_hours"])
    c4, c5 = st.columns(2)
    c4.metric("Avg View Duration", data["avg_view_duration"])
    c5.metric("New Subscribers (28d)", "—")
    st.divider()
    section("Top video this period")
    st.markdown(f"**{data['top_video']}** — {data['top_video_views']} views")
    with st.expander("Raw data"):
        st.json(data)

# ── TAB 4: LinkedIn ──
with tab4:
    st.markdown("### LinkedIn — US-05")
    st.caption("LinkedIn API · Awaiting: organization ID + OAuth credentials")
    mock_banner("LinkedIn")
    data = MOCK_LINKEDIN
    c1, c2, c3 = st.columns(3)
    c1.metric("Followers", data["followers"])
    c2.metric("Impressions", data["impressions"])
    c3.metric("Clicks", data["clicks"])
    c4, c5 = st.columns(2)
    c4.metric("Engagement Rate", data["engagement_rate"])
    c5.metric("New Followers (28d)", data["new_followers"])
    st.divider()
    section("Top post")
    st.markdown(f"**{data['top_post_impressions']}** impressions")
    with st.expander("Raw data"):
        st.json(data)

# ── TAB 5: Instagram ──
with tab5:
    st.markdown("### Instagram — US-03")
    st.caption("Meta Graph API · In progress")
    mock_banner("Instagram")
    data = MOCK_INSTAGRAM
    c1, c2, c3 = st.columns(3)
    c1.metric("Followers", data["followers"])
    c2.metric("Reach", data["reach"])
    c3.metric("Impressions", data["impressions"])
    c4, c5, c6 = st.columns(3)
    c4.metric("Likes", data["likes"])
    c5.metric("Comments", data["comments"])
    c6.metric("Profile Visits", data["profile_visits"])
    with st.expander("Raw data"):
        st.json(data)

# ── TAB 6: Facebook ──
with tab6:
    st.markdown("### Facebook — US-04")
    st.caption("Meta Graph API · In progress")
    mock_banner("Facebook")
    data = MOCK_FACEBOOK
    c1, c2, c3 = st.columns(3)
    c1.metric("Page Likes", data["page_likes"])
    c2.metric("Reach", data["reach"])
    c3.metric("Impressions", data["impressions"])
    c4, c5, c6 = st.columns(3)
    c4.metric("Post Engagements", data["post_engagements"])
    c5.metric("New Likes (28d)", data["new_likes"])
    c6.metric("Top Post Reach", data["top_post_reach"])
    with st.expander("Raw data"):
        st.json(data)