import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
import os
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import random

from theme import CSS, LOGO_SVG, CHART_COLORS, RED, RED_DARK, NAVY, GOLD, SLATE, plotly_layout, stat_card, market_chip, post_card
from config import (
    DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD,
    ORCH_URL, VEO_URL, OLLAMA_URL, DEFAULT_REGION,
    connection_config, password_is_placeholder,
    ENABLE_DASHBOARD_SIMULATION, orchestrator_headers,
    AUTO_SYNC_PIPELINE, AUTO_SYNC_INTERVAL_MINUTES,
    GROQ_API_KEY, GEMINI_API_KEY,
)
from pipeline_sync import (
    PIPELINE_AGENTS,
    LEGACY_12_AGENTS,
    auto_sync_pipeline,
    latest_cycle_completed,
    needs_immediate_sync,
)
from safe_data import val as _val, text as _text, fmt_dt as _fmt_dt, trunc as _trunc

APP_BUILD = "2026-06-13j"

AGENT_SIM_DETAILS: dict[str, tuple[str, str]] = {
    "MarketAnalyst": ("Analyzing Bangalore property market trends", "Market report: Whitefield prices up 9% YoY"),
    "RegulatoryWatch": ("Checking Karnataka RERA and BBMP compliance", "All active projects RERA-registered"),
    "LocationScout": ("Scouting Whitefield, Sarjapur, North Bangalore", "Electronic City and HSR top demand zones"),
    "CompetitorSpy": ("Scanning competitor real estate listings", "4 new competitor launches in Whitefield"),
    "CMO": ("Defining brand positioning and campaign themes", "Bangalore luxury positioning approved"),
    "ContentStrategist": ("Generating luxury property content", "Q3 Bangalore content calendar created"),
    "Copywriter": ("Writing ad copy and nurture sequences", "Meta/Google ad variants ready"),
    "SEOAgent": ("Optimizing property pages for search", "14 Bangalore keywords in top 20"),
    "VisualDesigner": ("Generating cinematic videos from site photos", "Gemini Veo videos created"),
    "SocialMediaManager": ("Scheduling property showcase posts", "Posts scheduled on FB, IG, LinkedIn"),
    "PaidAdsManager": ("Optimizing Google and Meta ad spend", "Budget rebalanced for Bangalore corridors"),
    "LeadQualification": ("Scoring incoming property inquiries", "3 hot leads, 2 warm leads identified"),
    "SalesCoach": ("Preparing objection handling scripts", "Site-visit closing playbook updated"),
    "WhatsAppAgent": ("Sending property recommendations", "Campaign delivered to 42 contacts"),
    "EmailMarketer": ("Sending drip campaigns and newsletters", "Welcome sequence queued for 6 leads"),
    "AppointmentScheduler": ("Scheduling site visits", "5 site visits confirmed this week"),
    "CRM": ("Syncing lead data to PostgreSQL", "CRM synchronized — 8 records updated"),
    "Analytics": ("Compiling performance metrics", "Dashboard metrics refreshed, 18% MoM growth"),
    "COO": ("Reviewing agent SLAs and bottlenecks", "Lead follow-up SLA at 94%"),
    "CEO": ("Reviewing market strategy", "Focus on Whitefield-Sarjapur corridor approved"),
}

RE_AGENTS = [
    (name, AGENT_SIM_DETAILS.get(name, (f"Running {name}", f"{name} completed"))[0],
     AGENT_SIM_DETAILS.get(name, (f"Running {name}", f"{name} completed"))[1])
    for name in PIPELINE_AGENTS
]

st.set_page_config(page_title="NIVARA — AREIS", page_icon="🏢", layout="wide", initial_sidebar_state="collapsed")

_last_db_error: str | None = None

def db():
    global _last_db_error
    try:
        return psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            cursor_factory=RealDictCursor,
            sslmode="require",
            connect_timeout=15,
        )
    except Exception as exc:
        _last_db_error = str(exc)
        return None

def q(sql, p=None, one=False):
    c = db()
    if not c:
        return None if one else []
    try:
        with c.cursor() as cur:
            cur.execute(sql, p)
            return cur.fetchone() if one else cur.fetchall()
    except Exception:
        return None if one else []
    finally:
        c.close()

RE_POSTS = [
    ("instagram", "Premium 3BHK apartments in Whitefield Bangalore with world-class amenities. Starting at \u20b91.2Cr. DM for virtual tour! #BangaloreRealEstate #LuxuryLiving", (2800, 38000)),
    ("facebook", "New launch alert! Sarjapur Road luxury villas with lake views. Pre-launch prices from \u20b92.1Cr. Register Now!", (5200, 58000)),
    ("linkedin", "Bangalore real estate Q2 2026: Residential prices up 10% YoY. North Bangalore leads at 18% appreciation. Commercial occupancy at 89%. Download full report.", (3200, 30000)),
    ("twitter", "Breaking: Namma Metro Phase 3 driving 18% price appreciation in surrounding corridors. Top Bangalore investment zones inside \u2192", (1400, 20000)),
    ("instagram", "Weekend open house! 4BHK duplex in gated community, HSR Layout. Premium finishes, clubhouse access. 9 AM - 6 PM Sun.", (2000, 24000)),
    ("facebook", "Attention investors! Plotted developments on Devanahalli corridor. 15% below comparable market rate. Limited inventory.", (4100, 44000)),
]

RE_CHAT = [
    ("whatsapp", "Project brochure request", "Hi, I saw the Whitefield project online. Can you send me the brochure and price list?", "lead"),
    ("whatsapp", "Brochure sent with pricing", "Sure! Here's the detailed brochure with all floor plans and pricing options for our Whitefield luxury project.", "ai"),
    ("whatsapp", "Site visit interest", "The 3BHK looks great. Can I schedule a site visit this weekend?", "lead"),
    ("whatsapp", "Site visit confirmed", "Absolutely! I've scheduled you for Saturday at 11 AM. Our team will show you the sample flat and amenities.", "ai"),
    ("whatsapp", "EMI options question", "What are the EMI options available for the 2BHK configuration?", "lead"),
    ("whatsapp", "EMI plan shared", "We have tie-ups with SBI, HDFC, and ICICI. For a 2BHK at \u20b91.1Cr, EMI starts at \u20b986,000/month for 20 years.", "ai"),
    ("whatsapp", "Budget clarification", "My budget is around \u20b980L. Any options in that range?", "lead"),
    ("whatsapp", "Budget options sent", "Yes! We have premium 2BHK options starting at \u20b978L in our Electronic City phase. Let me send you the available inventory.", "ai"),
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

        base = datetime.now() - timedelta(seconds=len(PIPELINE_AGENTS) * 7)
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

_db_ok = db() is not None
if not _db_ok:
    cfg = connection_config()
    if cfg["password_placeholder"]:
        st.error(
            "**Database password not configured.** Streamlit is still using a placeholder "
            "(`your-password` / `changeme`), not your real Supabase password.\n\n"
            "1. Open [share.streamlit.io](https://share.streamlit.io) → your app → **Settings → Secrets**\n"
            "2. Paste the block below with your **real** database password\n"
            "3. Click **Save**, then **Reboot app** (⋮ menu → Reboot app)\n\n"
            "Secrets must be **flat TOML** (no `export`, no `.env` format):"
        )
    else:
        st.error(
            "**Database connection failed** with the credentials currently loaded from "
            f"**{cfg['source']}**.\n\n"
            f"- Host: `{cfg['host']}`\n"
            f"- User: `{cfg['user']}`\n"
            f"- Database: `{cfg['database']}`\n"
            f"- Password: {cfg['password_preview']}\n\n"
            f"Error: `{_last_db_error or 'unknown'}`\n\n"
            "Use the **pooler** host `aws-1-ap-south-1.pooler.supabase.com` and user "
            "`postgres.mxjhwjxxqtkwsrwtqwuc` (not plain `postgres`)."
        )
    with st.expander("Copy-paste secrets template (replace YOUR_REAL_PASSWORD)"):
        st.code(
            'SUPABASE_URL = "https://mxjhwjxxqtkwsrwtqwuc.supabase.co"\n'
            'DB_HOST = "aws-1-ap-south-1.pooler.supabase.com"\n'
            'DB_PORT = "5432"\n'
            'DB_NAME = "postgres"\n'
            'DB_USER = "postgres.mxjhwjxxqtkwsrwtqwuc"\n'
            'DB_PASSWORD = "YOUR_REAL_PASSWORD"\n'
            'ORCHESTRATOR_URL = "https://nivara-orchestrator.onrender.com"\n'
            'VEO_MCP_URL = "https://nivara-veo-mcp.onrender.com"',
            language="toml",
        )
elif _db_ok and ENABLE_DASHBOARD_SIMULATION:
    simulate_activity()

_pipeline_sync_status: dict | None = None
if _db_ok and AUTO_SYNC_PIPELINE and not ENABLE_DASHBOARD_SIMULATION:
    _should_sync, _sync_reason = needs_immediate_sync(q)
    _session_cooldown = st.session_state.get("_pipeline_sync_at")
    _cooldown_ok = (
        not _session_cooldown
        or (datetime.now() - _session_cooldown).total_seconds() > 300
    )
    if _should_sync and _cooldown_ok:
        st.session_state["_pipeline_sync_at"] = datetime.now()
        with st.spinner(f"Auto-syncing 20-agent pipeline ({_sync_reason})…"):
            _pipeline_sync_status = auto_sync_pipeline(
                q,
                db_host=DB_HOST,
                db_port=DB_PORT,
                db_name=DB_NAME,
                db_user=DB_USER,
                db_password=DB_PASSWORD,
                default_region=DEFAULT_REGION,
                orch_url=ORCH_URL,
                orch_headers=orchestrator_headers(),
                interval_minutes=AUTO_SYNC_INTERVAL_MINUTES,
                prefer_direct=True,
                groq_api_key=GROQ_API_KEY,
                gemini_api_key=GEMINI_API_KEY,
            )

# ── Hero header ──
if _pipeline_sync_status and _pipeline_sync_status.get("synced"):
    st.success(
        f"Pipeline auto-synced: **{_pipeline_sync_status['agents_completed']}/"
        f"{_pipeline_sync_status['agents_expected']}** agents "
        f"via {_pipeline_sync_status.get('mode', 'direct')} mode."
    )
elif _pipeline_sync_status and _pipeline_sync_status.get("error"):
    st.warning(f"Pipeline auto-sync attempted but failed: {_pipeline_sync_status['error'][:120]}")

h1, h2 = st.columns([3, 1])
with h1:
    st.markdown(
        '<div class="hero-banner">'
        '<div class="hero-tag">Bangalore · Karnataka · Autonomous Real Estate AI · '
        f'Build {APP_BUILD}</div>'
        f'{LOGO_SVG}'
        '</div>',
        unsafe_allow_html=True,
    )
with h2:
    st.markdown(
        '<div class="hero-banner" style="text-align:right;padding:1.8rem 1.4rem">'
        '<div class="hero-clock-label">System Time · IST</div>'
        '<div id="clock" class="hero-clock">--:--:--</div>'
        '<div class="hero-clock-label" style="margin-top:6px">20 AI Agents Active</div>'
        '</div>',
        unsafe_allow_html=True,
    )

# ── Market Overview ──
st.markdown('<div class="section-title">Market Overview</div>', unsafe_allow_html=True)
m1, m2, m3, m4 = st.columns(4)
market_data = [
    ("Bangalore Avg. Price", "\u20b98,200/sq.ft", "+10.1% YoY"),
    ("Active Listings", "18,450", "+11% vs Q1"),
    ("Demand Index", "89.2", "High Demand"),
    ("Hot Corridor", "Whitefield", "+18% appreciation"),
]
for i, (mcol, (label, val, sub)) in enumerate(zip([m1, m2, m3, m4], market_data)):
    with mcol:
        st.markdown(market_chip(label, val, sub), unsafe_allow_html=True)

# ── Stats ──
st.markdown('<div class="section-title">Performance Metrics</div>', unsafe_allow_html=True)
lq = q("SELECT count(*) c FROM leads", one=True)
hq = q("SELECT count(*) c FROM leads WHERE score >= 70", one=True)
pq = q("SELECT count(*) c FROM social_posts", one=True)
bq = q("SELECT count(*) c FROM bot_logs", one=True)
aq = q("SELECT COALESCE(AVG(score),0)::int a FROM leads", one=True)
cq = q("SELECT count(*) c FROM leads WHERE status='converted'", one=True)
rq = q("SELECT COALESCE(SUM(reach),0) r FROM social_posts", one=True)
tq = q("SELECT count(*) c FROM crm_activity", one=True)

stats = [
    (_val(lq, "c"), "Total Leads", "Active targets", "red"),
    (_val(hq, "c"), "Hot Leads", "Score ≥ 70", "red"),
    (str(_val(aq, "a")), "Avg Score", "Lead quality", "gold"),
    (_val(cq, "c"), "Converted", "Deals closed", "green"),
    (_val(pq, "c"), "Posts", "Published", "gold"),
    (f'{_val(rq, "r"):,}', "Total Reach", "Social impressions", "navy"),
    (_val(bq, "c"), "Agent Runs", "Executions", "blue"),
    (_val(tq, "c"), "CRM Actions", "Activities", "green"),
]

s1, s2, s3, s4 = st.columns(4)
s5, s6, s7, s8 = st.columns(4)
all_cols = [s1, s2, s3, s4, s5, s6, s7, s8]
for col, (val, label, sub, accent) in zip(all_cols, stats):
    with col:
        st.markdown(stat_card(label, val, sub, accent), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs ──
t1, t2, t3, t4, t5, t6, t7 = st.tabs([
    "Activity", "Pipeline", "Social", "Media", "Chat", "Leads", "Settings"
])

# ═══ TAB 1 ═══
with t1:
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1: sf = st.selectbox("", ["All", "success", "processing", "error"], label_visibility="collapsed", key="filter_status")
    with c2: af = st.selectbox("", ["All"] + PIPELINE_AGENTS, label_visibility="collapsed", key="filter_agent")
    with c3:
        if st.button(u"\u27F3 REFRESH", key="refresh_activity"): st.rerun()
    sql = "SELECT * FROM bot_logs WHERE 1=1"; pr = []
    if sf != "All": sql += " AND status=%s"; pr.append(sf)
    if af != "All": sql += " AND agent_name=%s"; pr.append(af)
    sql += " ORDER BY timestamp DESC LIMIT 60"
    logs = q(sql, tuple(pr))
    if logs:
        for r in logs:
            detail = _text(r, "details", "", 120)
            ts = _fmt_dt(r.get("timestamp"), "%H:%M:%S")
            agent = _text(r, "agent_name", "Unknown")
            action = _text(r, "action", "")
            status = _text(r, "status", "")
            dot = "dot-ok" if status == "success" else "dot-err" if status == "error" else "dot-run"
            status_color = "#16A34A" if status == "success" else RED if status == "error" else "#2563EB"
            st.markdown(
                f'<div class="log-row"><span class="dot {dot}"></span>'
                f'<span style="color:{SLATE};margin-right:8px">[{ts}]</span>'
                f'<span style="font-weight:700;color:{NAVY};margin-right:8px">{agent}</span>'
                f'<span style="color:{status_color};font-weight:600;margin-right:10px">{action}</span>'
                f'<span style="color:#475569">{detail}</span></div>',
                unsafe_allow_html=True,
            )
    else:
        st.info("No activity logs found. Pipeline will auto-generate data.")

# ═══ TAB 2 ═══
with t2:
    agents = PIPELINE_AGENTS
    pl = q("SELECT agent_name,action,status,timestamp FROM bot_logs WHERE timestamp>=COALESCE((SELECT MAX(timestamp) FROM bot_logs WHERE agent_name='MarketAnalyst' AND action='Starting task'),now()-interval'1 hour') ORDER BY timestamp ASC")
    done = set(); running = None
    if pl:
        for r in pl:
            if r["action"]=="Starting task": running = r["agent_name"]
            elif r["action"]=="Task completed": done.add(r["agent_name"]); running = None if running==r["agent_name"] else running

    orch_agent_count = None
    try:
        import requests
        hr = requests.get(f"{ORCH_URL}/health", timeout=8)
        if hr.ok:
            orch_agent_count = hr.json().get("agent_count")
    except Exception:
        pass

    if orch_agent_count is not None and orch_agent_count < len(agents):
        st.error(
            f"**Orchestrator at `{ORCH_URL}` is running an old {orch_agent_count}-agent build**, "
            f"not the current 20-agent pipeline. Redeploy Render (`nivara-orchestrator`) from latest `main`, "
            "then run **Settings → ▶ FULL PIPELINE** again."
        )
    elif len(done) == 12 and done == LEGACY_12_AGENTS:
        missing = [a for a in agents if a not in done]
        st.error(
            "**Latest pipeline run used the legacy 12-agent graph** (Render not redeployed). "
            f"Missing agents: {', '.join(missing)}. "
            "Redeploy `nivara-orchestrator` on Render from latest `main`, then re-run the full pipeline."
        )

    st.markdown('<div class="pipeline-wrap">', unsafe_allow_html=True)
    for i, a in enumerate(agents):
        cls = "done" if a in done else "run" if a == running else "wait"
        st.markdown(f'<span class="node {cls}">{a}</span>', unsafe_allow_html=True)
        if i < len(agents) - 1:
            st.markdown('<span class="pipe-arrow">→</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    if done or running:
        pct = len(done) / len(agents)
        st.progress(min(pct, 1.0))
        pending = [a for a in agents if a not in done and a != running]
        st.markdown(
            f'<p style="font-size:0.75rem;color:{SLATE};text-align:center;margin:0.4rem 0">'
            f'{len(done)}/{len(agents)} agents complete — {int(pct * 100)}%</p>',
            unsafe_allow_html=True,
        )
        if pending:
            st.warning(
                f"**{len(pending)} agents not yet run** in the latest cycle: {', '.join(pending)}. "
                "If this stays at 12/20 after a full pipeline run, your Render orchestrator needs redeploying."
            )
    else:
        st.info("No recent pipeline activity. Run **Settings → ▶ FULL PIPELINE** to start all 20 agents.")
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
                marker=dict(color=RED, line=dict(color=RED_DARK, width=0.5)),
                text=[f"{s:.0f}s" for s in df["Duration_s"]], textposition="outside",
                textfont=dict(color=NAVY, size=10),
            ))
            fig.update_layout(
                **plotly_layout(height=200),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="#F1F5F9", title="Seconds"),
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ═══ TAB 3 ═══
with t3:
    c1, c2 = st.columns([1, 4])
    with c1:
        pf = st.selectbox("", ["All","facebook","instagram","linkedin","twitter"], label_visibility="collapsed", key="filter_platform")
        if st.button("+ NEW POST", type="primary", key="new_post"): st.session_state.f = True
        if st.button("SIMULATE POST", key="sim_post"): st.session_state.sim_post = True
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
            st.markdown(
                post_card(
                    _text(p, "platform", "unknown").upper(),
                    _fmt_dt(p.get("published_at")),
                    _text(p, "content", ""),
                    _val(p, "reach", 0),
                ),
                unsafe_allow_html=True,
            )
    else:
        st.info("No posts yet. Click SIMULATE POST to generate one.")

# ═══ TAB 4 — MEDIA (Gemini Veo Photo → Video) ═══
with t4:
    st.markdown('<div class="section-title">Site Photo → Gemini Veo Video → Social Post</div>', unsafe_allow_html=True)
    import base64
    import requests as req

    projects = q("SELECT id, name, location_city FROM projects WHERE is_active=true ORDER BY name")
    proj_options = {
        f"{_text(p, 'name', 'Project')} ({_text(p, 'location_city', DEFAULT_REGION)})": str(_val(p, "id", ""))
        for p in projects
        if _val(p, "id", "")
    } if projects else {}

    col_up, col_gen = st.columns([1, 1])
    with col_up:
        st.markdown("**1. Upload Site Photo**")
        uploaded = st.file_uploader("Choose property photo", type=["jpg", "jpeg", "png", "webp"])
        proj_sel = st.selectbox("Project", ["— None —"] + list(proj_options.keys())) if proj_options else None
        project_id = proj_options.get(proj_sel) if proj_sel and proj_sel != "— None —" else None

        if uploaded and st.button("UPLOAD PHOTO", type="primary", key="upload_photo"):
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
            value="Experience luxury living with NIVARA REALTY 🏙️ #BangaloreRealEstate #LuxuryLiving",
            height=60,
        )
        platforms = st.multiselect("Platforms", ["instagram", "facebook", "linkedin"], default=["instagram", "facebook"])

        if st.button("🎬 GENERATE VIDEO & POST", type="primary", key="generate_video"):
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
    st.markdown('<div class="section-title">Media Library</div>', unsafe_allow_html=True)
    try:
        media = q(
            "SELECT id, asset_type, status, source_url, output_url, "
            "COALESCE(prompt, '') AS prompt, created_at "
            "FROM media_assets ORDER BY created_at DESC LIMIT 20"
        )
        if media:
            for m in media:
                url = _text(m, "output_url") or _text(m, "source_url")
                prompt = _text(m, "prompt", "", 100)
                asset_type = _text(m, "asset_type", "unknown").upper()
                status = _text(m, "status", "unknown").upper()
                st.markdown(
                    f'<div class="card" style="margin-bottom:8px">'
                    f'<span style="font-size:0.72rem;font-weight:700;color:{RED}">'
                    f'{asset_type} — {status}</span>'
                    f'<p style="font-size:0.8rem;color:{SLATE};margin:4px 0">{prompt}</p>'
                    f'<p style="font-size:0.7rem;color:#94A3B8">{_trunc(url, 80)}</p></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("No media assets yet. Upload a site photo to get started.")
    except Exception as exc:
        st.warning(f"Media library could not load: {exc}")

# ═══ TAB 5 — CHAT ═══
with t5:
    c1, c2 = st.columns([3, 2])
    with c1:
        st.markdown('<div class="section-title">Conversation Feed</div>', unsafe_allow_html=True)
        ch = q("SELECT ca.*,l.full_name FROM crm_activity ca LEFT JOIN leads l ON l.id=ca.lead_id WHERE ca.activity_type='whatsapp' ORDER BY ca.created_at ASC LIMIT 30")
        if ch:
            for c in ch:
                bot = c.get("performed_by") == "ai"
                nm = _text(c, "full_name", "Lead")
                title = _text(c, "title", "")
                desc = _text(c, "description", "", 150)
                if bot:
                    st.markdown(
                        f'<div class="chat-ai"><span style="font-size:0.65rem;color:{SLATE};font-weight:600">AI AGENT</span><br>'
                        f'<span style="font-size:0.85rem;font-weight:600;color:{NAVY}">{title}</span><br>'
                        f'<span style="font-size:0.78rem;color:{SLATE}">{desc}</span></div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f'<div class="chat-lead"><span style="font-size:0.65rem;color:{SLATE};font-weight:600">{nm}</span><br>'
                        f'<span style="font-size:0.85rem;font-weight:600;color:{NAVY}">{title}</span><br>'
                        f'<span style="font-size:0.78rem;color:{SLATE}">{desc}</span></div>',
                        unsafe_allow_html=True,
                    )
        else:
            st.info("No conversations yet. Auto-simulation will generate chat data.")
    with c2:
        st.markdown('<div class="section-title">Send Message</div>', unsafe_allow_html=True)
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
    with c1: sf2 = st.selectbox("", ["All","new","contacted","qualified","nurturing","negotiating","converted","lost"], label_visibility="collapsed", key="filter_lead_status")
    with c2: sb = st.selectbox("", ["Score \u2193","Score \u2191","Name A-Z","Newest"], label_visibility="collapsed", key="sort_leads")
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
            fig=px.pie(d,values="count",names="b",color_discrete_sequence=CHART_COLORS[:5])
            fig.update_layout(**plotly_layout())
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        with g2:
            sd=df["status"].value_counts().reset_index()
            fig=px.bar(sd,x="status",y="count",color_discrete_sequence=[RED])
            fig.update_layout(**plotly_layout(), xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#F1F5F9"))
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
                marker=dict(color=CHART_COLORS[:6])
            ))
            fig.update_layout(**plotly_layout(), showlegend=False)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("No leads found.")

# ═══ TAB 7 — SETTINGS ═══
with t7:
    st.markdown('<div class="section-title">Pipeline Controls</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button(u"\u25B6 FULL PIPELINE", type="primary", key="full_pipeline"):
            try:
                import requests
                r = requests.post(
                    f"{ORCH_URL}/orchestrate",
                    json={
                        "task": "daily_market_analysis",
                        "region": DEFAULT_REGION,
                        "agents": PIPELINE_AGENTS,
                    },
                    headers=orchestrator_headers(),
                    timeout=900,
                )
                if r.ok:
                    ran = len(r.json().get("agent_outputs", {}))
                    st.success(f"Pipeline launched — {ran}/{len(PIPELINE_AGENTS)} agents returned output.")
                else:
                    st.error(f"Failed: {r.status_code} — {r.text[:200]}")
                st.rerun()
            except Exception as e: st.error(f"Connection error: {e}")
    with c2:
        if st.button(u"\u27F3 HEALTH CHECK", key="health_check"):
            try:
                import requests
                r = requests.get(f"{ORCH_URL}/health", timeout=10)
                d = r.json()
                st.success(
                    f"Agents: {d.get('agent_count', '?')}/20 | "
                    f"LLM: {d.get('llm_provider', '?')} | "
                    f"DB: {d.get('supabase_configured')} | "
                    f"Auth: {d.get('api_auth_enabled')}"
                )
            except Exception as e: st.error(f"Unreachable: {e}")
    with c3:
        if st.button(u"\u2715 CLEAR LOGS", key="clear_logs"): q("DELETE FROM bot_logs", one=True); st.success("Cleared!"); st.rerun()
    with c4:
        if st.button(u"\u27F3 REFRESH", key="refresh_settings"): st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">Manual Agent Dispatch</div>', unsafe_allow_html=True)
    aa = PIPELINE_AGENTS
    ac = st.columns(4)
    for i, a in enumerate(aa):
        with ac[i%4]:
            if st.button(f"RUN {a}", key=f"r_{a}"):
                try:
                    import requests
                    r = requests.post(
                        f"{ORCH_URL}/orchestrate",
                        json={"task": "daily_market_analysis", "region": DEFAULT_REGION, "agents": [a]},
                        headers=orchestrator_headers(),
                        timeout=120,
                    )
                    st.success(f"{a} complete") if r.ok else st.error(f"{a} failed")
                    st.rerun()
                except Exception as e: st.error(str(e))
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">Database & Secrets</div>', unsafe_allow_html=True)
    cfg = connection_config()
    st.markdown(
        f"| Setting | Value |\n|---|---|\n"
        f"| Secrets source | **{cfg['source']}** |\n"
        f"| DB host | `{cfg['host']}` |\n"
        f"| DB user | `{cfg['user']}` |\n"
        f"| DB name | `{cfg['database']}` |\n"
        f"| Password loaded | **{'Yes' if cfg['password_set'] else 'NO — still placeholder'}** |\n"
        f"| Supabase URL set | {'Yes' if cfg['supabase_url_set'] else 'No'} |\n"
        f"| Build | `{APP_BUILD}` |\n"
        f"| Demo simulation | **{'On' if ENABLE_DASHBOARD_SIMULATION else 'Off (production)'}** |\n"
        f"| Auto pipeline sync | **{'On' if AUTO_SYNC_PIPELINE else 'Off'}** (every {AUTO_SYNC_INTERVAL_MINUTES} min via cron) |"
    )
    if AUTO_SYNC_PIPELINE:
        done_now = latest_cycle_completed(q)
        st.caption(
            f"Pipeline status: {len(done_now)}/{len(PIPELINE_AGENTS)} agents in latest cycle. "
            "Incomplete pipelines auto-sync on dashboard load; stale pipelines sync every 6h via GitHub Actions."
        )
    if cfg["password_placeholder"]:
        st.warning(
            "Password is still a placeholder. In Streamlit **Settings → Secrets**, set "
            "`DB_PASSWORD = \"your-actual-supabase-password\"` then **Reboot app**."
        )
    if st.button("Test database connection", key="test_db"):
        conn = db()
        if conn:
            conn.close()
            st.success("Database connection OK!")
        else:
            st.error(f"Connection failed: {_last_db_error or 'unknown error'}")
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">System Status</div>', unsafe_allow_html=True)
    s1, s2, s3, s4 = st.columns(4)

    def status_card(name: str, online: bool | None) -> str:
        if online is True:
            pill, label = "status-online", "● Online"
        elif online is False:
            pill, label = "status-offline", "● Offline"
        else:
            pill, label = "status-warn", "● Unreachable"
        return (
            f'<div class="card" style="text-align:center">'
            f'<div class="stat-label">{name}</div>'
            f'<div class="status-pill {pill}" style="margin-top:0.5rem">{label}</div></div>'
        )

    with s1:
        st.markdown(status_card("PostgreSQL", bool(db())), unsafe_allow_html=True)
    with s2:
        try:
            import requests
            r = requests.get(f"{ORCH_URL}/health", timeout=10)
            d = r.json() if r.ok else {}
            online = r.ok and d.get("db_connected", False)
            st.markdown(status_card("Orchestrator", online), unsafe_allow_html=True)
            if r.ok and not d.get("db_connected"):
                st.caption("Orchestrator up but DB not connected — set DB_SSLMODE=require on Render")
        except Exception:
            st.markdown(status_card("Orchestrator", None), unsafe_allow_html=True)
    with s3:
        ollama_url = OLLAMA_URL
        try:
            import requests
            r = requests.get(f"{ollama_url}/api/tags", timeout=5)
            st.markdown(status_card("Ollama", r.ok), unsafe_allow_html=True)
        except Exception:
            st.markdown(status_card("Ollama", None), unsafe_allow_html=True)
    with s4:
        st.markdown(status_card("Dashboard", True), unsafe_allow_html=True)

# ── Clock JS ──
st.markdown('''<script>
(function(){var e=document.getElementById('clock');if(!e)return;
function u(){var n=new Date();e.textContent=n.toTimeString().split(' ')[0]}
u();setInterval(u,1000)})();
</script>
<meta http-equiv="refresh" content="30">
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
            ("Arun Kumar", "+91-9884012345", "arun.k@email.com", 82, "qualified", "High budget, looking for 3BHK in Whitefield"),
            ("Priya Sharma", "+91-9845678901", "priya.s@email.com", 45, "new", "First time buyer, budget under 1.2Cr"),
            ("Rajesh Patel", "+91-9876543210", "rajesh.p@email.com", 91, "negotiating", "VIP client, interested in luxury villa"),
            ("Sneha Reddy", "+91-9988776655", "sneha.r@email.com", 38, "contacted", "Looking for 2BHK near HSR Layout"),
            ("Vikram Singh", "+91-9765432109", "vikram.s@email.com", 73, "nurturing", "NRI investor, comparing multiple projects"),
            ("Ananya Gupta", "+91-9654321876", "ananya.g@email.com", 28, "new", "Student, parents looking for investment"),
            ("Karthik Nair", "+91-9543218765", "karthik.n@email.com", 67, "nurturing", "Looking for 3BHK, budget 1.5-1.8Cr"),
            ("Divya Krishnan", "+91-9432187654", "divya.k@email.com", 55, "qualified", "Interested in Sarjapur property, gated community"),
            ("Suresh Babu", "+91-9321876543", "suresh.b@email.com", 88, "converted", "Booked 3BHK in Whitefield"),
            ("Lakshmi Narayan", "+91-9218765432", "lakshmi.n@email.com", 15, "lost", "Low budget, not responding"),
        ]
        for n, ph, em, sc, sts, nt in names:
            cur.execute("INSERT INTO leads(full_name,phone,email,score,status,ai_qualification_notes) VALUES(%s,%s,%s,%s,%s,%s)", (n, ph, em, sc, sts, nt))

        for i, (agent, s_detail, e_detail) in enumerate(RE_AGENTS):
            t = datetime.now() - timedelta(minutes=len(PIPELINE_AGENTS)-i, seconds=random.randint(10, 50))
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
