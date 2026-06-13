import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
import os
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import random

st.set_page_config(page_title=u"NIVARA \u2014 AREIS", page_icon=u"\u2B21", layout="wide", initial_sidebar_state="collapsed")

LOGO_SVG = u'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 90" style="width:100%;max-width:520px;height:auto">
<defs>
<linearGradient id="cg" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#00f0ff"/><stop offset="100%" stop-color="#0066ff"/></linearGradient>
<linearGradient id="mg" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#ff0055"/><stop offset="100%" stop-color="#bd00ff"/></linearGradient>
<filter id="gl"><feGaussianBlur stdDeviation="2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<g fill="none" stroke="url(#cg)" stroke-width="1.8">
<rect x="8" y="34" width="12" height="42" rx="1.5"/>
<rect x="24" y="50" width="9" height="26" rx="1"/>
<rect x="37" y="24" width="14" height="52" rx="1.5"/>
<rect x="55" y="42" width="9" height="34" rx="1"/>
</g>
<line x1="44" y1="10" x2="44" y2="24" stroke="url(#cg)" stroke-width="1.2"/>
<circle cx="44" cy="7" r="2.5" fill="#00f0ff" filter="url(#gl)"/>
<circle cx="44" cy="7" r="1.2" fill="#fff"/>
<g fill="#00f0ff" opacity="0.6">
<rect x="11" y="40" width="3" height="2" rx="0.5"/>
<rect x="11" y="46" width="3" height="2" rx="0.5" opacity="0.4"/>
<rect x="11" y="52" width="3" height="2" rx="0.5"/>
<rect x="11" y="58" width="3" height="2" rx="0.5" opacity="0.3"/>
<rect x="40" y="32" width="4" height="2.5" rx="0.5"/>
<rect x="40" y="40" width="4" height="2.5" rx="0.5" opacity="0.7"/>
<rect x="40" y="48" width="4" height="2.5" rx="0.5"/>
<rect x="40" y="56" width="4" height="2.5" rx="0.5" opacity="0.4"/>
<rect x="47" y="32" width="4" height="2.5" rx="0.5" opacity="0.5"/>
<rect x="47" y="40" width="4" height="2.5" rx="0.5" opacity="0.8"/>
<rect x="47" y="48" width="4" height="2.5" rx="0.5" opacity="0.3"/>
</g>
<path d="M14 34 L14 16 L44 16" stroke="url(#mg)" stroke-width="0.9" fill="none" opacity="0.45"/>
<path d="M44 16 L60 16 L60 42" stroke="url(#mg)" stroke-width="0.9" fill="none" opacity="0.25"/>
<circle cx="14" cy="16" r="1.5" fill="#ff0055"/>
<circle cx="60" cy="16" r="1.5" fill="#ff0055"/>
<circle cx="44" cy="16" r="2" fill="#00f0ff" filter="url(#gl)"/>
<text x="82" y="48" font-family="'Orbitron', sans-serif" font-size="30" font-weight="900" fill="url(#cg)" letter-spacing="3">NIVARA</text>
<text x="315" y="48" font-family="'Orbitron', sans-serif" font-size="12" font-weight="600" fill="#ff0055" letter-spacing="2">\u2014 AREIS</text>
<text x="82" y="66" font-family="'JetBrains Mono', monospace" font-size="6.5" fill="rgba(255,255,255,0.12)" letter-spacing="1.5">AUTONOMOUS REAL ESTATE INTELLIGENCE SYSTEM</text>
<text x="82" y="76" font-family="'JetBrains Mono', monospace" font-size="5.5" fill="rgba(0,240,255,0.08)" letter-spacing="3">CHENNAI  \u2022  ANDHRA  \u2022  REAL ESTATE AI</text>
</svg>'''

CSS = u'''<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');
.stApp { background: #08080f !important; color: #e2e8f0 !important; font-family: 'Inter', sans-serif !important; }
header, footer { display: none !important; }
.main > div { padding: 1.2rem 2.5rem !important; max-width: 1440px; margin: 0 auto; }
.title-bar { height: 1.5px; background: linear-gradient(90deg, #00f0ff, #0066ff, transparent); margin: 0.4rem 0 0.8rem 0; border-radius: 1px; }
.glass { background: rgba(10, 12, 26, 0.55) !important; backdrop-filter: blur(14px) !important; border: 1px solid rgba(0, 240, 255, 0.08) !important; border-radius: 12px !important; padding: 1.2rem !important; box-shadow: 0 4px 20px rgba(0,0,0,0.4) !important; transition: all 0.3s ease; }
.glass:hover { border-color: rgba(0, 240, 255, 0.25) !important; }
.stat-box { background: rgba(10, 12, 26, 0.5); backdrop-filter: blur(12px); border: 1px solid rgba(0, 240, 255, 0.08); border-radius: 10px; padding: 0.7rem 1.2rem; border-left: 3px solid #00f0ff; }
.stat-box.pink { border-left-color: #ff0055; }
.stat-box.gold { border-left-color: #ffd700; }
.stat-box.purple { border-left-color: #bd00ff; }
.stat-box.green { border-left-color: #4ade80; }
.stat-label { font-family: 'JetBrains Mono', monospace; font-size: 0.5rem; color: #667; text-transform: uppercase; letter-spacing: 1.5px; }
.stat-val { font-family: 'Orbitron', sans-serif; font-size: 1.4rem; font-weight: 700; color: #00f0ff; margin: 0.05rem 0; }
.stat-sub { font-family: 'JetBrains Mono', monospace; font-size: 0.5rem; color: #445; }
.text-cyan { color: #00f0ff !important; }
.text-pink { color: #ff0055 !important; }
.text-gold { color: #ffd700 !important; }
.text-purple { color: #bd00ff !important; }
.text-green { color: #4ade80 !important; }
.stButton button { font-family: 'Orbitron', sans-serif !important; font-size: 0.65rem !important; font-weight: 500 !important; letter-spacing: 1px !important; border-radius: 8px !important; padding: 0.4rem 1rem !important; transition: all 0.3s !important; background: rgba(0, 240, 255, 0.04) !important; color: #00f0ff !important; border: 1px solid rgba(0, 240, 255, 0.15) !important; }
.stButton button:hover { background: rgba(0, 240, 255, 0.1) !important; border-color: #00f0ff !important; box-shadow: 0 0 12px rgba(0, 240, 255, 0.15) !important; }
.stButton button[kind="primary"] { background: linear-gradient(135deg, rgba(0, 240, 255, 0.12), rgba(0, 102, 255, 0.08)) !important; border-color: rgba(0, 240, 255, 0.25) !important; }
.stButton button[kind="primary"]:hover { background: linear-gradient(135deg, rgba(0, 240, 255, 0.2), rgba(0, 102, 255, 0.12)) !important; box-shadow: 0 0 18px rgba(0, 240, 255, 0.25) !important; }
.stTabs [data-baseweb="tab-list"] { gap: 4px; background: rgba(5, 6, 12, 0.4) !important; border: 1px solid rgba(0, 240, 255, 0.06) !important; padding: 4px !important; border-radius: 10px !important; }
.stTabs [data-baseweb="tab"] { font-family: 'Orbitron', sans-serif !important; font-size: 0.65rem !important; font-weight: 700 !important; letter-spacing: 1px !important; color: rgba(255, 255, 255, 0.3) !important; border-radius: 6px !important; padding: 6px 14px !important; border: 1px solid transparent !important; }
.stTabs [data-baseweb="tab"]:hover { color: #00f0ff !important; }
.stTabs [aria-selected="true"] { color: #fff !important; background: rgba(0, 240, 255, 0.1) !important; border-color: rgba(0, 240, 255, 0.3) !important; box-shadow: 0 0 8px rgba(0, 240, 255, 0.1) !important; }
.node { display: inline-flex; align-items: center; gap: 4px; padding: 4px 8px; border-radius: 6px; font-family: 'JetBrains Mono', monospace; font-size: 0.5rem; font-weight: 700; text-transform: uppercase; border: 1px solid rgba(255,255,255,0.04); }
.node.done { background: rgba(0,240,255,0.06); color: #00f0ff; border-color: rgba(0,240,255,0.2); }
.node.run { background: rgba(255,0,85,0.08); color: #ff0055; border-color: #ff0055; animation: pulse 1.5s infinite; }
.node.wait { background: transparent; color: rgba(255,255,255,0.1); }
@keyframes pulse { 0%,100% { opacity: 0.7; box-shadow: 0 0 6px rgba(255,0,85,0.1); } 50% { opacity: 1; box-shadow: 0 0 14px rgba(255,0,85,0.3); } }
.chat-bot { background: rgba(0,240,255,0.05); border: 1px solid rgba(0,240,255,0.12); border-left: 3px solid #00f0ff; margin-right: 20%; border-radius: 10px; padding: 0.7rem; margin: 5px 0; }
.chat-lead { background: rgba(255,0,85,0.05); border: 1px solid rgba(255,0,85,0.12); border-right: 3px solid #ff0055; margin-left: 20%; border-radius: 10px; padding: 0.7rem; margin: 5px 0; text-align: right; }
.log-line { font-family: 'JetBrains Mono', monospace; font-size: 0.6rem; padding: 4px 0; border-bottom: 1px solid rgba(255,255,255,0.015); }
.dot { display: inline-block; width: 6px; height: 6px; border-radius: 50%; margin-right: 5px; }
.dg { background: #4ade80; box-shadow: 0 0 6px rgba(74,222,128,0.4); }
.db { background: #00f0ff; box-shadow: 0 0 6px rgba(0,240,255,0.4); animation: blink 1.5s infinite; }
.dr { background: #ff0055; box-shadow: 0 0 6px rgba(255,0,85,0.4); }
.dy { background: #ffd700; box-shadow: 0 0 6px rgba(255,215,0,0.4); }
@keyframes blink { 0%,100% { opacity: 1; } 50% { opacity: 0.3; } }
.section-label { font-family: 'JetBrains Mono', monospace; font-size: 0.5rem; letter-spacing: 2px; color: #445; text-transform: uppercase; }
div[data-baseweb="select"] > div { background: rgba(10,12,26,0.9) !important; border-color: rgba(0,240,255,0.08) !important; border-radius: 6px !important; }
.stProgress > div > div > div { background: linear-gradient(90deg, #00f0ff, #0066ff) !important; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #08080f; }
::-webkit-scrollbar-thumb { background: rgba(0,240,255,0.15); border-radius: 2px; }
.clock { font-family: 'Orbitron', monospace; font-size: 1.2rem; color: rgba(0,240,255,0.5); letter-spacing: 4px; text-align: right; }
.clock-label { font-family: 'JetBrains Mono', monospace; font-size: 0.5rem; color: #334; letter-spacing: 2px; text-transform: uppercase; text-align: right; }
.market-box { background: rgba(10,12,26,0.3); border: 1px solid rgba(0,240,255,0.04); border-radius: 8px; padding: 0.5rem 1rem; }
.market-label { font-family: 'JetBrains Mono', monospace; font-size: 0.45rem; color: #556; text-transform: uppercase; letter-spacing: 1.5px; }
.market-val { font-family: 'Orbitron', monospace; font-size: 0.8rem; color: #00f0ff; }
.market-sub { font-family: 'JetBrains Mono', monospace; font-size: 0.45rem; color: #445; }
</style>'''

BG = u'''<canvas id="bg" style="position:fixed;top:0;left:0;width:100%;height:100%;z-index:-1;pointer-events:none"></canvas>
<div style="position:fixed;top:0;left:0;width:100%;height:100%;z-index:-0.9;pointer-events:none;background:linear-gradient(180deg,rgba(8,8,15,0.92) 0%,rgba(8,8,15,0.15) 25%,transparent 40%,transparent 60%,rgba(8,8,15,0.15) 75%,rgba(8,8,15,0.92) 100%)"></div>
<div style="position:fixed;top:0;left:0;width:100%;height:3px;z-index:-0.8;pointer-events:none;background:linear-gradient(90deg,transparent,#00f0ff,transparent);opacity:0.15"></div>
<script>
(function(){
  var c=document.getElementById('bg'),ctx=c.getContext('2d');
  var w=c.width=window.innerWidth,h=c.height=window.innerHeight;
  window.addEventListener('resize',function(){w=c.width=window.innerWidth;h=c.height=window.innerHeight});
  var t=0;
  function anim(){
    t+=0.003;
    ctx.clearRect(0,0,w,h);
    var vx=w/2,vy=h*0.25;
    ctx.strokeStyle='rgba(0,240,255,0.025)';
    ctx.lineWidth=0.7;
    for(var y=h;y>vy;){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(w,y);ctx.stroke();y-=Math.pow((y-vy)/(h-vy),0.5)*38+2.5;}
    for(var x=-w;x<w*2;x+=45){ctx.beginPath();ctx.moveTo(vx,vy);ctx.lineTo(x,h);ctx.stroke();}
    ctx.strokeStyle='rgba(255,0,85,0.012)';
    var ox=Math.sin(t)*15;
    for(var y=h;y>vy;){ctx.beginPath();ctx.moveTo(ox,y);ctx.lineTo(w+ox,y);ctx.stroke();y-=Math.pow((y-vy)/(h-vy),0.5)*45+3;}
    for(var i=0;i<4;i++){var x=vx+Math.sin(t+i*1.5)*(w*0.25);var g=ctx.createRadialGradient(x,vy,0,x,vy,25);g.addColorStop(0,'rgba(0,240,255,0.035)');g.addColorStop(1,'transparent');ctx.fillStyle=g;ctx.beginPath();ctx.arc(x,vy,25,0,Math.PI*2);ctx.fill();}
    requestAnimationFrame(anim);
  }
  anim();
})();
</script>'''

DB_HOST = os.environ.get("DB_HOST", "postgres")
DB_PORT = int(os.environ.get("DB_PORT", "5432"))
ORCH_URL = os.environ.get("ORCHESTRATOR_URL", "http://host.docker.internal:8005")
VEO_URL = os.environ.get("VEO_MCP_URL", "http://host.docker.internal:8006")

def db():
    try: return psycopg2.connect(host=DB_HOST, port=DB_PORT, database="nivara", user="nivara", password="changeme", cursor_factory=RealDictCursor)
    except: return None

def q(sql, p=None, one=False):
    c = db()
    if not c: return None if one else []
    try:
        with c.cursor() as cur:
            cur.execute(sql, p)
            return cur.fetchone() if one else cur.fetchall()
    except: return None if one else []
    finally: c.close()

RE_AGENTS = [
    ("MarketAnalyst", "Analyzing Chennai property market trends", "Market report: OMR prices up 11% YoY, ECR demand rising"),
    ("CompetitorSpy", "Scanning competitor real estate listings", "3 new competitor projects detected in Sholinganallur"),
    ("ContentStrategist", "Generating luxury property content", "Content calendar for Q3 luxury segment created"),
    ("SEOAgent", "Optimizing property pages for search", "12 property keywords now rank in top 20"),
    ("SocialMediaManager", "Scheduling property showcase posts", "Posts scheduled across Facebook, Instagram, LinkedIn"),
    ("VisualDesigner", "Generating cinematic videos from site photos", "Gemini Veo videos created for property listings"),
    ("LeadQualification", "Scoring incoming property inquiries", "2 hot leads, 3 warm leads identified"),
    ("WhatsAppAgent", "Sending property recommendations", "Campaign delivered to 38 contacts, 12 replies"),
    ("AppointmentScheduler", "Scheduling site visits", "4 site visits confirmed for this week"),
    ("CRM", "Syncing lead data to PostgreSQL", "CRM synchronized \u2014 7 records updated"),
    ("Analytics", "Compiling performance metrics", "Dashboard metrics refreshed, 15% MoM growth"),
    ("CEO", "Reviewing market strategy", "Strategy report: focus on OMR corridor approved"),
]

RE_POSTS = [
    ("instagram", "Premium 3BHK apartments in OMR Chennai with world-class amenities. Starting at \u20b989L. DM for virtual tour! #ChennaiRealEstate #LuxuryLiving", (2500, 35000)),
    ("facebook", "New launch alert! Sholinganallur luxury villas with panoramic lake views. Pre-launch prices from \u20b91.8Cr. Register Now!", (5000, 55000)),
    ("linkedin", "Chennai real estate Q2 2026: Residential prices up 12% YoY. OMR leads at 23% appreciation. Commercial occupancy at 87%. Download full report.", (3000, 28000)),
    ("twitter", "Breaking: Chennai Metro Phase 2 driving 23% price appreciation in surrounding areas. Top investment zones inside \u2192", (1200, 18000)),
    ("instagram", "Weekend open house! 4BHK duplex in gated community, Velachery. Premium finishes, clubhouse access. 9 AM - 6 PM Sun.", (1800, 22000)),
    ("facebook", "Attention investors! Commercial plots in Andhra's new development corridor. 20% below market rate. Limited inventory.", (4000, 42000)),
]

RE_CHAT = [
    ("whatsapp", "Project brochure request", "Hi, I saw the OMR project online. Can you send me the brochure and price list?", "lead"),
    ("whatsapp", "Brochure sent with pricing", "Sure! Here's the detailed brochure with all floor plans and pricing options for our OMR luxury project.", "ai"),
    ("whatsapp", "Site visit interest", "The 3BHK looks great. Can I schedule a site visit this weekend?", "lead"),
    ("whatsapp", "Site visit confirmed", "Absolutely! I've scheduled you for Saturday at 11 AM. Our team will show you the sample flat and amenities.", "ai"),
    ("whatsapp", "EMI options question", "What are the EMI options available for the 2BHK configuration?", "lead"),
    ("whatsapp", "EMI plan shared", "We have tie-ups with SBI, HDFC, and ICICI. For a 2BHK at \u20b989L, EMI starts at \u20b978,000/month for 20 years.", "ai"),
    ("whatsapp", "Budget clarification", "My budget is around \u20b965L. Any options in that range?", "lead"),
    ("whatsapp", "Budget options sent", "Yes! We have premium 2BHK options starting at \u20b963L in our new phase. Let me send you the available inventory.", "ai"),
]

def simulate_activity():
    conn = db()
    if not conn: return
    cur = conn.cursor()
    try:
        cur.execute("SELECT MAX(timestamp) AS t FROM bot_logs")
        r = cur.fetchone()
        latest = r["t"] if r and r["t"] else datetime.min
        if isinstance(latest, datetime) and (datetime.now() - latest).total_seconds() < 25:
            return

        base = datetime.now() - timedelta(seconds=len(RE_AGENTS) * 7)
        for i, (agent, start_detail, end_detail) in enumerate(RE_AGENTS):
            t1 = base + timedelta(seconds=i * 7)
            cur.execute("INSERT INTO bot_logs(agent_name,action,status,details,timestamp) VALUES(%s,%s,%s,%s,%s)",
                        (agent, "Starting task", "processing", start_detail, t1))
            cur.execute("INSERT INTO bot_logs(agent_name,action,status,details,timestamp) VALUES(%s,%s,%s,%s,%s)",
                        (agent, "Task completed", "success", end_detail, t1 + timedelta(seconds=3)))

        cur.execute("UPDATE leads SET score = LEAST(100, score + floor(random() * 6 + 1)::int) WHERE random() < 0.35")
        cur.execute("UPDATE leads SET status = 'nurturing' WHERE score >= 50 AND status = 'new' AND random() < 0.3")
        cur.execute("UPDATE leads SET status = 'qualified' WHERE score >= 70 AND status = 'nurturing' AND random() < 0.25")

        p = random.choice(RE_POSTS)
        cur.execute("INSERT INTO social_posts(platform,content,reach,published_at) VALUES(%s,%s,%s,now())",
                    (p[0], p[1], random.randint(p[2][0], p[2][1])))

        cur.execute("SELECT id, full_name FROM leads ORDER BY random() LIMIT 1")
        lead = cur.fetchone()
        if lead:
            msg = random.choice(RE_CHAT)
            cur.execute("INSERT INTO crm_activity(lead_id,activity_type,title,description,performed_by,agent_name) VALUES(%s,%s,%s,%s,%s,'WhatsAppAgent')",
                        (lead["id"], msg[0], msg[1], msg[2], msg[3]))

        conn.commit()
    except:
        conn.rollback()
    finally:
        conn.close()

st.markdown(CSS, unsafe_allow_html=True)
st.markdown(BG, unsafe_allow_html=True)

simulate_activity()

# ── Header ──
h1, h2 = st.columns([3, 1])
with h1:
    st.markdown(f'<div style="margin-top:0.2rem">{LOGO_SVG}</div>', unsafe_allow_html=True)
with h2:
    st.markdown('<div class="clock-label">SYSTEM TIME</div>', unsafe_allow_html=True)
    st.markdown('<div id="clock" class="clock">--:--:--</div>', unsafe_allow_html=True)
    st.markdown('<div class="clock-label" style="margin-top:2px">CHENNAI / IST</div>', unsafe_allow_html=True)

st.markdown('<div class="title-bar"></div>', unsafe_allow_html=True)

# ── Market Overview ──
st.markdown('<div class="section-label" style="margin-bottom:6px">MARKET OVERVIEW</div>', unsafe_allow_html=True)
m1, m2, m3, m4 = st.columns(4)
market_data = [
    ("Chennai Avg. Price", "\u20b97,850/sq.ft", "+12.3% YoY"),
    ("Active Listings", "14,820", "+8% vs Q1"),
    ("Demand Index", "87.4", "High Demand"),
    ("Hot Corridor", "OMR Phase 2", "+23% appreciation"),
]
for i, (mcol, (label, val, sub)) in enumerate(zip([m1, m2, m3, m4], market_data)):
    with mcol:
        st.markdown(f'<div class="market-box"><div class="market-label">{label}</div><div class="market-val">{val}</div><div class="market-sub">{sub}</div></div>', unsafe_allow_html=True)

# ── Stats ──
lq = q("SELECT count(*) c FROM leads", one=True)
hq = q("SELECT count(*) c FROM leads WHERE score >= 70", one=True)
pq = q("SELECT count(*) c FROM social_posts", one=True)
bq = q("SELECT count(*) c FROM bot_logs", one=True)
aq = q("SELECT COALESCE(AVG(score),0)::int a FROM leads", one=True)
cq = q("SELECT count(*) c FROM leads WHERE status='converted'", one=True)
rq = q("SELECT COALESCE(SUM(reach),0) r FROM social_posts", one=True)
tq = q("SELECT count(*) c FROM crm_activity", one=True)

stats = [
    (lq["c"], "Total Leads", "Active targets", "cyan", ""),
    (hq["c"], "Hot Leads", "Score \u2265 70", "pink", "pink"),
    (f'{aq["a"]}', "Avg Score", "Lead quality", "gold", "gold"),
    (cq["c"], "Converted", "Deals closed", "green", "green"),
    (pq["c"], "Posts", "Published", "gold", "gold"),
    (f'{rq["r"]:,}', "Total Reach", "Social impressions", "purple", "purple"),
    (bq["c"], "Agent Runs", "Executions", "cyan", ""),
    (tq["c"], "CRM Actions", "Activities", "green", "green"),
]

s1, s2, s3, s4 = st.columns(4)
s5, s6, s7, s8 = st.columns(4)
all_cols = [s1, s2, s3, s4, s5, s6, s7, s8]
for col, (val, label, sub, color, extra) in zip(all_cols, stats):
    css_class = f"stat-box {extra}" if extra else "stat-box"
    with col:
        st.markdown(f'<div class="{css_class}"><div class="stat-label" style="color:#{ {"pink":"ff0055","gold":"ffd700","green":"4ade80","purple":"bd00ff"}.get(color, "00f0ff") }">{label}</div><div class="stat-val text-{color}">{val}</div><div class="stat-sub">{sub}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs ──
t1, t2, t3, t4, t5, t6, t7 = st.tabs([u"\u26A1 ACTIVITY", u"\U0001F6F8 PIPELINE", u"\U0001F4E1 SOCIAL", u"\U0001F3AC MEDIA", u"\U0001F4AC CHAT", u"\U0001F4CA LEADS", u"\u2699 SETTINGS"])

# ═══ TAB 1 ═══
with t1:
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1: sf = st.selectbox("", ["All", "success", "processing", "error"], label_visibility="collapsed")
    with c2: af = st.selectbox("", ["All", "MarketAnalyst","CompetitorSpy","ContentStrategist","SEOAgent","VisualDesigner","SocialMediaManager","LeadQualification","WhatsAppAgent","AppointmentScheduler","CRM","Analytics","CEO"], label_visibility="collapsed")
    with c3:
        if st.button(u"\u27F3 REFRESH"): st.rerun()
    sql = "SELECT * FROM bot_logs WHERE 1=1"; pr = []
    if sf != "All": sql += " AND status=%s"; pr.append(sf)
    if af != "All": sql += " AND agent_name=%s"; pr.append(af)
    sql += " ORDER BY timestamp DESC LIMIT 60"
    logs = q(sql, tuple(pr))
    if logs:
        for r in logs:
            dc = "dg" if r["status"]=="success" else "dr" if r["status"]=="error" else "db"
            cc = "#4ade80" if r["status"]=="success" else "#ff0055" if r["status"]=="error" else "#00f0ff"
            detail = r.get("details", "") or ""
            st.markdown(f'<div class="log-line"><span class="dot {dc}"></span><span style="color:#445;margin-right:8px">[{r["timestamp"].strftime("%H:%M:%S")}]</span><span style="font-family:Orbitron;color:#00f0ff;font-weight:700;margin-right:8px">{r["agent_name"].upper()}</span><span style="color:{cc};font-weight:500;margin-right:10px">{r["action"]}</span><span style="color:rgba(255,255,255,0.45)">{detail[:120]}</span></div>', unsafe_allow_html=True)
    else:
        st.info("No activity logs found. Pipeline will auto-generate data.")

# ═══ TAB 2 ═══
with t2:
    agents = ["MarketAnalyst","CompetitorSpy","ContentStrategist","SEOAgent","VisualDesigner","SocialMediaManager","LeadQualification","WhatsAppAgent","AppointmentScheduler","CRM","Analytics","CEO"]
    pl = q("SELECT agent_name,action,status,timestamp FROM bot_logs WHERE timestamp>=COALESCE((SELECT MAX(timestamp) FROM bot_logs WHERE agent_name='MarketAnalyst' AND action='Starting task'),now()-interval'1 hour') ORDER BY timestamp ASC")
    done = set(); running = None
    if pl:
        for r in pl:
            if r["action"]=="Starting task": running = r["agent_name"]
            elif r["action"]=="Task completed": done.add(r["agent_name"]); running = None if running==r["agent_name"] else running
    st.markdown('<div style="display:flex;align-items:center;gap:5px;flex-wrap:wrap;padding:0.6rem 0">', unsafe_allow_html=True)
    for i, a in enumerate(agents):
        cls = "done" if a in done else "run" if a==running else "wait"
        ico = u"\u2B22" if a in done else u"\u2394" if a==running else u"\u2B21"
        st.markdown(f'<span class="node {cls}">{ico} {a[:10]}</span>', unsafe_allow_html=True)
        if i < len(agents)-1: st.markdown('<span style="color:rgba(0,240,255,0.1);font-size:0.6rem;margin:0 -2px">\u2192</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    if done or running:
        pct = len(done)/len(agents); st.progress(min(pct, 1.0))
        st.markdown(f'<p style="font-family:JetBrains Mono;font-size:0.6rem;color:#556;text-align:center;margin:0.3rem 0">{len(done)}/{len(agents)} agents complete \u2014 {int(pct*100)}%</p>', unsafe_allow_html=True)
    else:
        st.info("Run pipeline from Settings tab, or wait for auto-simulation.")
    st.markdown("<br>", unsafe_allow_html=True)

    # Pipeline duration chart
    t = q("SELECT agent_name,MIN(CASE WHEN action='Starting task' THEN timestamp END)s,MAX(CASE WHEN action='Task completed' THEN timestamp END)f FROM bot_logs WHERE action IN('Starting task','Task completed') AND timestamp>now()-interval'1 hour' GROUP BY agent_name ORDER BY MAX(timestamp) ASC")
    if t:
        rows = []; [rows.append({"Agent":r["agent_name"],"Duration_s":(r["f"]-r["s"]).total_seconds()}) for r in t if r["s"] and r["f"]]
        if rows:
            df = pd.DataFrame(rows)
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df["Agent"], y=df["Duration_s"],
                marker=dict(color="#00f0ff", line=dict(color="#00f0ff", width=0.8)),
                text=[f"{s:.0f}s" for s in df["Duration_s"]], textposition="outside", textfont=dict(color="#00f0ff", size=9)
            ))
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(family="JetBrains Mono",color="#86868b",size=9),margin=dict(l=10,r=10,t=10,b=20),height=200,xaxis=dict(showgrid=False),yaxis=dict(showgrid=True,gridcolor="rgba(0,240,255,0.05)",title="Seconds"))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ═══ TAB 3 ═══
with t3:
    c1, c2 = st.columns([1, 4])
    with c1:
        pf = st.selectbox("", ["All","facebook","instagram","linkedin","twitter"], label_visibility="collapsed")
        if st.button("+ NEW POST", type="primary"): st.session_state.f = True
        if st.button("SIMULATE POST"): st.session_state.sim_post = True
    with c2:
        if st.session_state.get("f"):
            with st.container(border=True):
                with st.form("np"):
                    bc1, bc2 = st.columns(2)
                    with bc1: pl = st.selectbox("Platform", ["facebook","instagram","linkedin","twitter"])
                    with bc2: rch = st.number_input("Reach", 500, 500000, 10000, step=1000)
                    ct = st.text_area("Content", height=80)
                    if st.form_submit_button("PUBLISH", type="primary"):
                        q("INSERT INTO social_posts(platform,content,reach,published_at)VALUES(%s,%s,%s,now())", (pl, ct, rch), one=True)
                        st.success("Published!"); st.session_state.f = False; st.rerun()

    if st.session_state.get("sim_post"):
        p = random.choice(RE_POSTS)
        q("INSERT INTO social_posts(platform,content,reach,published_at)VALUES(%s,%s,%s,now())", (p[0], p[1], random.randint(p[2][0], p[2][1])), one=True)
        st.session_state.sim_post = False
        st.rerun()

    sql = "SELECT * FROM social_posts"; p2 = []
    if pf != "All": sql += " WHERE platform=%s"; p2.append(pf)
    sql += " ORDER BY published_at DESC"
    posts = q(sql, tuple(p2))
    if posts:
        for p in posts:
            st.markdown(f'<div class="glass" style="margin-bottom:8px"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px"><span style="font-family:Orbitron;color:#00f0ff;font-size:0.65rem">{p["platform"].upper()}</span><span style="font-family:JetBrains Mono;font-size:0.5rem;color:#445">{p["published_at"].strftime("%d %b %H:%M")}</span></div><p style="color:#c8d6e5;line-height:1.4;font-size:0.8rem">{p["content"]}</p><div style="margin-top:4px;display:flex;gap:20px;font-size:0.7rem"><span style="font-family:Orbitron;color:#ff0055">{p["reach"]:,} <span style="font-family:JetBrains Mono;font-size:0.45rem;color:#445">REACH</span></span></div></div>', unsafe_allow_html=True)
    else:
        st.info("No posts yet. Click SIMULATE POST to generate one.")

# ═══ TAB 4 — MEDIA (Gemini Veo Photo → Video) ═══
with t4:
    st.markdown('<div class="section-label">Site Photo → Gemini Veo Video → Social Post</div>', unsafe_allow_html=True)
    import base64
    import requests as req

    projects = q("SELECT id, name, location_city FROM projects WHERE is_active=true ORDER BY name")
    proj_options = {f"{p['name']} ({p['location_city']})": str(p['id']) for p in projects} if projects else {}

    col_up, col_gen = st.columns([1, 1])
    with col_up:
        st.markdown("**1. Upload Site Photo**")
        uploaded = st.file_uploader("Choose property photo", type=["jpg", "jpeg", "png", "webp"])
        proj_sel = st.selectbox("Project", ["— None —"] + list(proj_options.keys())) if proj_options else None
        project_id = proj_options.get(proj_sel) if proj_sel and proj_sel != "— None —" else None

        if uploaded and st.button("UPLOAD PHOTO", type="primary"):
            try:
                files = {"file": (uploaded.name, uploaded.getvalue(), uploaded.type)}
                data = {}
                if project_id:
                    data["project_id"] = project_id
                r = req.post(f"{VEO_URL}/upload", files=files, data=data, timeout=60)
                if r.ok:
                    result = r.json()
                    st.session_state["last_media_asset"] = result.get("result", {})
                    st.session_state["last_photo_url"] = result.get("public_url", "")
                    st.success(f"Uploaded! Asset ID: {result.get('result', {}).get('id', 'N/A')}")
                else:
                    st.error(f"Upload failed: {r.status_code} {r.text[:200]}")
            except Exception as e:
                st.error(f"Upload error: {e}")

    with col_gen:
        st.markdown("**2. Generate Video & Post**")
        motion_prompt = st.text_area(
            "Video motion prompt",
            value="Smooth cinematic camera pan across this luxury property, golden hour lighting, gentle breeze",
            height=80,
        )
        caption = st.text_area(
            "Social post caption",
            value="Experience luxury living with NIVARA REALTY 🏙️ #ChennaiRealEstate #LuxuryLiving",
            height=60,
        )
        platforms = st.multiselect("Platforms", ["instagram", "facebook", "linkedin"], default=["instagram", "facebook"])

        if st.button("🎬 GENERATE VIDEO & POST", type="primary"):
            asset = st.session_state.get("last_media_asset", {})
            asset_id = str(asset.get("id", ""))
            if not asset_id:
                st.error("Upload a site photo first.")
            else:
                try:
                    with st.spinner("Generating video with Gemini Veo (may take 2-5 min)..."):
                        r = req.post(
                            f"{VEO_URL}/call",
                            json={
                                "name": "photo_to_video",
                                "arguments": {
                                    "media_asset_id": asset_id,
                                    "prompt": motion_prompt,
                                    "project_id": project_id,
                                    "auto_publish": True,
                                    "platforms": platforms,
                                    "post_caption": caption,
                                },
                            },
                            timeout=600,
                        )
                    if r.ok:
                        data = r.json().get("result", {})
                        st.success(f"Video created: {data.get('video_url', 'N/A')}")
                        pub = data.get("publish_results", [])
                        if pub:
                            st.json(pub)
                        st.rerun()
                    else:
                        st.error(f"Generation failed: {r.status_code} {r.text[:300]}")
                except Exception as e:
                    st.error(f"Error: {e}")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">Media Library</div>', unsafe_allow_html=True)
    media = q("SELECT id, asset_type, status, source_url, output_url, prompt, created_at FROM media_assets ORDER BY created_at DESC LIMIT 20")
    if media:
        for m in media:
            url = m.get("output_url") or m.get("source_url") or ""
            st.markdown(
                f'<div class="glass" style="margin-bottom:6px">'
                f'<span style="font-family:Orbitron;color:#00f0ff;font-size:0.6rem">{m["asset_type"].upper()} — {m["status"].upper()}</span>'
                f'<p style="font-size:0.7rem;color:#667;margin:2px 0">{m.get("prompt","")[:100]}</p>'
                f'<p style="font-size:0.6rem;color:#445">{url[:80]}</p></div>',
                unsafe_allow_html=True,
            )
    else:
        st.info("No media assets yet. Upload a site photo to get started.")

# ═══ TAB 5 — CHAT ═══
with t5:
    c1, c2 = st.columns([3, 2])
    with c1:
        st.markdown('<div class="section-label">Conversation Feed</div>', unsafe_allow_html=True)
        ch = q("SELECT ca.*,l.full_name FROM crm_activity ca LEFT JOIN leads l ON l.id=ca.lead_id WHERE ca.activity_type='whatsapp' ORDER BY ca.created_at ASC LIMIT 30")
        if ch:
            for c in ch:
                bot = c.get("performed_by")=="ai"; nm = c.get("full_name") or "Lead"
                title = c.get("title") or ""
                desc = c.get("description") or ""
                if bot:
                    st.markdown(f'<div class="chat-bot"><span style="font-family:JetBrains Mono;font-size:0.45rem;color:#445">AI AGENT</span><br><span style="font-size:0.8rem;font-weight:500">{title}</span><br><span style="font-size:0.65rem;color:#667">{desc[:150]}</span></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-lead"><span style="font-family:JetBrains Mono;font-size:0.45rem;color:#445">{nm}</span><br><span style="font-size:0.8rem;font-weight:500">{title}</span><br><span style="font-size:0.65rem;color:#667">{desc[:150]}</span></div>', unsafe_allow_html=True)
        else:
            st.info("No conversations yet. Auto-simulation will generate chat data.")
    with c2:
        st.markdown('<div class="section-label">Send Message</div>', unsafe_allow_html=True)
        leads = q("SELECT id,full_name,phone FROM leads ORDER BY score DESC")
        if leads:
            with st.form("sw"):
                ls = st.selectbox("Lead", [f"{l['full_name']} ({l['phone']})" for l in leads])
                dr = st.selectbox("Direction", ["Lead \u2192 AI","AI \u2192 Lead"])
                msg = st.text_area("Message", height=80)
                if st.form_submit_button("SEND", type="primary"):
                    idx = [f"{l['full_name']} ({l['phone']})" for l in leads].index(ls)
                    lid = leads[idx]["id"]; p = "lead" if "Lead" in dr else "ai"
                    q("INSERT INTO crm_activity(lead_id,activity_type,title,description,performed_by,agent_name)VALUES(%s,'whatsapp',%s,%s,%s,'Manual')", (lid, msg, f"Message to {leads[idx]['full_name']}", p), one=True)
                    st.success("Sent!"); st.rerun()
        else:
            st.info("No leads in database.")

# ═══ TAB 6 — LEADS ═══
with t6:
    c1, c2 = st.columns(2)
    with c1: sf2 = st.selectbox("", ["All","new","contacted","qualified","nurturing","negotiating","converted","lost"], label_visibility="collapsed")
    with c2: sb = st.selectbox("", ["Score \u2193","Score \u2191","Name A-Z","Newest"], label_visibility="collapsed")
    sql = "SELECT full_name,phone,email,score,status,ai_qualification_notes FROM leads WHERE 1=1"; p3 = []
    if sf2 != "All": sql += " AND status=%s"; p3.append(sf2)
    sql += {"Score \u2193":" ORDER BY score DESC","Score \u2191":" ORDER BY score ASC","Name A-Z":" ORDER BY full_name ASC","Newest":" ORDER BY created_at DESC"}.get(sb, " ORDER BY score DESC")
    leads = q(sql, tuple(p3))
    if leads:
        df = pd.DataFrame(leads)
        st.dataframe(df, use_container_width=True, hide_index=True, column_config={"full_name":"Name","phone":"Phone","email":"Email","score":st.column_config.NumberColumn("Score",format="%d"),"status":"Status","ai_qualification_notes":"Notes"})
        st.markdown("<br>", unsafe_allow_html=True)
        g1, g2, g3 = st.columns(3)
        with g1:
            bins=[0,30,50,70,85,101];labels=["Cold","Warm","Interested","Hot","Ready"]
            df["b"]=pd.cut(df["score"],bins=bins,labels=labels,right=False)
            d=df["b"].value_counts().reindex(labels,fill_value=0).reset_index()
            fig=px.pie(d,values="count",names="b",color_discrete_sequence=["#ff0055","#ffd700","#00f0ff","#bd00ff","#4ade80"])
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",font=dict(family="Inter",color="#86868b",size=9),margin=dict(l=10,r=10,t=10,b=10),height=200)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        with g2:
            sd=df["status"].value_counts().reset_index()
            fig=px.bar(sd,x="status",y="count",color_discrete_sequence=["#00f0ff"])
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(family="Inter",color="#86868b",size=9),margin=dict(l=10,r=10,t=10,b=10),height=200,xaxis=dict(showgrid=False),yaxis=dict(showgrid=True,gridcolor="rgba(0,240,255,0.05)"))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        with g3:
            funnel_stages = ["new","contacted","qualified","nurturing","negotiating","converted"]
            funnel_vals = []
            for s in funnel_stages:
                v = df[df["status"]==s].shape[0]
                funnel_vals.append(v if v else 1)
            fig = go.Figure(go.Funnel(
                y=funnel_stages, x=funnel_vals,
                textposition="inside", textinfo="value",
                marker=dict(color=["#ff0055","#ffd700","#00f0ff","#bd00ff","#4ade80","#0066ff"])
            ))
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",font=dict(family="Inter",color="#86868b",size=9),margin=dict(l=10,r=10,t=10,b=10),height=200,showlegend=False)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("No leads found.")

# ═══ TAB 7 — SETTINGS ═══
with t7:
    st.markdown('<div class="section-label">Pipeline Controls</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button(u"\u25B6 FULL PIPELINE", type="primary"):
            try:
                import requests
                r = requests.post(f"{ORCH_URL}/orchestrate", json={"task":"daily_market_analysis","region":"Chennai"}, timeout=600)
                st.success("Pipeline launched!") if r.ok else st.error(f"Failed: {r.status_code}")
                st.rerun()
            except Exception as e: st.error(f"Connection error: {e}")
    with c2:
        if st.button(u"\u27F3 HEALTH CHECK"):
            try:
                import requests
                r = requests.get(f"{ORCH_URL}/health", timeout=10); d = r.json()
                st.success(f"Ollama: {d['ollama']} | DB: {d['supabase_configured']}")
            except Exception as e: st.error(f"Unreachable: {e}")
    with c3:
        if st.button(u"\u2715 CLEAR LOGS"): q("DELETE FROM bot_logs", one=True); st.success("Cleared!"); st.rerun()
    with c4:
        if st.button(u"\u27F3 REFRESH"): st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">Manual Agent Dispatch</div>', unsafe_allow_html=True)
    aa = ["MarketAnalyst","CompetitorSpy","ContentStrategist","SEOAgent","VisualDesigner","SocialMediaManager","LeadQualification","WhatsAppAgent","AppointmentScheduler","CRM","Analytics","CEO"]
    ac = st.columns(4)
    for i, a in enumerate(aa):
        with ac[i%4]:
            if st.button(f"RUN {a}", key=f"r_{a}"):
                try:
                    import requests
                    r = requests.post(f"{ORCH_URL}/orchestrate", json={"task":"daily_market_analysis","region":"Chennai","agents":[a]}, timeout=120)
                    st.success(f"{a} complete") if r.ok else st.error(f"{a} failed")
                    st.rerun()
                except Exception as e: st.error(str(e))
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">System Status</div>', unsafe_allow_html=True)
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        ok = db()
        st.markdown(f'<div class="glass" style="text-align:center"><div class="stat-label" style="color:#00f0ff">POSTGRES</div><div style="font-family:Orbitron;font-size:0.85rem;margin:0.2rem 0;color:{"#4ade80" if ok else "#ff0055"}">{"\u25CF ONLINE" if ok else "\u25CF OFFLINE"}</div></div>', unsafe_allow_html=True)
    with s2:
        try:
            import requests; r = requests.get(f"{ORCH_URL}/health", timeout=5)
            st.markdown(f'<div class="glass" style="text-align:center"><div class="stat-label" style="color:#ff0055">ORCHESTRATOR</div><div style="font-family:Orbitron;font-size:0.85rem;margin:0.2rem 0;color:{"#4ade80" if r.ok else "#ff0055"}">{"\u25CF ONLINE" if r.ok else "\u25CF ERROR"}</div></div>', unsafe_allow_html=True)
        except: st.markdown(f'<div class="glass" style="text-align:center"><div class="stat-label" style="color:#ff0055">ORCHESTRATOR</div><div style="font-family:Orbitron;font-size:0.85rem;margin:0.2rem 0;color:#ffd700">\u25CF UNREACHABLE</div></div>', unsafe_allow_html=True)
    with s3:
        try:
            import requests; r = requests.get("http://host.docker.internal:11434/api/tags", timeout=5)
            st.markdown(f'<div class="glass" style="text-align:center"><div class="stat-label" style="color:#ffd700">OLLAMA</div><div style="font-family:Orbitron;font-size:0.85rem;margin:0.2rem 0;color:{"#4ade80" if r.ok else "#ff0055"}">{"\u25CF ONLINE" if r.ok else "\u25CF ERROR"}</div></div>', unsafe_allow_html=True)
        except: st.markdown(f'<div class="glass" style="text-align:center"><div class="stat-label" style="color:#ffd700">OLLAMA</div><div style="font-family:Orbitron;font-size:0.85rem;margin:0.2rem 0;color:#ffd700">\u25CF UNREACHABLE</div></div>', unsafe_allow_html=True)
    with s4:
        st.markdown(f'<div class="glass" style="text-align:center"><div class="stat-label" style="color:#667">DASHBOARD</div><div style="font-family:Orbitron;font-size:0.85rem;margin:0.2rem 0;color:#4ade80">\u25CF ACTIVE</div></div>', unsafe_allow_html=True)

# ── Clock JS ──
st.markdown(u'''<script>
(function(){var e=document.getElementById('clock');if(!e)return;
function u(){var n=new Date();e.textContent=n.toTimeString().split(' ')[0]}
u();setInterval(u,1000)})();
</script>
<style>
@keyframes horizonPulse{0%,100%{opacity:0.08}50%{opacity:0.15}}
</style>
<meta http-equiv="refresh" content="20">
''', unsafe_allow_html=True)

# ── Seed demo data on first run ──
def seed_demo():
    conn = db()
    if not conn: return
    cur = conn.cursor()
    try:
        cur.execute("SELECT count(*) c FROM leads")
        rc = cur.fetchone()
        if rc and rc["c"] > 0: return

        names = [
            ("Arun Kumar", "+91-9884012345", "arun.k@email.com", 82, "qualified", "High budget, looking for 3BHK in OMR"),
            ("Priya Sharma", "+91-9845678901", "priya.s@email.com", 45, "new", "First time buyer, budget under 1Cr"),
            ("Rajesh Patel", "+91-9876543210", "rajesh.p@email.com", 91, "negotiating", "VIP client, interested in luxury villa"),
            ("Sneha Reddy", "+91-9988776655", "sneha.r@email.com", 38, "contacted", "Looking for 2BHK near Velachery"),
            ("Vikram Singh", "+91-9765432109", "vikram.s@email.com", 73, "nurturing", "NRI investor, comparing multiple projects"),
            ("Ananya Gupta", "+91-9654321876", "ananya.g@email.com", 28, "new", "Student, parents looking for investment"),
            ("Karthik Nair", "+91-9543218765", "karthik.n@email.com", 67, "nurturing", "Looking for 3BHK, budget 1.2-1.5Cr"),
            ("Divya Krishnan", "+91-9432187654", "divya.k@email.com", 55, "qualified", "Interested in ECR property, sea view"),
            ("Suresh Babu", "+91-9321876543", "suresh.b@email.com", 88, "converted", "Booked 3BHK in OMR Phase 2"),
            ("Lakshmi Narayan", "+91-9218765432", "lakshmi.n@email.com", 15, "lost", "Low budget, not responding"),
        ]
        for n, ph, em, sc, sts, nt in names:
            cur.execute("INSERT INTO leads(full_name,phone,email,score,status,ai_qualification_notes) VALUES(%s,%s,%s,%s,%s,%s)", (n, ph, em, sc, sts, nt))

        for i, (agent, s_detail, e_detail) in enumerate(RE_AGENTS):
            t = datetime.now() - timedelta(minutes=len(RE_AGENTS)-i, seconds=random.randint(10, 50))
            cur.execute("INSERT INTO bot_logs(agent_name,action,status,details,timestamp) VALUES(%s,%s,%s,%s,%s)", (agent, "Starting task", "processing", s_detail, t))
            cur.execute("INSERT INTO bot_logs(agent_name,action,status,details,timestamp) VALUES(%s,%s,%s,%s,%s)", (agent, "Task completed", "success", e_detail, t + timedelta(seconds=random.randint(3, 15))))

        for p in RE_POSTS[:3]:
            cur.execute("INSERT INTO social_posts(platform,content,reach,published_at) VALUES(%s,%s,%s,now()-interval'1 day'*random())", (p[0], p[1], random.randint(p[2][0], p[2][1])))

        conn.commit()
    except:
        conn.rollback()
    finally:
        conn.close()

seed_demo()
