import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import anthropic
import time

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="C&H Scout — NSE India",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

  html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

  .main { background-color: #0a0c10; }
  .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

  /* Header */
  .app-header {
    background: linear-gradient(135deg, #111318 0%, #181c24 100%);
    border: 1px solid #1e2530;
    border-radius: 12px;
    padding: 20px 28px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .app-title {
    font-size: 36px;
    font-weight: 700;
    letter-spacing: -0.5px;
    color: #f0b429;
    margin: 0;
  }
  .app-title span { color: #e8eaf0; }
  .app-sub { font-size: 12px; color: #5a6175; margin-top: 2px; font-family: 'DM Mono', monospace; }
  .live-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(0,212,170,.12); border: 1px solid rgba(0,212,170,.35);
    color: #00d4aa; font-size: 11px; padding: 4px 12px; border-radius: 20px;
    font-family: 'DM Mono', monospace; letter-spacing: .5px;
  }

  /* Signal cards */
  .sig-card {
    border-radius: 10px; padding: 16px; margin-bottom: 12px;
    border: 1px solid #1e2530; background: #111318;
    transition: border-color .2s;
  }
  .sig-card:hover { border-color: #2e3a50; }
  .sig-ticker { font-size: 22px; font-weight: 700; color: #f0b429; letter-spacing: .5px; }
  .sig-name { font-size: 12px; color: #5a6175; margin-top: 2px; }
  .sig-score-high { color: #00d4aa; font-size: 32px; font-weight: 700; }
  .sig-score-mid  { color: #f0b429; font-size: 32px; font-weight: 700; }
  .sig-score-low  { color: #ff4d6d; font-size: 32px; font-weight: 700; }

  /* Metric tiles */
  .metric-tile {
    background: #0a0c10; border: 1px solid #1e2530; border-radius: 8px;
    padding: 12px 14px; text-align: center;
  }
  .metric-lbl { font-size: 10px; color: #5a6175; text-transform: uppercase;
    letter-spacing: .8px; font-family: 'DM Mono', monospace; margin-bottom: 4px; }
  .metric-val { font-size: 15px; font-weight: 600; font-family: 'DM Mono', monospace; }
  .mv-green { color: #00d4aa; }
  .mv-yellow { color: #f0b429; }
  .mv-red { color: #ff4d6d; }
  .mv-blue { color: #5b9cf6; }

  /* Signal badges */
  .badge {
    display: inline-block; font-size: 11px; font-weight: 600;
    padding: 4px 12px; border-radius: 4px; letter-spacing: .5px;
  }
  .badge-sb { background: rgba(0,212,170,.18); color: #00d4aa; border: 1px solid rgba(0,212,170,.4); }
  .badge-bu { background: rgba(0,212,170,.1);  color: #5ee8c8; border: 1px solid rgba(0,212,170,.2); }
  .badge-wa { background: rgba(240,180,41,.15); color: #f0b429; border: 1px solid rgba(240,180,41,.3); }
  .badge-av { background: rgba(255,77,109,.12); color: #ff4d6d; border: 1px solid rgba(255,77,109,.25); }
  .badge-sk { background: rgba(255,77,109,.2);  color: #ff4d6d; border: 1px solid rgba(255,77,109,.4); }
  .badge-n50 { background: rgba(240,180,41,.1); color: #f0b429; border: 1px solid rgba(240,180,41,.25); }
  .badge-mid { background: rgba(0,212,170,.08); color: #00d4aa; border: 1px solid rgba(0,212,170,.2); }
  .badge-sc  { background: rgba(91,156,246,.1); color: #5b9cf6; border: 1px solid rgba(91,156,246,.25); }
  .badge-wl  { background: rgba(167,139,250,.1);color: #a78bfa; border: 1px solid rgba(167,139,250,.25); }
  .badge-tf  { background: rgba(255,255,255,.05); color: #8892a4; border: 1px solid #1e2530; font-size:10px; }

  /* Checklist */
  .chk-row { display: flex; align-items: center; gap: 8px; font-size: 12px; margin-bottom: 5px; }
  .chk-pass { color: #00d4aa; } .chk-fail { color: #ff4d6d; }

  /* AI box */
  .ai-box {
    background: #0a0c10; border: 1px solid #1e2530; border-radius: 8px;
    padding: 14px 16px; margin-top: 12px;
  }
  .ai-label { font-size: 10px; color: #f0b429; text-transform: uppercase;
    letter-spacing: 1px; font-family: 'DM Mono', monospace; margin-bottom: 8px; }
  .ai-text { font-size: 13px; color: #c8cad4; line-height: 1.65; font-weight: 300; }

  /* Disclaimer */
  .disc {
    background: rgba(255,77,109,.04); border: 1px solid rgba(255,77,109,.15);
    border-radius: 8px; padding: 12px 16px; font-size: 11px; color: #5a6175;
    line-height: 1.6; margin-top: 24px;
  }

  /* Sidebar */
  section[data-testid="stSidebar"] { background: #111318; }
  section[data-testid="stSidebar"] .stMarkdown { color: #e8eaf0; }

  /* Streamlit overrides */
  .stProgress .st-bo { background-color: #f0b429; }
  div[data-testid="stExpander"] { border: 1px solid #1e2530 !important; border-radius: 8px !important; background: #111318; }
  div[data-testid="stExpander"] summary { color: #f0b429 !important; }
</style>
""", unsafe_allow_html=True)

# ── STOCK LISTS ───────────────────────────────────────────────────────────────
NIFTY50 = [
    ("RELIANCE","Reliance Industries"),("TCS","Tata Consultancy Svcs"),
    ("HDFCBANK","HDFC Bank"),("INFY","Infosys"),
    ("ICICIBANK","ICICI Bank"),("HINDUNILVR","Hindustan Unilever"),
    ("SBIN","State Bank of India"),("BHARTIARTL","Bharti Airtel"),
    ("ITC","ITC Limited"),("KOTAKBANK","Kotak Mahindra Bank"),
    ("LT","Larsen & Toubro"),("AXISBANK","Axis Bank"),
    ("ASIANPAINT","Asian Paints"),("MARUTI","Maruti Suzuki"),
    ("SUNPHARMA","Sun Pharmaceutical"),("TITAN","Titan Company"),
    ("WIPRO","Wipro"),("ULTRACEMCO","UltraTech Cement"),
    ("BAJFINANCE","Bajaj Finance"),("NESTLEIND","Nestle India"),
    ("TATAMOTORS","Tata Motors"),("HCLTECH","HCL Technologies"),
    ("POWERGRID","Power Grid Corp"),("NTPC","NTPC Limited"),
    ("M&M","Mahindra & Mahindra"),("JSWSTEEL","JSW Steel"),
    ("ADANIENT","Adani Enterprises"),("ONGC","ONGC"),
    ("CIPLA","Cipla Ltd"),("COALINDIA","Coal India"),
    ("TATASTEEL","Tata Steel"),("BAJAJFINSV","Bajaj Finserv"),
    ("TECHM","Tech Mahindra"),("GRASIM","Grasim Industries"),
    ("APOLLOHOSP","Apollo Hospitals"),("EICHERMOT","Eicher Motors"),
    ("HINDALCO","Hindalco Industries"),("DIVISLAB","Divi's Labs"),
    ("BEL","Bharat Electronics"),("BPCL","BPCL"),
    ("HEROMOTOCO","Hero MotoCorp"),("DRREDDY","Dr. Reddy's"),
    ("SHRIRAMFIN","Shriram Finance"),("TATACONSUM","Tata Consumer"),
    ("ADANIPORTS","Adani Ports"),("INDUSINDBK","IndusInd Bank"),
    ("SBILIFE","SBI Life Insurance"),("HDFCLIFE","HDFC Life"),
    ("BAJAJ-AUTO","Bajaj Auto"),("HAL","Hindustan Aeronautics"),
]

MIDCAP50 = [
    ("BSE","BSE Limited"),("INDUSTOWER","Indus Towers"),
    ("POLYCAB","Polycab India"),("LUPIN","Lupin Ltd"),
    ("ASHOKLEY","Ashok Leyland"),("GMRINFRA","GMR Airports"),
    ("MARICO","Marico Ltd"),("BHEL","Bharat Heavy Electricals"),
    ("WAAREEENER","Waaree Energies"),("ICICIGI","ICICI Lombard"),
    ("BHARATFORG","Bharat Forge"),("PERSISTENT","Persistent Systems"),
    ("MANKIND","Mankind Pharma"),("HAVELLS","Havells India"),
    ("AUROPHARMA","Aurobindo Pharma"),("HINDPETRO","HPCL"),
    ("NHPC","NHPC Ltd"),("DABUR","Dabur India"),
    ("OIL","Oil India"),("NMDC","NMDC Ltd"),
    ("FEDERALBNK","Federal Bank"),("MFSL","Max Financial Services"),
    ("CUMMINSIND","Cummins India"),("OFSS","Oracle Fin Services"),
    ("SUZLON","Suzlon Energy"),("PIIND","PI Industries"),
    ("CONCOR","Container Corp"),("ABCAPITAL","Aditya Birla Capital"),
    ("BANKBARODA","Bank of Baroda"),("MPHASIS","Mphasis"),
    ("TRENT","Trent Ltd"),("ZOMATO","Zomato Ltd"),
    ("DELHIVERY","Delhivery Ltd"),("PAGEIND","Page Industries"),
    ("SUPREMEIND","Supreme Industries"),("COFORGE","Coforge Ltd"),
    ("SUNDARMFIN","Sundaram Finance"),("LICHSGFIN","LIC Housing Finance"),
    ("KALYANKJIL","Kalyan Jewellers"),("INDHOTEL","Indian Hotels"),
    ("ALKEM","Alkem Laboratories"),("TORNTPHARM","Torrent Pharma"),
    ("VOLTAS","Voltas Ltd"),("IDFCFIRSTB","IDFC First Bank"),
    ("SOLARINDS","Solar Industries"),("OBEROIRLTY","Oberoi Realty"),
    ("KPITTECH","KPIT Technologies"),("MCX","Multi Commodity Exchange"),
    ("ABFRL","Aditya Birla Fashion"),("GODREJPROP","Godrej Properties"),
]

SMALLCAP50 = [
    ("LAURUSLABS","Laurus Labs"),("RADICO","Radico Khaitan"),
    ("NH","Narayana Hrudayalaya"),("JBCHEPHARM","JB Chemicals"),
    ("ASTERDM","Aster DM Healthcare"),("POONAWALLA","Poonawalla Fincorp"),
    ("NAVINFLUOR","Navin Fluorine"),("CDSL","CDSL"),
    ("KAYNES","Kaynes Technology"),("AMBER","Amber Enterprises"),
    ("NBCC","NBCC India"),("MANAPPURAM","Manappuram Finance"),
    ("RAMCOCEM","Ramco Cements"),("WELCORP","Welspun Corp"),
    ("MAZDOCK","Mazagon Dock"),("ELGIEQUIP","Elgi Equipments"),
    ("APARINDS","Apar Industries"),("BIKAJI","Bikaji Foods"),
    ("ANANTRAJ","Anant Raj Ltd"),("PNBHOUSING","PNB Housing Finance"),
    ("CAMS","CAMS"),("NUVAMA","Nuvama Wealth Mgmt"),
    ("HOMEFIRST","Home First Finance"),("CREDITACC","CreditAccess Grameen"),
    ("RKFORGE","Ramkrishna Forgings"),("ROUTE","Route Mobile"),
    ("NEWGEN","Newgen Software"),("GRINDWELL","Grindwell Norton"),
    ("KANSAINER","Kansai Nerolac"),("AAVAS","Aavas Financiers"),
    ("JKCEMENT","JK Cement"),("EQUITASBNK","Equitas Small Finance"),
    ("BANDHANBNK","Bandhan Bank"),("KARURVYSYA","Karur Vysya Bank"),
    ("GLAND","Gland Pharma"),("CHOLAHLDNG","Chola Financial Hldg"),
    ("HIMATSEIDE","Himadri Speciality"),("SAPPHIRE","Sapphire Foods"),
    ("TEJASNET","Tejas Networks"),("NIACL","New India Assurance"),
    ("CENTURYPLY","Century Plyboards"),("LAXMIMACH","Lakshmi Machine Works"),
    ("POLYMED","Poly Medicure"),("DMART","Avenue Supermarts"),
    ("FINEORG","Fine Organic Industries"),("HERITGFOOD","Heritage Foods"),
    ("NAZARA","Nazara Technologies"),("TARSONS","Tarsons Products"),
    ("PGHL","Procter & Gamble Health"),("KFINTECH","KFin Technologies"),
]

# ── TIMEFRAME CONFIG ──────────────────────────────────────────────────────────
TF_CONFIG = {
    "Daily (300 days)":  {"interval": "1d",  "period": "14mo", "key": "D",  "bars": 300},
    "Weekly (104 weeks)":{"interval": "1wk", "period": "2y",   "key": "W",  "bars": 104},
    "Daily 5Y":          {"interval": "1d",  "period": "5y",   "key": "D5", "bars": 1250},
    "Weekly 5Y":         {"interval": "1wk", "period": "5y",   "key": "W5", "bars": 260},
}

# ── DATA FETCHING ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=900, show_spinner=False)  # Cache 15 min
def fetch_ohlcv(symbol: str, interval: str, period: str) -> pd.DataFrame | None:
    try:
        ticker = yf.Ticker(f"{symbol}.NS")
        df = ticker.history(period=period, interval=interval, auto_adjust=True)
        if df is None or len(df) < 30:
            return None
        df = df[["Open","High","Low","Close","Volume"]].dropna()
        return df
    except Exception:
        return None

@st.cache_data(ttl=900, show_spinner=False)
def fetch_info(symbol: str) -> dict:
    try:
        t = yf.Ticker(f"{symbol}.NS")
        info = t.fast_info
        return {
            "ltp": getattr(info, "last_price", None),
            "prev_close": getattr(info, "previous_close", None),
            "week52_high": getattr(info, "year_high", None),
            "week52_low": getattr(info, "year_low", None),
        }
    except Exception:
        return {}

# ── CUP & HANDLE DETECTION ────────────────────────────────────────────────────
def detect_ch(df: pd.DataFrame) -> dict | None:
    closes = df["Close"].values
    volumes = df["Volume"].values
    n = len(closes)
    if n < 30:
        return None

    p1e = int(n * 0.25)
    p2s, p2e = int(n * 0.18), int(n * 0.62)
    p3s, p3e = int(n * 0.52), int(n * 0.86)
    p4s = int(n * 0.83)

    pk1 = closes[:p1e].max()
    bot = closes[p2s:p2e].min()
    pk2 = closes[p3s:p3e].max()
    hlo = closes[p4s:].min()
    cur = closes[-1]

    cup_depth  = (pk1 - bot) / pk1
    recovery   = (pk2 - bot) / (pk1 - bot) if (pk1 - bot) > 0 else 0
    handle_pct = (pk2 - hlo) / pk2 if pk2 > 0 else 0

    avg_vol = volumes[:p4s].mean() if p4s > 0 else 1
    brk_vol = volumes[p4s:].mean() if len(volumes[p4s:]) > 0 else 1
    vol_surge = brk_vol / avg_vol if avg_vol > 0 else 1

    c_ushape   = 0.07 < cup_depth < 0.45
    c_recovery = recovery > 0.75
    c_handle   = 0.015 < handle_pct < 0.20
    c_near_brk = cur > pk2 * 0.96
    c_breakout = cur > pk2 * 1.001
    c_volume   = vol_surge > 1.2

    score = 0
    if c_ushape:   score += 22
    if c_recovery: score += 28
    if c_handle:   score += 22
    if c_near_brk: score += 18
    if c_volume:   score += 10
    score = min(98, max(5, score))

    entry    = pk2 * 1.003
    stop     = hlo * 0.986
    target   = pk2 + (pk2 - bot) * 0.85
    rr       = (target - entry) / (entry - stop) if entry > stop else 0

    return {
        "score": score,
        "checks": {
            "U-shaped cup":         c_ushape,
            "Recovery to rim":      c_recovery,
            "Clean handle":         c_handle,
            "Near breakout zone":   c_near_brk,
            "Breakout confirmed":   c_breakout,
            f"Volume surge ({vol_surge:.1f}x)": c_volume,
        },
        "entry":  round(entry, 2),
        "stop":   round(stop, 2),
        "target": round(target, 2),
        "rr":     round(rr, 1),
        "cup_depth": round(cup_depth * 100, 1),
        "recovery":  round(recovery * 100, 1),
        "vol_surge": round(vol_surge, 1),
        "pk1": pk1, "bot": bot, "pk2": pk2, "hlo": hlo, "cur": cur,
    }

# ── SIGNAL HELPERS ────────────────────────────────────────────────────────────
def get_signal(score: int, rr: float) -> tuple[str, str]:
    if score >= 80 and rr >= 2: return "STRONG BUY", "badge-sb"
    if score >= 65:              return "BUY",         "badge-bu"
    if score >= 45:              return "WATCH",       "badge-wa"
    if score >= 30:              return "AVOID",       "badge-av"
    return "SELL / SKIP", "badge-sk"

def score_color(score: int) -> str:
    if score >= 70: return "sig-score-high"
    if score >= 45: return "sig-score-mid"
    return "sig-score-low"

def fmt_inr(v) -> str:
    return f"₹{v:,.2f}" if v else "N/A"

def pct_change(cur, prev) -> str:
    if not cur or not prev: return ""
    d = (cur - prev) / prev * 100
    return f"{'▲' if d >= 0 else '▼'} {abs(d):.2f}%"

def src_badge(src: str) -> str:
    badges = {"N50":"badge-n50","MID":"badge-mid","SC":"badge-sc","WL":"badge-wl"}
    labels = {"N50":"Nifty 50","MID":"Midcap 50","SC":"Smallcap 50","WL":"Watchlist"}
    c = badges.get(src,"badge-wl")
    l = labels.get(src, src)
    return f'<span class="badge {c}">{l}</span>'

# ── PLOTLY CHART ──────────────────────────────────────────────────────────────
def make_chart(df: pd.DataFrame, analysis: dict, sym: str, tf_label: str) -> go.Figure:
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        row_heights=[0.75, 0.25], vertical_spacing=0.03
    )

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"],
        increasing_line_color="#00d4aa", decreasing_line_color="#ff4d6d",
        increasing_fillcolor="#00d4aa", decreasing_fillcolor="#ff4d6d",
        name="Price", line_width=1,
    ), row=1, col=1)

    # Volume bars
    colors = ["#00d4aa" if c >= o else "#ff4d6d"
              for c, o in zip(df["Close"], df["Open"])]
    fig.add_trace(go.Bar(
        x=df.index, y=df["Volume"], marker_color=colors,
        opacity=0.5, name="Volume", showlegend=False,
    ), row=2, col=1)

    # Key levels
    a = analysis
    closes = df["Close"].values
    n = len(closes)

    # Cup rim left
    p1e_idx = int(n * 0.25)
    rim_left_idx = int(np.argmax(closes[:p1e_idx]))
    rim_right_s = int(n * 0.55)
    rim_right_e = int(n * 0.86)
    rim_right_idx = rim_right_s + int(np.argmax(closes[rim_right_s:rim_right_e]))
    cup_bottom_idx = int(n * 0.18) + int(np.argmin(closes[int(n*0.18):int(n*0.62)]))
    handle_low_idx = int(n * 0.83) + int(np.argmin(closes[int(n*0.83):]))

    # Dotted level lines
    def hline(y, color, dash, label, row=1):
        fig.add_hline(y=y, line_color=color, line_dash=dash,
                      line_width=1, opacity=0.7, row=row, col=1,
                      annotation_text=label,
                      annotation_position="right",
                      annotation_font_color=color,
                      annotation_font_size=10)

    hline(a["entry"],  "#f0b429", "dash",  f"Entry {fmt_inr(a['entry'])}")
    hline(a["stop"],   "#ff4d6d", "dot",   f"SL {fmt_inr(a['stop'])}")
    hline(a["target"], "#00d4aa", "dash",  f"Target {fmt_inr(a['target'])}")

    # Cup shape annotation
    fig.add_shape(dict(
        type="path",
        path=f"M {rim_left_idx},1 Q {cup_bottom_idx},0 {rim_right_idx},1",
        xref="x", yref="paper",
        line=dict(color="rgba(240,180,41,0.3)", width=1, dash="dot"),
    ))

    fig.update_layout(
        plot_bgcolor="#0a0c10", paper_bgcolor="#111318",
        margin=dict(l=10, r=80, t=30, b=10),
        height=380,
        showlegend=False,
        xaxis_rangeslider_visible=False,
        xaxis=dict(gridcolor="#1e2530", showgrid=True, color="#5a6175"),
        yaxis=dict(gridcolor="#1e2530", showgrid=True, color="#5a6175",
                   title="Price (₹)", title_font_color="#5a6175"),
        xaxis2=dict(gridcolor="#1e2530", color="#5a6175"),
        yaxis2=dict(gridcolor="#1e2530", color="#5a6175", title="Volume",
                    title_font_color="#5a6175"),
        font=dict(color="#8892a4", family="DM Sans"),
        title=dict(text=f"{sym} · {tf_label}",
                   font=dict(color="#f0b429", size=13), x=0.01),
    )
    return fig

# ── AI ANALYSIS ───────────────────────────────────────────────────────────────
def get_ai_analysis(sym: str, name: str, analysis: dict,
                    tf_label: str, info: dict) -> str:
    try:
        client = anthropic.Anthropic()
        sig, _ = get_signal(analysis["score"], analysis["rr"])
        chg = pct_change(info.get("ltp"), info.get("prev_close"))
        prompt = f"""You are a sharp NSE/BSE technical analyst. Analyze this Cup & Handle setup:

Stock: {sym} ({name}) | NSE | Timeframe: {tf_label}
Live Price: {fmt_inr(info.get('ltp'))} | Today's change: {chg or 'N/A'}
52W High: {fmt_inr(info.get('week52_high'))} | 52W Low: {fmt_inr(info.get('week52_low'))}

Pattern Score: {analysis['score']}/100 | Signal: {sig}
Cup depth: {analysis['cup_depth']}% | Recovery: {analysis['recovery']}% | Handle pullback: {((analysis['pk2']-analysis['hlo'])/analysis['pk2']*100):.1f}%
Entry: {fmt_inr(analysis['entry'])} | Stop Loss: {fmt_inr(analysis['stop'])} | Target: {fmt_inr(analysis['target'])} | R:R = {analysis['rr']}:1
Volume surge at breakout zone: {analysis['vol_surge']}x average
Breakout confirmed: {'Yes' if analysis['checks'].get('Breakout confirmed') else 'No — watch zone'}

In 2-3 sharp sentences: assess the pattern quality (textbook vs flawed), flag one key risk specific to this stock, and give one actionable tip for an Indian retail trader. Be direct and specific. No generic disclaimers."""

        msg = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        return msg.content[0].text
    except Exception as e:
        return f"AI analysis unavailable — evaluate the metrics manually. ({str(e)[:60]})"

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Scan Settings")
    st.markdown("---")

    st.markdown("#### 📊 Universe")
    use_n50  = st.checkbox("Nifty 50",        value=True,  help="Top 50 large cap NSE stocks")
    use_mid  = st.checkbox("Nifty Midcap 50", value=False, help="Top 50 mid cap NSE stocks")
    use_sc   = st.checkbox("Nifty Smallcap 50", value=False, help="Top 50 small cap NSE stocks")

    st.markdown("#### 📋 My Watchlist")
    watchlist_input = st.text_area(
        "NSE symbols (comma separated)",
        placeholder="e.g. BAJFINANCE, TATAMOTORS, SUNPHARMA",
        height=80, label_visibility="collapsed"
    )
    use_watchlist = bool(watchlist_input.strip())

    st.markdown("#### 📅 Timeframe")
    tf_options = list(TF_CONFIG.keys())
    selected_tfs = []
    tf_daily  = st.checkbox("Daily (300 days)",  value=True)
    tf_weekly = st.checkbox("Weekly (104 weeks)", value=True)
    st.markdown("<small style='color:#5a6175'>— 5-Year Deep Scan —</small>", unsafe_allow_html=True)
    tf_d5 = st.checkbox("Daily 5Y (~1250 days)",   value=False)
    tf_w5 = st.checkbox("Weekly 5Y (~260 weeks)",  value=False)

    if tf_daily:  selected_tfs.append("Daily (300 days)")
    if tf_weekly: selected_tfs.append("Weekly (104 weeks)")
    if tf_d5:     selected_tfs.append("Daily 5Y")
    if tf_w5:     selected_tfs.append("Weekly 5Y")

    st.markdown("#### 🎯 Min Confidence Score")
    min_score = st.slider("", 30, 80, 40, step=5, label_visibility="collapsed")

    st.markdown("#### 🤖 AI Analysis")
    run_ai = st.checkbox("Generate Claude AI analysis", value=True,
                         help="Uses Claude API — requires ANTHROPIC_API_KEY in Streamlit secrets")

    st.markdown("---")
    scan_btn = st.button("▶ SCAN NOW", type="primary", use_container_width=True)

    st.markdown("""
    <div style='font-size:10px;color:#3a4155;margin-top:16px;line-height:1.6;'>
    Data: Yahoo Finance (yfinance)<br>
    Live NSE prices · 15-min delayed<br>
    AI: Claude claude-sonnet-4-20250514
    </div>
    """, unsafe_allow_html=True)

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <div>
    <div class="app-title">C&H <span>Scout</span></div>
    <div class="app-sub">Cup & Handle Pattern AI Agent · Live NSE Data</div>
  </div>
  <div>
    <div class="live-badge">● LIVE NSE · Yahoo Finance</div>
    <div style="font-size:10px;color:#3a4155;margin-top:4px;text-align:right;font-family:'DM Mono',monospace;">Powered by Claude AI</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── MAIN SCAN LOGIC ───────────────────────────────────────────────────────────
if scan_btn:
    # Validate
    if not any([use_n50, use_mid, use_sc, use_watchlist]):
        st.error("Please select at least one universe.")
        st.stop()
    if not selected_tfs:
        st.error("Please select at least one timeframe.")
        st.stop()

    # Build stock list
    stock_map = {}
    if use_n50:
        for s, n in NIFTY50:
            stock_map[s] = (n, "N50")
    if use_mid:
        for s, n in MIDCAP50:
            if s not in stock_map:
                stock_map[s] = (n, "MID")
    if use_sc:
        for s, n in SMALLCAP50:
            if s not in stock_map:
                stock_map[s] = (n, "SC")
    if use_watchlist:
        for sym in watchlist_input.split(","):
            sym = sym.strip().upper()
            if sym and sym not in stock_map:
                stock_map[sym] = (sym, "WL")

    stocks = list(stock_map.items())  # [(sym, (name, src))]
    total = len(stocks) * len(selected_tfs)

    st.markdown(f"**Scanning {len(stocks)} stocks × {len(selected_tfs)} timeframe(s) = {total} requests**")

    prog_bar  = st.progress(0)
    prog_text = st.empty()
    results   = []
    done = 0
    found = 0

    for sym, (name, src) in stocks:
        for tf_label in selected_tfs:
            done += 1
            cfg = TF_CONFIG[tf_label]
            prog_text.markdown(
                f"`Fetching {sym}.NS [{tf_label}]  ·  {done}/{total}  ·  Patterns found: {found}`"
            )
            prog_bar.progress(done / total)

            df = fetch_ohlcv(sym, cfg["interval"], cfg["period"])
            if df is None or len(df) < 30:
                continue

            analysis = detect_ch(df)
            if analysis is None or analysis["score"] < min_score:
                continue

            info = fetch_info(sym)
            found += 1
            results.append({
                "sym": sym, "name": name, "src": src,
                "tf": tf_label, "df": df,
                "analysis": analysis, "info": info,
            })
            time.sleep(0.05)  # gentle rate limiting

    prog_bar.progress(1.0)
    prog_text.markdown(f"`✓ Scan complete · {done} requests · {found} patterns found`")

    if not results:
        st.warning("No Cup & Handle patterns found above the minimum score threshold. Try lowering the minimum confidence score or expanding the universe.")
        st.stop()

    # Sort by score desc
    results.sort(key=lambda x: x["analysis"]["score"], reverse=True)

    # ── SUMMARY STATS ─────────────────────────────────────────────────────────
    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    strong = sum(1 for r in results if r["analysis"]["score"] >= 70)
    avg_rr = np.mean([r["analysis"]["rr"] for r in results])
    c1.metric("Patterns Found",    found)
    c2.metric("Strong Setups ≥70", strong)
    c3.metric("Avg R:R Ratio",     f"{avg_rr:.1f}:1")
    c4.metric("Stocks Scanned",    len(stocks))

    # ── FILTER TABS ───────────────────────────────────────────────────────────
    tabs = st.tabs(["All Results", "Strong ≥70", "Nifty 50", "Midcap 50", "Smallcap 50",
                    "Watchlist", "Daily", "Weekly", "5-Year"])
    tab_filters = {
        0: lambda r: True,
        1: lambda r: r["analysis"]["score"] >= 70,
        2: lambda r: r["src"] == "N50",
        3: lambda r: r["src"] == "MID",
        4: lambda r: r["src"] == "SC",
        5: lambda r: r["src"] == "WL",
        6: lambda r: r["tf"] in ("Daily (300 days)",),
        7: lambda r: r["tf"] in ("Weekly (104 weeks)",),
        8: lambda r: r["tf"] in ("Daily 5Y", "Weekly 5Y"),
    }

    for tab_idx, tab in enumerate(tabs):
        with tab:
            filtered = [r for r in results if tab_filters[tab_idx](r)]
            if not filtered:
                st.info("No patterns in this category.")
                continue

            for r in filtered:
                sym      = r["sym"]
                name     = r["name"]
                src      = r["src"]
                tf_label = r["tf"]
                df       = r["df"]
                a        = r["analysis"]
                info     = r["info"]
                sig, sig_cls = get_signal(a["score"], a["rr"])
                chg      = pct_change(info.get("ltp"), info.get("prev_close"))
                chg_col  = "green" if chg and "▲" in chg else "red" if chg else "gray"

                with st.expander(
                    f"{'🟢' if a['score']>=70 else '🟡' if a['score']>=45 else '🔴'} "
                    f"{sym} — Score {a['score']} — {sig} — {tf_label}",
                    expanded=False
                ):
                    # ── Top row: identity + live price
                    col_id, col_price, col_score = st.columns([3, 3, 2])
                    with col_id:
                        st.markdown(
                            f"<div class='sig-ticker'>{sym}</div>"
                            f"<div class='sig-name'>{name}</div>"
                            f"<div style='margin-top:6px'>"
                            f"{src_badge(src)} "
                            f"<span class='badge badge-tf'>{tf_label}</span>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
                    with col_price:
                        ltp = info.get("ltp")
                        if ltp:
                            st.markdown(
                                f"<div class='metric-tile'>"
                                f"<div class='metric-lbl'>Live Price (NSE)</div>"
                                f"<div class='metric-val mv-yellow'>{fmt_inr(ltp)}</div>"
                                f"<div style='font-size:12px;color:{chg_col};margin-top:2px'>{chg}</div>"
                                f"</div>",
                                unsafe_allow_html=True
                            )
                    with col_score:
                        st.markdown(
                            f"<div class='metric-tile' style='text-align:center'>"
                            f"<div class='metric-lbl'>Confidence</div>"
                            f"<div class='{score_color(a['score'])}'>{a['score']}</div>"
                            f"<div><span class='badge {sig_cls}'>{sig}</span></div>"
                            f"</div>",
                            unsafe_allow_html=True
                        )

                    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

                    # ── Metric tiles
                    m1, m2, m3, m4, m5 = st.columns(5)
                    tiles = [
                        (m1, "Entry Zone",    fmt_inr(a["entry"]),  "mv-yellow"),
                        (m2, "Stop Loss",     fmt_inr(a["stop"]),   "mv-red"),
                        (m3, "Target",        fmt_inr(a["target"]), "mv-green"),
                        (m4, "Risk : Reward", f"{a['rr']}:1",       "mv-green" if a["rr"] >= 2 else "mv-yellow"),
                        (m5, "Vol Surge",     f"{a['vol_surge']}x", "mv-blue"),
                    ]
                    for col, lbl, val, cls in tiles:
                        col.markdown(
                            f"<div class='metric-tile'>"
                            f"<div class='metric-lbl'>{lbl}</div>"
                            f"<div class='metric-val {cls}'>{val}</div>"
                            f"</div>",
                            unsafe_allow_html=True
                        )

                    # ── 52W info
                    st.markdown(
                        f"<div style='font-size:11px;color:#5a6175;font-family:DM Mono,monospace;margin-top:8px;'>"
                        f"52W High: <span style='color:#00d4aa'>{fmt_inr(info.get('week52_high'))}</span> &nbsp;|&nbsp; "
                        f"52W Low: <span style='color:#ff4d6d'>{fmt_inr(info.get('week52_low'))}</span> &nbsp;|&nbsp; "
                        f"Cup depth: <span style='color:#f0b429'>{a['cup_depth']}%</span> &nbsp;|&nbsp; "
                        f"Recovery: <span style='color:#f0b429'>{a['recovery']}%</span>"
                        f"</div>",
                        unsafe_allow_html=True
                    )

                    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

                    # ── Chart + Checklist
                    chart_col, check_col = st.columns([3, 1])
                    with chart_col:
                        fig = make_chart(df, a, sym, tf_label)
                        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

                    with check_col:
                        st.markdown("<div style='padding-top:20px'>", unsafe_allow_html=True)
                        st.markdown("**Pattern Checklist**")
                        for label, passed in a["checks"].items():
                            icon = "✅" if passed else "❌"
                            color = "#00d4aa" if passed else "#ff4d6d"
                            st.markdown(
                                f"<div class='chk-row'>"
                                f"<span>{icon}</span>"
                                f"<span style='color:{color};font-size:12px'>{label}</span>"
                                f"</div>",
                                unsafe_allow_html=True
                            )
                        st.markdown("</div>", unsafe_allow_html=True)

                    # ── AI Analysis
                    if run_ai:
                        ai_key = f"ai_{sym}_{tf_label}"
                        if ai_key not in st.session_state:
                            with st.spinner("🤖 Claude is analyzing this setup..."):
                                st.session_state[ai_key] = get_ai_analysis(
                                    sym, name, a, tf_label, info
                                )
                        ai_text = st.session_state[ai_key]
                        st.markdown(
                            f"<div class='ai-box'>"
                            f"<div class='ai-label'>⚡ Claude AI Analysis</div>"
                            f"<div class='ai-text'>{ai_text}</div>"
                            f"</div>",
                            unsafe_allow_html=True
                        )

# ── IDLE STATE ────────────────────────────────────────────────────────────────
else:
    st.markdown("""
    <div style='text-align:center;padding:60px 20px;'>
      <div style='font-size:48px;margin-bottom:12px;'>📈</div>
      <div style='font-size:20px;color:#f0b429;font-weight:600;margin-bottom:8px;'>
        Configure your scan in the sidebar and hit SCAN NOW
      </div>
      <div style='font-size:13px;color:#5a6175;max-width:500px;margin:0 auto;line-height:1.7;'>
        Scans Nifty 50, Midcap 50, Smallcap 50 or your watchlist for Cup & Handle patterns
        across Daily and Weekly timeframes. Powered by live NSE data via Yahoo Finance.
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── DISCLAIMER ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="disc">
  <strong style='color:#ff4d6d'>⚠ Disclaimer:</strong>
  For <strong>educational purposes only</strong>. Data via Yahoo Finance (15-min delayed).
  Pattern detection is algorithmic — always verify on live charts.
  This is NOT financial advice. Consult a SEBI-registered investment advisor before trading.
</div>
""", unsafe_allow_html=True)
