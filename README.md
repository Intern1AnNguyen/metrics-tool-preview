# Automated Metrics Tool
**Studio Kula / Community, Serve Us**
Prepared by: An Nguyen (Intern) | Supervised by: Danielle Busko (CEO)

---

## What This Does

Automatically pulls 28-day metrics from all tracked platforms and displays them in a browser dashboard. Replaces Danielle's manual monthly tracking across 6 platforms.

**Platforms:**
| Story | Platform | API | Status |
|---|---|---|---|
| US-01 | CS.Us website | GA4 Data API | ✅ Live |
| US-02 | Studio Kula website | GA4 Data API | ✅ Live |
| US-06 | YouTube | YouTube Data API v3 | 🔄 In progress |
| US-05 | LinkedIn | LinkedIn API | 🔄 In progress |
| US-03 | Instagram | Meta Graph API | 🔄 In progress |
| US-04 | Facebook | Meta Graph API | 🔄 In progress |

---

## Setup (One Time)

### 1. Install dependencies
```bash
pip install google-analytics-data google-auth python-dotenv streamlit
```

### 2. Configure credentials
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Fill in your `.env`:
```
GA4_PROPERTY_ID=your_csus_property_id
GA4_PROPERTY_ID_SK=your_studiokula_property_id
GA4_SERVICE_ACCOUNT_FILE=service_account.json
```

### 3. Add the service account JSON
Place the downloaded `service_account.json` file in this folder.

> **Important:** The service account must have **Viewer** access to both GA4 properties.
> In GA4: Admin > Property Access Management > Add the service account email with Viewer role.

---

## Usage

**Run the browser dashboard (recommended):**
```bash
python -m streamlit run dashboard.py
```
Opens at `http://localhost:8501`

**Run individual scripts (terminal output):**
```bash
python ga4_metrics.py
python studio_kula_metrics.py
```

**Custom date range:**
```bash
python ga4_metrics.py --start 2026-01-01 --end 2026-06-22
```

---

## Sample Output (CS.Us GA4)

```
Running GA4 report: 2026-05-23 → 2026-06-22

════════════════════════════════════════════════════════════
  STUDIO KULA — GA4 METRICS REPORT
  Period: 2026-05-23 → 2026-06-22
════════════════════════════════════════════════════════════
  Metric                                   Value
  ---------------------------------------------
  Total Sessions                             915
  Total Users                                883
  Total Pageviews                          1,109
  Avg Bounce Rate                         74.3%
  Avg Session Duration                    1m 10s
  ---------------------------------------------
  31 days of data returned.
════════════════════════════════════════════════════════════
```

---

## Mock Mode

All scripts run in **mock mode** automatically when credentials are missing — no errors, just sample data. This allows development and demos without live credentials.

Mock mode disables automatically when valid credentials are found in `.env`.

---

## Files

| File | Purpose |
|---|---|
| `dashboard.py` | 6-tab Streamlit browser dashboard |
| `ga4_metrics.py` | CS.Us GA4 script (US-01) |
| `studio_kula_metrics.py` | Studio Kula GA4 script (US-02) |
| `.env.example` | Credentials template — copy to `.env` and fill in |
| `.env` | Your actual credentials — **never commit this** |
| `service_account.json` | Google service account key — **never commit this** |
| `.gitignore` | Protects credentials from being pushed to GitHub |

---

## Repo
github.com/Studio-Kula/metrics-tool