import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io, re, csv

st.set_page_config(
    page_title="ASAP Benchmark Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- CSS ----------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background-color: #f0f2f6; }

    /* ── Dashboard Header ── */
    .dashboard-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #2563ab 100%);
        padding: 24px 32px;
        border-radius: 14px;
        margin-bottom: 24px;
        color: white;
    }
    .dashboard-header h1 { font-size: 24px; font-weight: 700; margin: 0 0 4px 0; color: white; }
    .dashboard-header p { font-size: 13px; color: rgba(255,255,255,0.7); margin: 0; }

    /* ── KPI Cards ── */
    .kpi-card {
        background: white;
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        border-left: 5px solid #e5e7eb;
        height: 100%;
    }
    .kpi-card.blue   { border-left-color: #2563ab; }
    .kpi-card.green  { border-left-color: #16a34a; }
    .kpi-card.yellow { border-left-color: #d97706; }
    .kpi-card.orange { border-left-color: #ea580c; }
    .kpi-card.red    { border-left-color: #dc2626; }

    /* percentage = big, count = smaller beneath */
    .kpi-pct  { font-size: 36px; font-weight: 700; line-height: 1; margin-bottom: 2px; }
    .kpi-card.blue   .kpi-pct { color: #2563ab; }
    .kpi-card.green  .kpi-pct { color: #16a34a; }
    .kpi-card.yellow .kpi-pct { color: #d97706; }
    .kpi-card.orange .kpi-pct { color: #ea580c; }
    .kpi-card.red    .kpi-pct { color: #dc2626; }
    .kpi-count { font-size: 13px; font-weight: 500; color: #6b7280; margin-bottom: 4px; }
    .kpi-label { font-size: 11px; color: #9ca3af; font-weight: 500; }

    /* ── Chart Cards ── */
    .chart-card {
        background: white;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        margin-bottom: 16px;
    }
    .chart-title {
        background: #1e3a5f;
        color: #ffffff !important;
        font-size: 13px;
        font-weight: 600;
        padding: 10px 16px;
        margin: 0;
        letter-spacing: 0.02em;
    }
    .chart-body { padding: 16px; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] { background: #1e3a5f; }
    [data-testid="stSidebar"] * { color: white !important; }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label { color: rgba(255,255,255,0.8) !important; font-size: 12px !important; }

    /* Sidebar brand header — larger */
    .sidebar-header {
        padding: 22px 16px 14px 16px;
        border-bottom: 1px solid rgba(255,255,255,0.18);
        margin-bottom: 14px;
    }
    .sidebar-header .brand { font-size: 20px; font-weight: 700; color: #ffffff !important; line-height: 1.2; }
    .sidebar-header .sub   { font-size: 13px; color: rgba(255,255,255,0.75) !important; margin-top: 4px; font-weight: 500; }

    /* Upload boxes — compact + dark text inside dropzone */
    [data-testid="stSidebar"] .stFileUploader { margin-bottom: 4px !important; }
    [data-testid="stSidebar"] .stFileUploader label {
        font-size: 10px !important;
        font-weight: 600 !important;
        color: rgba(255,255,255,0.8) !important;
        margin-bottom: 2px !important;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
        background: rgba(255,255,255,0.93) !important;
        border: 1.5px dashed rgba(255,255,255,0.45) !important;
        border-radius: 6px !important;
        padding: 6px 8px !important;
        min-height: unset !important;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] p,
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] *,
    [data-testid="stSidebar"] small,
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] span {
        color: #1e293b !important;
        font-size: 10px !important;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploaderFile"] * { color: #ffffff !important; font-size: 10px !important; }

    /* ── Hide the native sidebar toggle (we replace it with a custom one) ── */
    [data-testid="stSidebarCollapseButton"] { display: none !important; }

    /* ── Custom always-visible sidebar toggle ── */
    #custom-sidebar-btn {
        position: fixed;
        top: 50vh;
        transform: translateY(-50%);
        z-index: 99999;
        background: #2563ab;
        color: white;
        border: 2px solid white;
        border-radius: 0 20px 20px 0;
        width: 22px;
        height: 44px;
        cursor: pointer;
        font-size: 13px;
        font-weight: 700;
        padding: 0;
        box-shadow: 3px 0 10px rgba(0,0,0,0.35);
        line-height: 44px;
        text-align: center;
        transition: background 0.2s;
    }
    #custom-sidebar-btn:hover { background: #1e3a5f; }

    /* ── Download button ── */
    .stDownloadButton button {
        background: linear-gradient(135deg, #1e3a5f, #2563ab) !important;
        color: white !important; border: none !important;
        padding: 10px 24px !important; border-radius: 8px !important;
        font-weight: 600 !important; width: 100%;
    }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
</style>
<script>
(function() {
    function setup() {
        // Find the real native toggle button inside Streamlit's element
        var native = document.querySelector('[data-testid="stSidebarCollapseButton"] button');
        if (!native) { setTimeout(setup, 300); return; }

        // Create our custom button if not already there
        if (document.getElementById('custom-sidebar-btn')) return;
        var btn = document.createElement('button');
        btn.id = 'custom-sidebar-btn';
        document.body.appendChild(btn);

        function update() {
            var sidebar = document.querySelector('[data-testid="stSidebar"]');
            var isOpen = sidebar && sidebar.getBoundingClientRect().width > 60;
            var right = isOpen ? sidebar.getBoundingClientRect().right : 0;
            btn.style.left = right + 'px';
            btn.textContent = isOpen ? '◀' : '▶';
        }

        btn.addEventListener('click', function() {
            native.click();
            // update after animation
            setTimeout(update, 350);
        });

        update();
        // Watch for sidebar open/close transitions
        new MutationObserver(update).observe(document.body, { subtree: true, attributes: true, attributeFilter: ['style', 'class'] });
        window.addEventListener('resize', update);
    }
    // Wait for Streamlit to render
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() { setTimeout(setup, 500); });
    } else {
        setTimeout(setup, 500);
    }
})();
</script>
""", unsafe_allow_html=True)

# ---------- Helpers ----------
def read_any(file_obj):
    fname = file_obj.name
    raw = file_obj.read()
    bio = io.BytesIO(raw)
    if fname.lower().endswith((".xlsx", ".xls")):
        for strategy in [
            lambda: pd.read_excel(bio, dtype=str),
            lambda: pd.read_excel(bio, dtype=str, engine='openpyxl'),
            lambda: pd.read_excel(bio, engine='openpyxl', dtype=str, na_filter=False, keep_default_na=False),
        ]:
            try:
                bio.seek(0); df = strategy()
                for col in df.columns: df[col] = df[col].astype(str)
                return df
            except: continue
        raise ValueError(f"Cannot read {fname}")

    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin1"):
        try:
            bio.seek(0)
            sample = bio.read(200_000).decode(enc, errors="ignore")
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
                sep, qc = dialect.delimiter, dialect.quotechar
            except: sep, qc = None, '"'
            bio.seek(0)
            return pd.read_csv(bio, encoding=enc, sep=sep, engine="python",
                               quotechar=qc, on_bad_lines="warn", dtype=str)
        except: continue
    raise ValueError(f"Cannot read {fname}")

def coerce_str_id(s):
    return s.astype(str).str.strip().str.replace(r"\.0$", "", regex=True)

def to_flag(x):
    if pd.isna(x): return 0
    sx = str(x).strip()
    try: return 1 if float(sx) > 0 else 0
    except: pass
    return 1 if sx.lower() in {"1","true","t","yes","y","completed","complete","met","done","x"} else 0

def fuzzy_pick(col_name, cols):
    if col_name in cols: return col_name
    want = re.sub(r"\s+"," ", col_name.lower()).strip()
    for c in cols:
        if re.sub(r"\s+"," ", c.lower()).strip() == want: return c
    root = col_name.split(" (")[0].lower()
    for c in cols:
        if root in c.lower(): return c
    return None

PLOTLY_TEMPLATE = dict(
    plot_bgcolor="white", paper_bgcolor="white",
    font=dict(family="Inter, sans-serif", size=12),
    margin=dict(t=20, b=40, l=40, r=20),
)

STATUS_COLORS = {
    "Completed": "#16a34a",
    "Missing group": "#d97706",
    "Missing individual": "#ea580c",
    "Missing both": "#dc2626"
}

# ---------- Sidebar: file upload + filters ----------
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <div class="brand">📊 ASAP Reports</div>
        <div class="sub">Bronx Community College</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("**📁 Upload Files**")
    up_master     = st.file_uploader("MASTER file",              type=["csv","xlsx","xls"], key="master")
    up_indv       = st.file_uploader("INDIVIDUAL MEETINGS",      type=["csv","xlsx","xls"], key="indv")
    up_group      = st.file_uploader("GROUP MEETINGS",           type=["csv","xlsx","xls"], key="group")
    up_central    = st.file_uploader("CENTRAL BENCHMARK",        type=["csv","xlsx","xls"], key="central")
    up_enrollment = st.file_uploader("STUDENT ENROLLMENT",       type=["csv","xlsx","xls"], key="enroll")
    up_appts      = st.file_uploader("UPCOMING APPOINTMENTS",    type=["csv","xlsx","xls"], key="appts")

# ---------- Header ----------
st.markdown("""
<div class="dashboard-header">
    <h1>📊 ASAP Benchmark Dashboard</h1>
    <p>Bronx Community College · Advisor Meeting Compliance · Use filters in the sidebar to slice data</p>
</div>
""", unsafe_allow_html=True)

all_uploaded = all([up_master, up_indv, up_group, up_central, up_enrollment, up_appts])

if not all_uploaded:
    n = sum([bool(up_master), bool(up_indv), bool(up_group), bool(up_central), bool(up_enrollment), bool(up_appts)])
    st.info(f"👈 Upload all 6 files in the sidebar to load the dashboard. ({n}/6 uploaded)")
    st.stop()

# ---------- Process data ----------
@st.cache_data(show_spinner=False)
def process_files(m, i, g, c, e, a):
    df_master     = read_any(m)
    df_indv       = read_any(i)
    df_group      = read_any(g)
    df_central    = read_any(c)
    df_enrollment = read_any(e)
    df_appts      = read_any(a)

    for df in (df_master, df_indv, df_group, df_central, df_enrollment, df_appts):
        df.columns = df.columns.str.strip()

    df_master["EMPLID"] = coerce_str_id(df_master["EMPLID"])
    df_central["EMPLID"] = coerce_str_id(df_central["EMPLID"])

    indv_id = next((c for c in ["Student ID","StudentID","EMPLID","Emplid"] if c in df_indv.columns), None)
    df_indv["StudentID_clean"] = coerce_str_id(df_indv[indv_id])

    grp_id = next((c for c in ["Student ID","StudentID","EMPLID","Emplid"] if c in df_group.columns), None)
    df_group["StudentID_clean"] = coerce_str_id(df_group[grp_id])

    enroll_id = next((c for c in ["EMPLID","Emplid","Student ID","StudentID"] if c in df_enrollment.columns), None)
    df_enrollment["EMPLID"] = coerce_str_id(df_enrollment[enroll_id])

    appts_id = next((c for c in ["Student ID","StudentID","EMPLID","Emplid"] if c in df_appts.columns), None)
    df_appts["StudentID_clean"] = coerce_str_id(df_appts[appts_id])

    # --- Monthly trend from meeting dates ---
    date_col = next((c for c in df_indv.columns if "date" in c.lower()), None)
    monthly_trend = None
    if date_col:
        df_indv[date_col] = pd.to_datetime(df_indv[date_col], errors="coerce")
        df_indv["Month"] = df_indv[date_col].dt.to_period("M").astype(str)

    indv_counts = df_indv.groupby("StudentID_clean", as_index=False).size().rename(columns={"size":"individual_meeting_count"})
    group_flag  = df_group.drop_duplicates("StudentID_clean").assign(group_meeting=1)[["StudentID_clean","group_meeting"]]

    ecm = {k: fuzzy_pick(k, df_enrollment.columns.tolist()) for k in ["UNV EMAIL","PERS EMAIL","PHONE"]}
    for col, val in ecm.items():
        if val is None: df_enrollment[col] = np.nan; ecm[col] = col
    df_enrollment = df_enrollment.rename(columns={v:k for k,v in ecm.items()})
    enrollment_data = df_enrollment[["EMPLID","UNV EMAIL","PERS EMAIL","PHONE"]].drop_duplicates("EMPLID", keep="first")

    df_appts_u = df_appts[["StudentID_clean"]].drop_duplicates().copy()
    df_appts_u["Upcoming Appts"] = "Yes"

    fallbacks = {
        "First Name": ["First name","FirstName","FIRST NAME"],
        "Last Name":  ["Last name","LastName","LAST NAME"],
        "Cohort Name": ["Cohort","CohortName"],
        "Phone Number Preferred": ["Phone","Preferred Phone","Phone Number"],
        "ASAPi Assigned Advisor": ["ASAPi Advisor","Assigned Advisor","Advisor"],
        "ASAPi Support Level": ["Support Level","ASAPi Support","ASAP Support Level"],
    }
    for target, alts in fallbacks.items():
        if target not in df_master.columns:
            for a in alts:
                if a in df_master.columns: df_master[target] = df_master[a]; break
            if target not in df_master.columns: df_master[target] = np.nan

    keep = ["EMPLID","First Name","Last Name","Cohort Name","ASAPi Assigned Advisor","ASAPi Support Level"]
    base = df_master[[c for c in keep if c in df_master.columns]].copy()
    base = base.merge(indv_counts, left_on="EMPLID", right_on="StudentID_clean", how="left").drop(columns=["StudentID_clean"], errors="ignore")
    base["individual_meeting_count"] = pd.to_numeric(base["individual_meeting_count"], errors="coerce").fillna(0).astype(int)
    base = base.merge(group_flag, left_on="EMPLID", right_on="StudentID_clean", how="left").drop(columns=["StudentID_clean"], errors="ignore")
    base["group_meeting"] = pd.to_numeric(base["group_meeting"], errors="coerce").fillna(0).astype(int)

    central_needed = ["Required Individual Advisement Contact (Current)",
                      "Second Advisement Contact (Current)",
                      "Met Advisement Benchmark (Current)"]
    central_map = {k: fuzzy_pick(k, df_central.columns.tolist()) for k in central_needed}
    central_slim = df_central[["EMPLID"] + [central_map[k] for k in central_needed if central_map[k]]].copy()
    central_slim.rename(columns={central_map[k]:k for k in central_needed if central_map[k]}, inplace=True)
    for c in central_needed:
        if c in central_slim: central_slim[c] = central_slim[c].apply(to_flag).astype(int)
        else: central_slim[c] = 0
    central_agg = central_slim.groupby("EMPLID", as_index=False)[central_needed].max()

    out = base.merge(central_agg, on="EMPLID", how="left")
    for c in central_needed: out[c] = out[c].fillna(0).astype(int)
    out = out.merge(enrollment_data, on="EMPLID", how="left")
    out = out.merge(df_appts_u, left_on="EMPLID", right_on="StudentID_clean", how="left").drop(columns=["StudentID_clean"], errors="ignore")
    out["Upcoming Appts"] = out["Upcoming Appts"].fillna("")

    INDCNT = "individual_meeting_count"
    REQIND = "Required Individual Advisement Contact (Current)"
    SECG   = "Second Advisement Contact (Current)"
    MET    = "Met Advisement Benchmark (Current)"

    out["has_individual"] = ((out[INDCNT] >= 1) | (out[REQIND] == 1)).astype(int)
    out["has_group"]      = ((out["group_meeting"] == 1) | (out[SECG] == 1)).astype(int)

    def decide(row):
        if row[MET] == 1 or row[INDCNT] >= 2: return "Completed"
        hi, hg = bool(row["has_individual"]), bool(row["has_group"])
        if hi and hg: return "Completed"
        if hi: return "Missing group"
        if hg: return "Missing individual"
        return "Missing both"

    out["Missing Services"] = out.apply(decide, axis=1)
    out = out.rename(columns={"ASAPi Assigned Advisor":"Advisor","ASAPi Support Level":"Support Level",
                               "UNV EMAIL":"BCC Email","PERS EMAIL":"Personal Email","PHONE":"Phone Number"})

    # Monthly trend: merge meeting dates back
    if date_col and "Month" in df_indv.columns:
        month_meetings = df_indv[["StudentID_clean","Month"]].copy()
        month_data = out[["EMPLID","Missing Services"]].merge(
            month_meetings, left_on="EMPLID", right_on="StudentID_clean", how="inner"
        )
        monthly_trend = (
            month_data.groupby("Month")
            .agg(total=("EMPLID","count"), completed=("Missing Services", lambda x: (x=="Completed").sum()))
            .reset_index()
        )
        monthly_trend["completion_rate"] = (monthly_trend["completed"] / monthly_trend["total"] * 100).round(1)
        monthly_trend = monthly_trend.sort_values("Month")

    return out, monthly_trend, df_indv, date_col

with st.spinner("Loading dashboard..."):
    try:
        final_df, monthly_trend, df_indv_raw, date_col = process_files(
            up_master, up_indv, up_group, up_central, up_enrollment, up_appts
        )
    except Exception as e:
        st.error(f"❌ Error processing files: {e}"); st.exception(e); st.stop()

# ---------- Sidebar filters ----------
with st.sidebar:
    st.markdown("---")
    st.markdown("### 🔍 Filters")

    advisor_opts = ["All"] + sorted(final_df["Advisor"].dropna().unique().tolist()) if "Advisor" in final_df.columns else ["All"]
    sel_advisor = st.selectbox("Advisor", advisor_opts)

    cohort_opts = ["All"] + sorted(final_df["Cohort Name"].dropna().unique().tolist()) if "Cohort Name" in final_df.columns else ["All"]
    sel_cohort = st.multiselect("Cohort Name", cohort_opts[1:], placeholder="All cohorts")

    support_opts = ["All"] + sorted(final_df["Support Level"].dropna().unique().tolist()) if "Support Level" in final_df.columns else ["All"]
    sel_support = st.multiselect("Support Level", support_opts[1:], placeholder="All levels")

    status_opts = ["Completed","Missing group","Missing individual","Missing both"]
    sel_status = st.multiselect("Missing Services", status_opts, default=status_opts)

# ---------- Apply filters ----------
df = final_df.copy()
if sel_advisor != "All" and "Advisor" in df.columns:
    df = df[df["Advisor"] == sel_advisor]
if sel_cohort and "Cohort Name" in df.columns:
    df = df[df["Cohort Name"].isin(sel_cohort)]
if sel_support and "Support Level" in df.columns:
    df = df[df["Support Level"].isin(sel_support)]
if sel_status:
    df = df[df["Missing Services"].isin(sel_status)]

# ---------- KPIs ----------
total = len(df)
completed = (df["Missing Services"] == "Completed").sum()
miss_group = (df["Missing Services"] == "Missing group").sum()
miss_both  = (df["Missing Services"] == "Missing both").sum()
miss_indv  = (df["Missing Services"] == "Missing individual").sum()
rate = f"{completed/total*100:.1f}%" if total > 0 else "0%"

def pct(n): return f"{n/total*100:.1f}%" if total > 0 else "0%"

k1,k2,k3,k4 = st.columns(4)
with k1:
    st.markdown(f'<div class="kpi-card green"><div class="kpi-pct">{pct(completed)}</div><div class="kpi-count">{completed:,} students</div><div class="kpi-label">✅ Total Completed</div></div>', unsafe_allow_html=True)
with k2:
    st.markdown(f'<div class="kpi-card yellow"><div class="kpi-pct">{pct(miss_group)}</div><div class="kpi-count">{miss_group:,} students</div><div class="kpi-label">⚠️ Missing Group</div></div>', unsafe_allow_html=True)
with k3:
    st.markdown(f'<div class="kpi-card red"><div class="kpi-pct">{pct(miss_both)}</div><div class="kpi-count">{miss_both:,} students</div><div class="kpi-label">🔴 Missing Both</div></div>', unsafe_allow_html=True)
with k4:
    st.markdown(f'<div class="kpi-card orange"><div class="kpi-pct">{pct(miss_indv)}</div><div class="kpi-count">{miss_indv:,} students</div><div class="kpi-label">🔶 Missing Individual</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------- Row 1: Advisor completion rate + Cohort compliance ----------
row1_left, row1_right = st.columns(2)

with row1_left:
    st.markdown('<div class="chart-card"><div class="chart-title">Completion Rate by Advisor</div><div class="chart-body">', unsafe_allow_html=True)
    if "Advisor" in df.columns:
        adv_df = df.groupby("Advisor").apply(
            lambda x: pd.Series({
                "Total": len(x),
                "Completed": (x["Missing Services"] == "Completed").sum()
            })
        ).reset_index()
        adv_df["Rate"] = (adv_df["Completed"] / adv_df["Total"] * 100).round(1)
        adv_df = adv_df.sort_values("Rate", ascending=True)
        fig = go.Figure(go.Bar(
            x=adv_df["Rate"], y=adv_df["Advisor"], orientation="h",
            marker_color=adv_df["Rate"].apply(lambda r: "#16a34a" if r >= 85 else "#d97706" if r >= 75 else "#dc2626"),
            text=adv_df["Rate"].apply(lambda r: f"{r}%"), textposition="outside",
            hovertemplate="<b>%{y}</b><br>Completion Rate: %{x}%<extra></extra>"
        ))
        fig.update_layout(**PLOTLY_TEMPLATE, height=320,
                          xaxis=dict(range=[0,110], showgrid=True, gridcolor="#f3f4f6"),
                          yaxis=dict(showgrid=False))
        st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

with row1_right:
    st.markdown('<div class="chart-card"><div class="chart-title">Meeting Compliance by Cohort</div><div class="chart-body">', unsafe_allow_html=True)
    if "Cohort Name" in df.columns:
        cohort_df = df.groupby(["Cohort Name","Missing Services"]).size().reset_index(name="Count")
        fig2 = px.bar(cohort_df, x="Cohort Name", y="Count", color="Missing Services",
                      color_discrete_map=STATUS_COLORS, barmode="stack",
                      hover_data={"Count":True, "Cohort Name":True})
        fig2.update_layout(**PLOTLY_TEMPLATE, height=320,
                           xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#f3f4f6"),
                           legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig2, use_container_width=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

# ---------- Row 2: Support level + Missing breakdown ----------
row2_left, row2_mid = st.columns(2)

with row2_left:
    st.markdown('<div class="chart-card"><div class="chart-title">Support Level Summary</div><div class="chart-body">', unsafe_allow_html=True)
    if "Support Level" in df.columns:
        sup_df = df.groupby(["Support Level","Missing Services"]).size().reset_index(name="Count")
        fig3 = px.bar(sup_df, x="Support Level", y="Count", color="Missing Services",
                      color_discrete_map=STATUS_COLORS, barmode="group")
        fig3.update_layout(**PLOTLY_TEMPLATE, height=280,
                           xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#f3f4f6"),
                           legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig3, use_container_width=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

with row2_mid:
    st.markdown('<div class="chart-card"><div class="chart-title">Missing Services Breakdown</div><div class="chart-body">', unsafe_allow_html=True)
    pie_df = df["Missing Services"].value_counts().reset_index()
    pie_df.columns = ["Status","Count"]
    total_for_pct = pie_df["Count"].sum()
    fig4 = go.Figure(go.Pie(
        labels=pie_df["Status"],
        values=pie_df["Count"],
        hole=0.6,
        marker_colors=[STATUS_COLORS.get(s, "#9ca3af") for s in pie_df["Status"]],
        textinfo="none",
        hovertemplate="<b>%{label}</b><br>%{value} students (%{percent})<extra></extra>",
        direction="clockwise",
        sort=False,
        domain=dict(x=[0, 0.55]),   # donut occupies left 55%, legend has room on right
    ))
    top_row = pie_df.iloc[0]
    top_pct = f"{top_row['Count']/total_for_pct*100:.1f}%" if total_for_pct > 0 else "0%"
    fig4.add_annotation(
        text=f"<b>{top_pct}</b><br><span style='font-size:10px'>{top_row['Status']}</span>",
        x=0.275, y=0.5, showarrow=False, font=dict(size=14, color="#1e3a5f"),
        align="center"
    )
    fig4.update_layout(
        **PLOTLY_TEMPLATE, height=280,
        showlegend=True,
        legend=dict(
            orientation="v",
            x=0.62, y=0.5,
            xanchor="left", yanchor="middle",
            font=dict(size=11),
            itemclick=False, itemdoubleclick=False,
        ),
    )
    st.plotly_chart(fig4, use_container_width=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

# ---------- Row 3: Advisor table (full width, no upcoming appts) ----------
st.markdown('<div class="chart-card"><div class="chart-title">Advisor Breakdown Table</div><div class="chart-body">', unsafe_allow_html=True)
if "Advisor" in df.columns:
    adv_table = df.groupby("Advisor")["Missing Services"].value_counts().unstack(fill_value=0).reset_index()
    for col in ["Completed","Missing group","Missing individual","Missing both"]:
        if col not in adv_table.columns: adv_table[col] = 0
    adv_table["Total"] = adv_table[["Completed","Missing group","Missing individual","Missing both"]].sum(axis=1)
    adv_table["Rate"] = (adv_table["Completed"] / adv_table["Total"] * 100).round(1).astype(str) + "%"
    totals = pd.DataFrame([{
        "Advisor": "TOTAL",
        "Completed": adv_table["Completed"].sum(),
        "Missing group": adv_table["Missing group"].sum(),
        "Missing individual": adv_table["Missing individual"].sum(),
        "Missing both": adv_table["Missing both"].sum(),
        "Total": adv_table["Total"].sum(),
        "Rate": f"{adv_table['Completed'].sum()/adv_table['Total'].sum()*100:.1f}%"
    }])
    adv_table = pd.concat([adv_table, totals], ignore_index=True)
    st.dataframe(adv_table[["Advisor","Completed","Missing group","Missing individual","Missing both","Total","Rate"]],
                 use_container_width=True, hide_index=True, height=280)
st.markdown('</div></div>', unsafe_allow_html=True)

# ---------- Full student table ----------
st.markdown('<div class="chart-card"><div class="chart-title">All Students</div><div class="chart-body">', unsafe_allow_html=True)
emplid_search = st.text_input("🔍 Search by EMPLID", placeholder="Type an EMPLID to filter...", label_visibility="collapsed")
show_cols = [c for c in ["EMPLID","First Name","Last Name","Advisor","Cohort Name","Support Level",
                          "Missing Services","Upcoming Appts","individual_meeting_count","group_meeting"] if c in df.columns]
filtered_df = df[df["EMPLID"].astype(str).str.contains(emplid_search.strip(), case=False, na=False)] if emplid_search.strip() else df
st.dataframe(filtered_df[show_cols], use_container_width=True, height=350, hide_index=True)
st.caption(f"{len(filtered_df):,} students shown")
st.markdown('</div></div>', unsafe_allow_html=True)

# ---------- Download ----------
st.markdown("---")
output = io.BytesIO()
with pd.ExcelWriter(output, engine="openpyxl") as writer:
    final_df.to_excel(writer, index=False, sheet_name="Benchmark Report")
output.seek(0)

dc1, dc2, dc3 = st.columns([1,2,1])
with dc2:
    st.download_button(
        label="⬇️ Download Full Report as Excel",
        data=output,
        file_name="ASAP_Benchmark_Status.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
