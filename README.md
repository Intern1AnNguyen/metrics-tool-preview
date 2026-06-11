# Automated Metrics Tool — US-01: Google Analytics 4
**Studio Kula / Community, Serve Us**
Prepared by: An Nguyen (Intern) | Supervised by: Danielle Busko (CEO)

---

## What This Does

Pulls core website metrics from Google Analytics 4 (GA4) for the CS.Us property and prints a summary report to the terminal. Metrics include sessions, users, pageviews, bounce rate, and average session duration for any date range.

---

## Setup (One Time)

### 1. Install dependencies
```bash
pip install google-analytics-data google-auth python-dotenv
```

### 2. Configure credentials
Rename `.env.example` to `.env`:
```bash
cp .env.example .env
```

Then open `.env` and fill in:
- `GA4_PROPERTY_ID` — find this in GA4 > Admin > Property Settings
- `GA4_SERVICE_ACCOUNT_FILE` — path to your service account JSON file (default: `service_account.json`)

### 3. Add the service account JSON
Place the downloaded `service_account.json` file in this folder.

> **Important:** The service account must have **Viewer** access to the GA4 property.
> In GA4: Admin > Property Access Management > Add the service account email with Viewer role.

---

## Usage

**Default (last 30 days):**
```bash
python ga4_metrics.py
```

**Custom date range:**
```bash
python ga4_metrics.py --start 2026-01-01 --end 2026-06-10
```

---

## Sample Output

```
Running GA4 report: 2026-05-11 → 2026-06-10

════════════════════════════════════════════════════════════
  STUDIO KULA — GA4 METRICS REPORT
  Period: 2026-05-11 → 2026-06-10
════════════════════════════════════════════════════════════

  Metric                         Value
  ---------------------------------------------
  Total Sessions                 1,284
  Total Users                      976
  Total Pageviews                3,541
  Avg Bounce Rate                42.3%
  Avg Session Duration           2m 14s
  ---------------------------------------------

  30 days of data returned.
════════════════════════════════════════════════════════════
```

---

## Status

| Item | Status |
|------|--------|
| Script scaffolded | ✅ Done |
| Mock output working | ✅ Done |
| GA4 Property ID | ⏳ Waiting on Danielle |
| Service Account JSON | ⏳ Waiting on Danielle |
| Live data confirmed | ⏳ Pending credentials |

---

## Files

| File | Purpose |
|------|---------|
| `ga4_metrics.py` | Main script |
| `.env.example` | Credentials template — rename to `.env` and fill in |
| `.env` | Your actual credentials — **never commit this** |
| `service_account.json` | Google service account key — **never commit this** |
| `.gitignore` | Protects credentials from being pushed to GitHub |

---

## Next Steps (After Credentials Received)
1. Fill in `.env` with Property ID and service account path
2. Run `python ga4_metrics.py` to confirm live data pulls
3. Expand to additional platforms: Instagram, Facebook, LinkedIn, YouTube (US-02+)