"""NIVARA AREIS — Marvel-inspired premium real estate dashboard theme.

Design references:
- Marvel cinematic palette (heroic red, gold, deep navy)
- Dribbble premium real estate dashboards (Urbanhouse, Arche, EstateRocket):
  clean cards, generous whitespace, clear hierarchy, readable typography.
"""

from __future__ import annotations

# ── Brand palette ──────────────────────────────────────────────────────────
RED = "#E62429"          # Marvel heroic red
RED_DARK = "#B91C1C"
RED_LIGHT = "#FEE2E2"
GOLD = "#F5C518"         # Marvel gold accent
NAVY = "#1B2838"         # Deep navy (not flat black)
NAVY_SOFT = "#2A3F54"
SLATE = "#64748B"
INK = "#0F172A"
BG = "#F1F5F9"           # Light premium canvas
CARD = "#FFFFFF"
BORDER = "#E2E8F0"
SUCCESS = "#16A34A"
WARNING = "#D97706"
INFO = "#2563EB"

CHART_COLORS = [RED, GOLD, NAVY, INFO, SUCCESS, "#7C3AED", "#0891B2", WARNING]

LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 88" style="width:100%;max-width:480px;height:auto">
  <defs>
    <linearGradient id="heroGrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#E62429"/>
      <stop offset="100%" stop-color="#B91C1C"/>
    </linearGradient>
  </defs>
  <rect x="0" y="12" width="56" height="64" rx="10" fill="url(#heroGrad)"/>
  <path d="M18 28 L38 28 L28 58 Z" fill="#F5C518" opacity="0.95"/>
  <rect x="10" y="20" width="36" height="4" rx="2" fill="#fff" opacity="0.25"/>
  <text x="72" y="46" font-family="'Bebas Neue', Impact, sans-serif" font-size="38" fill="#1B2838" letter-spacing="2">NIVARA</text>
  <text x="72" y="68" font-family="'Inter', sans-serif" font-size="11" fill="#64748B" letter-spacing="3" font-weight="600">AREIS · REAL ESTATE INTELLIGENCE</text>
  <rect x="72" y="74" width="120" height="3" rx="1.5" fill="#E62429"/>
</svg>"""

CSS = f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Base ── */
.stApp {{
  background: {BG} !important;
  color: {INK} !important;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}}
header, footer, [data-testid="stHeader"], [data-testid="stToolbar"] {{ display: none !important; }}
.main > div {{
  padding: 1.5rem 2rem 2.5rem !important;
  max-width: 1320px;
  margin: 0 auto;
}}
.block-container {{ padding-top: 1rem !important; }}

/* ── Hero header ── */
.hero-banner {{
  background: linear-gradient(135deg, {NAVY} 0%, {NAVY_SOFT} 55%, #1e3a5f 100%);
  border-radius: 16px;
  padding: 1.4rem 1.8rem;
  margin-bottom: 1.25rem;
  box-shadow: 0 8px 32px rgba(27, 40, 56, 0.18);
  border-bottom: 4px solid {RED};
  position: relative;
  overflow: hidden;
}}
.hero-banner::after {{
  content: '';
  position: absolute;
  top: -40%;
  right: -5%;
  width: 220px;
  height: 220px;
  background: radial-gradient(circle, rgba(230,36,41,0.15) 0%, transparent 70%);
  pointer-events: none;
}}
.hero-tag {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.65rem;
  letter-spacing: 2px;
  color: rgba(255,255,255,0.55);
  text-transform: uppercase;
  margin-bottom: 0.35rem;
}}
.hero-clock {{
  font-family: 'Bebas Neue', sans-serif;
  font-size: 1.8rem;
  color: {GOLD};
  letter-spacing: 2px;
  text-align: right;
  line-height: 1;
}}
.hero-clock-label {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.55rem;
  color: rgba(255,255,255,0.45);
  text-align: right;
  letter-spacing: 1.5px;
  text-transform: uppercase;
}}

/* ── Section labels ── */
.section-title {{
  font-family: 'Inter', sans-serif;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 1.5px;
  color: {SLATE};
  text-transform: uppercase;
  margin: 0.5rem 0 0.75rem 0;
  display: flex;
  align-items: center;
  gap: 8px;
}}
.section-title::before {{
  content: '';
  width: 3px;
  height: 14px;
  background: {RED};
  border-radius: 2px;
}}

/* ── Cards ── */
.card {{
  background: {CARD} !important;
  border: 1px solid {BORDER} !important;
  border-radius: 14px !important;
  padding: 1.1rem 1.25rem !important;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06), 0 4px 12px rgba(15, 23, 42, 0.04) !important;
  transition: box-shadow 0.2s ease, border-color 0.2s ease;
}}
.card:hover {{
  box-shadow: 0 4px 20px rgba(15, 23, 42, 0.08) !important;
  border-color: #CBD5E1 !important;
}}

/* ── KPI stat boxes ── */
.stat-card {{
  background: {CARD};
  border: 1px solid {BORDER};
  border-radius: 14px;
  padding: 1rem 1.15rem;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
  border-top: 3px solid {RED};
  min-height: 88px;
}}
.stat-card.gold {{ border-top-color: {GOLD}; }}
.stat-card.navy {{ border-top-color: {NAVY}; }}
.stat-card.green {{ border-top-color: {SUCCESS}; }}
.stat-card.blue {{ border-top-color: {INFO}; }}
.stat-card.purple {{ border-top-color: #7C3AED; }}
.stat-label {{
  font-size: 0.68rem;
  font-weight: 600;
  color: {SLATE};
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 0.25rem;
}}
.stat-value {{
  font-family: 'Bebas Neue', sans-serif;
  font-size: 1.75rem;
  color: {INK};
  letter-spacing: 0.5px;
  line-height: 1.1;
}}
.stat-value.red {{ color: {RED}; }}
.stat-value.gold {{ color: #B45309; }}
.stat-value.green {{ color: {SUCCESS}; }}
.stat-value.blue {{ color: {INFO}; }}
.stat-sub {{
  font-size: 0.65rem;
  color: #94A3B8;
  margin-top: 0.15rem;
}}

/* ── Market strip ── */
.market-chip {{
  background: {CARD};
  border: 1px solid {BORDER};
  border-radius: 12px;
  padding: 0.85rem 1rem;
  box-shadow: 0 1px 2px rgba(15,23,42,0.04);
}}
.market-chip-label {{ font-size: 0.62rem; font-weight: 600; color: {SLATE}; text-transform: uppercase; letter-spacing: 0.5px; }}
.market-chip-val {{ font-family: 'Bebas Neue', sans-serif; font-size: 1.25rem; color: {NAVY}; margin: 0.1rem 0; }}
.market-chip-sub {{ font-size: 0.62rem; color: {SUCCESS}; font-weight: 600; }}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
  gap: 6px;
  background: {CARD} !important;
  border: 1px solid {BORDER} !important;
  padding: 6px !important;
  border-radius: 14px !important;
  box-shadow: 0 1px 3px rgba(15,23,42,0.05);
}}
.stTabs [data-baseweb="tab"] {{
  font-family: 'Inter', sans-serif !important;
  font-size: 0.72rem !important;
  font-weight: 600 !important;
  color: {SLATE} !important;
  border-radius: 10px !important;
  padding: 8px 16px !important;
  background: transparent !important;
}}
.stTabs [data-baseweb="tab"]:hover {{ color: {RED} !important; background: {RED_LIGHT} !important; }}
.stTabs [aria-selected="true"] {{
  color: #fff !important;
  background: linear-gradient(135deg, {RED}, {RED_DARK}) !important;
  box-shadow: 0 2px 8px rgba(230,36,41,0.25) !important;
}}

/* ── Buttons ── */
.stButton button {{
  font-family: 'Inter', sans-serif !important;
  font-size: 0.78rem !important;
  font-weight: 600 !important;
  border-radius: 10px !important;
  padding: 0.45rem 1.1rem !important;
  background: {CARD} !important;
  color: {NAVY} !important;
  border: 1px solid {BORDER} !important;
  box-shadow: 0 1px 2px rgba(15,23,42,0.04) !important;
  transition: all 0.15s ease !important;
}}
.stButton button:hover {{
  border-color: {RED} !important;
  color: {RED} !important;
  background: {RED_LIGHT} !important;
}}
.stButton button[kind="primary"] {{
  background: linear-gradient(135deg, {RED}, {RED_DARK}) !important;
  color: #fff !important;
  border: none !important;
  box-shadow: 0 2px 10px rgba(230,36,41,0.3) !important;
}}
.stButton button[kind="primary"]:hover {{
  box-shadow: 0 4px 16px rgba(230,36,41,0.4) !important;
  transform: translateY(-1px);
}}

/* ── Pipeline nodes ── */
.pipeline-wrap {{ display: flex; align-items: center; gap: 6px; flex-wrap: wrap; padding: 0.75rem 0; }}
.node {{
  display: inline-flex; align-items: center; gap: 5px;
  padding: 6px 12px; border-radius: 20px;
  font-size: 0.62rem; font-weight: 600;
  border: 1px solid {BORDER}; background: {CARD};
  color: {SLATE};
}}
.node.done {{ background: #DCFCE7; color: {SUCCESS}; border-color: #BBF7D0; }}
.node.run {{ background: {RED_LIGHT}; color: {RED}; border-color: #FECACA; animation: pulse 1.5s infinite; }}
.node.wait {{ background: #F8FAFC; color: #CBD5E1; }}
@keyframes pulse {{ 0%,100% {{ opacity: 1; }} 50% {{ opacity: 0.7; }} }}
.pipe-arrow {{ color: #CBD5E1; font-size: 0.7rem; }}

/* ── Activity logs ── */
.log-row {{
  font-size: 0.78rem;
  padding: 0.55rem 0;
  border-bottom: 1px solid #F1F5F9;
  line-height: 1.5;
}}
.dot {{ display: inline-block; width: 7px; height: 7px; border-radius: 50%; margin-right: 8px; vertical-align: middle; }}
.dot-ok {{ background: {SUCCESS}; }}
.dot-run {{ background: {INFO}; }}
.dot-err {{ background: {RED}; }}

/* ── Chat bubbles ── */
.chat-ai {{
  background: #EFF6FF;
  border: 1px solid #BFDBFE;
  border-left: 3px solid {INFO};
  border-radius: 12px;
  padding: 0.85rem 1rem;
  margin: 6px 15% 6px 0;
}}
.chat-lead {{
  background: #FFF7ED;
  border: 1px solid #FED7AA;
  border-right: 3px solid {GOLD};
  border-radius: 12px;
  padding: 0.85rem 1rem;
  margin: 6px 0 6px 15%;
  text-align: right;
}}

/* ── Post cards ── */
.post-card {{
  background: {CARD};
  border: 1px solid {BORDER};
  border-radius: 12px;
  padding: 1rem 1.15rem;
  margin-bottom: 10px;
  box-shadow: 0 1px 2px rgba(15,23,42,0.04);
}}
.post-platform {{
  font-size: 0.68rem;
  font-weight: 700;
  color: {RED};
  text-transform: uppercase;
  letter-spacing: 0.5px;
}}
.post-meta {{ font-size: 0.62rem; color: {SLATE}; }}
.post-body {{ color: {INK}; font-size: 0.85rem; line-height: 1.55; margin: 0.4rem 0; }}
.post-reach {{ font-family: 'Bebas Neue', sans-serif; font-size: 1rem; color: {NAVY}; }}

/* ── Streamlit widgets ── */
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
.stTextArea textarea, .stTextInput input {{
  background: {CARD} !important;
  border-color: {BORDER} !important;
  border-radius: 10px !important;
  color: {INK} !important;
}}
.stProgress > div > div > div > div {{
  background: linear-gradient(90deg, {RED}, {GOLD}) !important;
}}
[data-testid="stDataFrame"] {{
  border: 1px solid {BORDER};
  border-radius: 12px;
  overflow: hidden;
}}
[data-testid="stAlert"] {{
  border-radius: 10px !important;
}}

/* ── Status badges ── */
.status-pill {{
  display: inline-block;
  padding: 0.35rem 0.75rem;
  border-radius: 20px;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.5px;
}}
.status-online {{ background: #DCFCE7; color: {SUCCESS}; }}
.status-offline {{ background: #FEE2E2; color: {RED}; }}
.status-warn {{ background: #FEF3C7; color: {WARNING}; }}

::-webkit-scrollbar {{ width: 6px; }}
::-webkit-scrollbar-track {{ background: {BG}; }}
::-webkit-scrollbar-thumb {{ background: #CBD5E1; border-radius: 3px; }}
</style>"""


def stat_card(label: str, value: str, sub: str, accent: str = "") -> str:
    accent_class = f" {accent}" if accent else ""
    val_class = f" stat-value {accent}" if accent else " stat-value"
    return (
        f'<div class="stat-card{accent_class}">'
        f'<div class="stat-label">{label}</div>'
        f'<div class="{val_class.strip()}">{value}</div>'
        f'<div class="stat-sub">{sub}</div></div>'
    )


def market_chip(label: str, value: str, sub: str) -> str:
    return (
        f'<div class="market-chip">'
        f'<div class="market-chip-label">{label}</div>'
        f'<div class="market-chip-val">{value}</div>'
        f'<div class="market-chip-sub">{sub}</div></div>'
    )


def post_card(platform: str, time_str: str, content: str, reach: int) -> str:
    return (
        f'<div class="post-card">'
        f'<div style="display:flex;justify-content:space-between;align-items:center">'
        f'<span class="post-platform">{platform}</span>'
        f'<span class="post-meta">{time_str}</span></div>'
        f'<p class="post-body">{content}</p>'
        f'<span class="post-reach">{reach:,} reach</span></div>'
    )


def plotly_layout(**kwargs) -> dict:
    base = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color=SLATE, size=11),
        margin=dict(l=10, r=10, t=24, b=10),
        height=220,
    )
    base.update(kwargs)
    return base
