# C&H Scout — NSE India
## Cup & Handle Pattern AI Agent · Powered by Claude AI

### Live at: [your-app.streamlit.app]

---

## 🚀 Deploy in 4 Steps (No coding needed)

### Step 1 — Create GitHub Repository
1. Go to **github.com** → Sign Up (if you don't have an account)
2. Click **+** (top right) → **New repository**
3. Name: `ch-scout` · Set to **Public** · Check **Add README**
4. Click **Create repository**

### Step 2 — Upload These Files
In your new repository, click **Add file → Upload files** and upload:
- `app.py`
- `requirements.txt`
- `README.md`

Then click **Commit changes**

### Step 3 — Get Your Claude API Key
1. Go to **console.anthropic.com**
2. Sign up / log in
3. Click **API Keys → Create Key**
4. Copy the key (starts with `sk-ant-...`)

### Step 4 — Deploy on Streamlit Cloud
1. Go to **share.streamlit.io**
2. Click **Sign in with GitHub**
3. Click **New app**
4. Fill in:
   - Repository: `your-username/ch-scout`
   - Branch: `main`
   - Main file path: `app.py`
5. Click **Advanced settings → Secrets** and paste:

```toml
ANTHROPIC_API_KEY = "sk-ant-your-key-here"
```

6. Click **Deploy!**

Your app will be live in ~2 minutes at:
`https://your-username-ch-scout.streamlit.app`

---

## Features
- 📡 **Live NSE data** via Yahoo Finance (yfinance) — server-side, no CORS issues
- 🔍 **150 stocks** — Nifty 50 + Midcap 50 + Smallcap 50 + custom watchlist
- 📅 **4 timeframes** — Daily 300d, Weekly 104w, Daily 5Y, Weekly 5Y
- 🤖 **Claude AI analysis** — per setup, specific to each stock
- 📊 **Plotly charts** — interactive candlestick with entry/SL/target levels
- ✅ **Pattern checklist** — 6-point C&H quality validation

## Data Source
Yahoo Finance via `yfinance` Python library — free, no API key needed for price data.
Data is cached for 15 minutes to avoid rate limits.

## Disclaimer
For educational purposes only. Not financial advice.
