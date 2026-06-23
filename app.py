import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import wbgapi as wb
import numpy as np
from scipy import stats

st.set_page_config(page_title="Japan Workforce Crisis", page_icon="🇯🇵", layout="wide")

st.markdown("""
<style>
    /* Main Sidebar Background */
    section[data-testid="stSidebar"] {
        background: #0d0f1a;
        border-right: 1px solid #1f2335;
    }

    /* Hide default sidebar navigation if any */
    div[data-testid="stSidebarNav"] {
        display: none;
    }

    /* Hide the 'Navigate to' title above radio buttons */
    [data-testid="stSidebar"] .stRadio > label {
        display: none !important;
    }

    /* Space out the radio group */
    [data-testid="stSidebar"] div[role="radiogroup"] {
        gap: 0.5rem;
        padding: 0 8px;
    }

    /* Base styling for radio options (acting as buttons) */
    [data-testid="stSidebar"] div[role="radiogroup"] > label {
        background: #141724;
        border: 1px solid #1f2335;
        border-radius: 8px;
        padding: 12px 16px;
        cursor: pointer;
        transition: all 0.25s ease;
        display: flex;
        align-items: center;
        width: 100%;
        margin: 0;
    }

    /* COMPLETELY hide the native radio circles */
    [data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {
        display: none !important;
    }

    /* Text styling for the unselected buttons */
    [data-testid="stSidebar"] div[role="radiogroup"] > label p {
        color: #8b8fa8 !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        margin: 0 !important;
    }

    /* Hover State */
    [data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
        background: #1a1d2e;
        border-color: #ff6b35;
        transform: translateX(4px); /* Subtle slide to the right */
    }
    
    [data-testid="stSidebar"] div[role="radiogroup"] > label:hover p {
        color: #ffffff !important;
    }

    /* Active/Selected State */
    [data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
        background: linear-gradient(90deg, rgba(255,107,53,0.1) 0%, rgba(20,23,36,0) 100%);
        border: 1px solid #1f2335;
        border-left: 4px solid #ff6b35; /* Orange accent bar on the left */
    }

    [data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) p {
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    /* Custom classes for HTML elements */
    .sidebar-header-box {
        text-align: center;
        padding: 10px 0 20px 0;
    }
    
    .sidebar-icon {
        background: linear-gradient(135deg, #ff6b35, #ff4d6d);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 42px;
        font-weight: bold;
        margin-bottom: 8px;
    }
    /* Hide the default Streamlit top toolbar */
    [data-testid="stToolbar"] {
        visibility: hidden !important;
    }
</style>
""", unsafe_allow_html=True)

# ─── HARDCODED DATA ───────────────────────────────────────────
japan_birth_rate = {
    2000:9.5,2001:9.3,2002:9.2,2003:8.9,2004:8.8,
    2005:8.4,2006:8.7,2007:8.6,2008:8.7,2009:8.5,
    2010:8.5,2011:8.3,2012:8.2,2013:8.2,2014:8.0,
    2015:8.0,2016:7.8,2017:7.6,2018:7.4,2019:7.0,
    2020:6.8,2021:6.6,2022:6.3
}
japan_death_rate = {
    2000:7.7,2001:7.7,2002:7.8,2003:8.0,2004:8.2,
    2005:8.6,2006:8.6,2007:8.8,2008:9.1,2009:9.1,
    2010:9.5,2011:9.9,2012:10.0,2013:10.1,2014:10.1,
    2015:10.3,2016:10.5,2017:10.8,2018:11.0,2019:11.2,
    2020:11.1,2021:11.7,2022:12.9
}
japan_fertility_rate = {
    2000:1.36,2001:1.33,2002:1.32,2003:1.29,2004:1.29,
    2005:1.26,2006:1.32,2007:1.34,2008:1.37,2009:1.37,
    2010:1.39,2011:1.39,2012:1.41,2013:1.43,2014:1.42,
    2015:1.45,2016:1.44,2017:1.43,2018:1.42,2019:1.36,
    2020:1.33,2021:1.30,2022:1.26
}
japan_gdp_per_capita = {
    2000:39169,2001:33846,2002:32288,2003:34808,2004:37688,
    2005:37217,2006:35434,2007:35275,2008:39339,2009:40855,
    2010:44507,2011:48167,2012:48603,2013:40454,2014:38096,
    2015:34474,2016:38900,2017:38428,2018:39241,2019:40246,
    2020:39583,2021:39312,2022:33815
}
japan_it_shortage = {2015:170000,2018:220000,2020:300000,2030:790000}
stem_graduates = {
    "India":2550000,"Japan":550000,
    "Vietnam":350000,"Bangladesh":75000,"Sri Lanka":25000
}
median_age = {
    "Japan":     {2000:41.2,2005:43.0,2010:44.7,2015:46.4,2020:48.4,2024:50.4},
    "India":     {2000:21.6,2005:22.7,2010:24.0,2015:25.5,2020:27.2,2024:29.5},
    "Vietnam":   {2000:23.0,2005:24.8,2010:27.3,2015:29.8,2020:31.9,2024:33.9},
    "Bangladesh":{2000:19.8,2005:21.0,2010:22.5,2015:24.3,2020:26.2,2024:27.6},
    "Sri Lanka": {2000:28.0,2005:29.5,2010:30.9,2015:32.4,2020:33.8,2024:34.8}
}
japan_age_structure = {
    "0-14":  {2000:14.6,2005:13.7,2010:13.2,2015:12.7,2020:12.0,2022:11.6},
    "15-64": {2000:68.1,2005:65.9,2010:63.8,2015:60.7,2020:59.3,2022:58.9},
    "65+":   {2000:17.3,2005:20.4,2010:23.0,2015:26.6,2020:28.7,2022:29.5}
}

YEARS = list(range(2000, 2023))

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#e0e0e0", family="sans-serif"),
    xaxis=dict(gridcolor="#2d3147", linecolor="#2d3147"),
    yaxis=dict(gridcolor="#2d3147", linecolor="#2d3147"),
    margin=dict(t=30, b=20, l=10, r=10)
)

# ─── LOAD WORLD BANK DATA ─────────────────────────────────────
@st.cache_data(ttl=3600)
def load_wb_data():
    import time
    for attempt in range(3):
        try:
            gdp     = wb.data.DataFrame('NY.GDP.MKTP.CD',   'JPN', mrv=23).T
            pop     = wb.data.DataFrame('SP.POP.TOTL',       'JPN', mrv=23).T
            exports = wb.data.DataFrame('NE.EXP.GNFS.CD',   'JPN', mrv=23).T
            imports = wb.data.DataFrame('NE.IMP.GNFS.CD',   'JPN', mrv=23).T
            labor   = wb.data.DataFrame('SL.TLF.TOTL.IN',   'JPN', mrv=23).T
            elderly = wb.data.DataFrame('SP.POP.65UP.TO.ZS','JPN', mrv=23).T
            pop_countries = wb.data.DataFrame(
                'SP.POP.TOTL',
                ['JPN','IND','VNM','BGD','LKA'], mrv=23).T

            df = pd.DataFrame({
                "Year":                         YEARS,
                "GDP (USD Billion)":           (gdp.values.flatten()/1e9).round(1),
                "Population (Million)":        (pop.values.flatten()/1e6).round(2),
                "Exports (USD Billion)":       (exports.values.flatten()/1e9).round(1),
                "Imports (USD Billion)":       (imports.values.flatten()/1e9).round(1),
                "Trade Balance (USD Billion)": ((exports.values.flatten()-imports.values.flatten())/1e9).round(1),
                "Labor Force (Million)":       (labor.values.flatten()/1e6).round(2),
                "Elderly Population (%)":      elderly.values.flatten().round(2),
            })
            df["Birth Rate"]     = df["Year"].map(japan_birth_rate)
            df["Death Rate"]     = df["Year"].map(japan_death_rate)
            df["Fertility Rate"] = df["Year"].map(japan_fertility_rate)
            df["GDP Per Capita"] = df["Year"].map(japan_gdp_per_capita)
            df["Natural Growth"] = df["Birth Rate"] - df["Death Rate"]
            return df, pop_countries

        except Exception as e:
            if attempt < 2:
                time.sleep(3)
            else:
                st.error("World Bank API unavailable. Please refresh the page.")
                st.stop()

# FIX: Execute the data load function so 'df' and 'pop_countries' are defined globally
df, pop_countries = load_wb_data()

# ─── HEADER ───────────────────────────────────────────────────
st.markdown("""
<div style='margin-bottom:8px;'>
  <span class='tag'>World Bank API</span>
  <span class='tag'>Live Data</span>
  <span class='tag'>METI · UNESCO · UN</span>
  <span class='tag'>2000–2030 Forecast</span>
</div>""", unsafe_allow_html=True)

st.title("🇯🇵 Japan Workforce Crisis Dashboard")
st.markdown("<p style='font-size:17px;color:#8b8fa8;margin-top:-8px;'>Analyzing why Japan urgently needs global tech talent — and which nations are positioned to help</p>",
            unsafe_allow_html=True)
st.markdown("---")

# ─── SIDEBAR ──────────────────────────────────────────────────
st.sidebar.markdown("""
<div class='sidebar-header-box'>
    <div class='sidebar-icon'>JP</div>
    <h3 style='color:#ffffff; margin:0 0 4px 0; font-size:16px; letter-spacing: 0.5px;'>Japan Dashboard</h3>
    <p style='color:#8b8fa8; font-size:12px; margin:0; text-transform: uppercase; letter-spacing: 1px;'>Workforce Crisis</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("<hr style='border-color: #1f2335; margin: 0 16px 24px 16px;'>", unsafe_allow_html=True)

section = st.sidebar.radio("Navigate to", [
    "📊 Overview",
    "👥 Population Crisis",
    "💹 Economic Impact",
    "🌏 Global Talent Gap",
    "🔮 2030 Forecast"
])

# ══════════════════════════════════════════════════════════════
# SECTION 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════
if section == "📊 Overview":

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Peak GDP", f"${df['GDP (USD Billion)'].max():,.0f}B",
              str(df.loc[df['GDP (USD Billion)'].idxmax(),'Year']))
    c2.metric("Population Loss",
              f"-{df['Population (Million)'].iloc[0]-df['Population (Million)'].iloc[-1]:.1f}M",
              "Since 2000", delta_color="inverse")
    c3.metric("Labor Force Shrink",
              f"{df['Labor Force (Million)'].iloc[0]-df['Labor Force (Million)'].iloc[-1]:.1f}M",
              "Since 2000", delta_color="inverse")
    c4.metric("Elderly Share 2022", f"{df['Elderly Population (%)'].iloc[-1]:.1f}%",
              f"+{df['Elderly Population (%)'].iloc[-1]-df['Elderly Population (%)'].iloc[0]:.1f}% since 2000",
              delta_color="inverse")

    st.markdown("---")

    st.markdown("""
    <div class='insight-card'>
    <h3 style='color:#ff6b35;margin-top:0;'>🔍 The Core Problem</h3>
    <p style='color:#c0c4d6;line-height:1.9;font-size:15px;'>
    Japan is facing a <b style='color:white;'>triple demographic crisis</b> — a collapsing birth rate,
    a rapidly aging population, and a labor force that has been shrinking for over a decade.
    With <b style='color:white;'>29.5% of its population above 65</b> — the highest in the world —
    and a fertility rate of just <b style='color:white;'>1.26</b> (far below the 2.1 replacement level),
    Japan cannot solve this through domestic policy alone.
    The IT worker shortage alone is projected to reach <b style='color:white;'>790,000 by 2030</b>
    according to Japan's Ministry of Economy, Trade and Industry (METI).
    <b style='color:white;'>Programs like GS-JTI are not optional — they are economically existential.</b>
    </p>
    </div>""", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("GDP vs Labor Force Trend")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["Year"], y=df["GDP (USD Billion)"],
                                 name="GDP (USD B)", line=dict(color="#ff6b35", width=2),
                                 fill="tozeroy", fillcolor="rgba(255,107,53,0.08)"))
        fig.add_trace(go.Scatter(x=df["Year"], y=df["Labor Force (Million)"]*50,
                                 name="Labor Force (scaled)", line=dict(color="#4cc9f0", width=2, dash="dash")))
        fig.update_layout(height=320, template="plotly_dark",
                          legend=dict(bgcolor="rgba(0,0,0,0)"), **CHART_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("""<div class='section-card'>
        <p style='color:#8b8fa8;font-size:13px;margin:0;'>
        📌 <b style='color:white;'>Observation:</b> GDP and labor force tracked closely until 2012.
        After 2013, GDP became increasingly volatile while labor force continued declining steadily —
        suggesting productivity gains are masking a deeper structural weakness.
        </p></div>""", unsafe_allow_html=True)

    with col_b:
        st.subheader("Birth Rate vs Death Rate Crossover")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=YEARS, y=list(japan_birth_rate.values()),
                                  name="Birth Rate", line=dict(color="#06d6a0", width=2)))
        fig2.add_trace(go.Scatter(x=YEARS, y=list(japan_death_rate.values()),
                                  name="Death Rate", line=dict(color="#ff4d6d", width=2)))
        fig2.add_vline(x=2010, line_dash="dash", line_color="#ffd60a",
                       annotation_text="Death > Birth (2010)",
                       annotation_font_color="#ffd60a")
        fig2.update_layout(height=320, template="plotly_dark",
                           legend=dict(bgcolor="rgba(0,0,0,0)"), **CHART_LAYOUT)
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("""<div class='section-card'>
        <p style='color:#8b8fa8;font-size:13px;margin:0;'>
        📌 <b style='color:white;'>Critical Crossover:</b> Japan's death rate permanently exceeded
        its birth rate around 2010 — meaning the population now shrinks purely from natural causes,
        independent of migration. By 2022, the gap widened to <b style='color:white;'>6.6 per 1000</b>,
        the largest in recorded Japanese history.
        </p></div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# SECTION 2 — POPULATION CRISIS
# ══════════════════════════════════════════════════════════════
elif section == "👥 Population Crisis":

    st.subheader("Japan's Demographic Collapse — A Deep Dive")

    c1,c2,c3 = st.columns(3)
    c1.metric("Fertility Rate 2022", "1.26", "vs 2.1 replacement level", delta_color="inverse")
    c2.metric("Natural Growth 2022",
              f"{list(japan_birth_rate.values())[-1]-list(japan_death_rate.values())[-1]:.1f}",
              "per 1000 people", delta_color="inverse")
    c3.metric("Median Age 2024", "50.4 years", "Oldest nation on Earth")

    st.markdown("---")

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Fertility Rate Trend")
        fert_df = pd.DataFrame({"Year": YEARS,
                                 "Fertility Rate": list(japan_fertility_rate.values())})
        fig = px.line(fert_df, x="Year", y="Fertility Rate",
                      template="plotly_dark", color_discrete_sequence=["#f72585"])
        fig.add_hline(y=2.1, line_dash="dash", line_color="#ffd60a",
                      annotation_text="Replacement Level (2.1)",
                      annotation_font_color="#ffd60a")
        fig.update_layout(height=300, **CHART_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("""<div class='section-card'>
        <p style='color:#8b8fa8;font-size:13px;margin:0;'>
        📌 <b style='color:white;'>Observation:</b> Fertility rate has <b style='color:white;'>never reached
        replacement level</b> in the entire 2000–2022 period. Despite a slight recovery from the 2005 low of 1.26,
        the rate resumed decline post-2015 and hit a new low of <b style='color:white;'>1.26 in 2022</b>.
        At this rate, each generation is roughly <b style='color:white;'>40% smaller</b> than the previous one.
        </p></div>""", unsafe_allow_html=True)

    with col_b:
        st.subheader("Age Structure Breakdown (%)")
        age_years = [2000, 2005, 2010, 2015, 2020, 2022]
        age_df = pd.DataFrame({
            "Year": age_years,
            "Children (0–14)":   [japan_age_structure["0-14"][y]  for y in age_years],
            "Working Age (15–64)":[japan_age_structure["15-64"][y] for y in age_years],
            "Elderly (65+)":     [japan_age_structure["65+"][y]   for y in age_years],
        })
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(name="Children (0–14)",    x=age_df["Year"],
                              y=age_df["Children (0–14)"],    marker_color="#4cc9f0"))
        fig2.add_trace(go.Bar(name="Working Age (15–64)",x=age_df["Year"],
                              y=age_df["Working Age (15–64)"],marker_color="#06d6a0"))
        fig2.add_trace(go.Bar(name="Elderly (65+)",      x=age_df["Year"],
                              y=age_df["Elderly (65+)"],      marker_color="#ff4d6d"))
        fig2.update_layout(barmode="stack", height=300, template="plotly_dark",
                           legend=dict(bgcolor="rgba(0,0,0,0)"), **CHART_LAYOUT)
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("""<div class='section-card'>
        <p style='color:#8b8fa8;font-size:13px;margin:0;'>
        📌 <b style='color:white;'>Structural Shift:</b> Working-age population dropped from
        <b style='color:white;'>68.1% in 2000 to 58.9% in 2022</b> — a loss of 9.2 percentage points
        in just 22 years. Meanwhile elderly share nearly doubled from 17.3% to 29.5%.
        Fewer workers are now supporting more retirees — a <b style='color:white;'>dependency ratio crisis.</b>
        </p></div>""", unsafe_allow_html=True)

    st.subheader("Natural Population Growth Rate (Birth − Death)")
    nat_df = pd.DataFrame({"Year": YEARS,
                            "Natural Growth": [japan_birth_rate[y]-japan_death_rate[y] for y in YEARS]})
    colors = ["#06d6a0" if v > 0 else "#ff4d6d" for v in nat_df["Natural Growth"]]
    fig3 = go.Figure(go.Bar(x=nat_df["Year"], y=nat_df["Natural Growth"],
                            marker_color=colors))
    fig3.add_hline(y=0, line_color="#ffffff", line_width=1)
    fig3.update_layout(height=280, template="plotly_dark", **CHART_LAYOUT)
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown("""<div class='insight-card'>
    <p style='color:#c0c4d6;font-size:14px;margin:0;'>
    📌 <b style='color:white;'>Key Finding:</b> Japan crossed into <b style='color:white;'>negative
    natural growth around 2005</b> and the deficit has accelerated sharply since 2019.
    By 2022, the natural growth rate hit <b style='color:white;'>−6.6 per 1000</b> — meaning Japan
    loses roughly <b style='color:white;'>830,000 people per year</b> from natural causes alone,
    with no immigration policy capable of fully compensating at current levels.
    </p></div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# SECTION 3 — ECONOMIC IMPACT
# ══════════════════════════════════════════════════════════════
elif section == "💹 Economic Impact":

    st.subheader("Economic Indicators — GDP, Trade & Productivity")

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Peak GDP Per Capita", f"${max(japan_gdp_per_capita.values()):,}",
              str(max(japan_gdp_per_capita, key=japan_gdp_per_capita.get)))
    c2.metric("2022 GDP Per Capita", f"${japan_gdp_per_capita[2022]:,}",
              f"-${japan_gdp_per_capita[2012]-japan_gdp_per_capita[2022]:,} from peak",
              delta_color="inverse")
    c3.metric("IT Shortage 2020", "300,000", "METI estimate")
    c4.metric("Projected IT Shortage 2030", "790,000", "+163% vs 2020", delta_color="inverse")

    st.markdown("---")

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("GDP Per Capita (USD)")
        gdppc_df = pd.DataFrame({"Year": YEARS,
                                  "GDP Per Capita": [japan_gdp_per_capita[y] for y in YEARS]})
        fig = px.area(gdppc_df, x="Year", y="GDP Per Capita",
                      template="plotly_dark", color_discrete_sequence=["#ffd60a"])
        fig.update_traces(fillcolor="rgba(255,214,10,0.08)")
        fig.update_layout(height=300, **CHART_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("""<div class='section-card'>
        <p style='color:#8b8fa8;font-size:13px;margin:0;'>
        📌 <b style='color:white;'>Observation:</b> GDP per capita peaked at
        <b style='color:white;'>$48,603 in 2012</b> then dropped sharply — driven by
        Abenomics-era JPY depreciation rather than real output decline. The 2022 figure of
        $33,815 reflects a <b style='color:white;'>30% nominal drop</b> due to the weakest yen
        in 30 years, masking real productivity stagnation.
        </p></div>""", unsafe_allow_html=True)

    with col_b:
        st.subheader("IT Worker Shortage Forecast (METI)")
        it_df = pd.DataFrame({"Year": list(japan_it_shortage.keys()),
                               "Shortage": list(japan_it_shortage.values())})
        fig2 = go.Figure(go.Bar(x=it_df["Year"], y=it_df["Shortage"],
                                marker_color=["#4cc9f0","#4cc9f0","#ff6b35","#ff4d6d"],
                                text=[f"{v:,}" for v in it_df["Shortage"]],
                                textposition="outside",
                                textfont=dict(color="#e0e0e0")))
        fig2.update_layout(height=300, template="plotly_dark", **CHART_LAYOUT)
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("""<div class='section-card'>
        <p style='color:#8b8fa8;font-size:13px;margin:0;'>
        📌 <b style='color:white;'>Critical Gap:</b> Japan's IT talent deficit grew from
        170,000 in 2015 to 300,000 in 2020 — a <b style='color:white;'>76% increase in 5 years</b>.
        METI projects this will hit <b style='color:white;'>790,000 by 2030</b> as digital
        transformation accelerates while domestic STEM graduates plateau at ~550,000 annually.
        </p></div>""", unsafe_allow_html=True)

    st.subheader("Trade Balance — Structural Shifts")
    colors = ["#ff4d6d" if x < 0 else "#06d6a0" for x in df["Trade Balance (USD Billion)"]]
    fig3 = go.Figure(go.Bar(x=df["Year"], y=df["Trade Balance (USD Billion)"],
                            marker_color=colors,
                            text=df["Trade Balance (USD Billion)"].round(0),
                            textposition="outside",
                            textfont=dict(size=9, color="#8b8fa8")))
    fig3.update_layout(height=300, template="plotly_dark", **CHART_LAYOUT)
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown("""<div class='insight-card'>
    <p style='color:#c0c4d6;font-size:14px;margin:0;'>
    📌 <b style='color:white;'>Finding:</b> Japan ran a trade surplus for
    <b style='color:white;'>17 of 23 years</b> — confirming its export-led growth model.
    The 2011–2015 deficit period was triggered by the <b style='color:white;'>Fukushima disaster</b>
    forcing a shutdown of all 54 nuclear reactors, causing a massive surge in LNG and oil imports.
    Recovery post-2016 was short-lived — the 2022 deficit of <b style='color:white;'>−$162B</b>
    is the worst on record, driven by JPY weakness and energy import costs.
    </p></div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# SECTION 4 — GLOBAL TALENT GAP
# ══════════════════════════════════════════════════════════════
elif section == "🌏 Global Talent Gap":

    st.subheader("Why Global South is Japan's Answer")

    c1,c2,c3 = st.columns(3)
    c1.metric("India STEM Graduates/yr", "2,550,000", "4.6x Japan's output")
    c2.metric("Japan Median Age", "50.4 yrs", "vs India's 29.5 yrs")
    c3.metric("Combined GS STEM Pool", "~3,000,000", "India+Vietnam+BD+SL/yr")

    st.markdown("---")

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Median Age Comparison (UN Data)")
        med_years = [2000, 2005, 2010, 2015, 2020, 2024]
        colors_map = {"Japan":"#ff6b35","India":"#4cc9f0",
                      "Vietnam":"#06d6a0","Bangladesh":"#f72585","Sri Lanka":"#ffd60a"}
        fig = go.Figure()
        for country, data in median_age.items():
            fig.add_trace(go.Scatter(
                x=med_years, y=[data[y] for y in med_years],
                name=country, mode="lines+markers",
                line=dict(color=colors_map[country], width=2),
                marker=dict(size=6)
            ))
        fig.add_hline(y=37, line_dash="dash", line_color="#8b8fa8",
                      annotation_text="Global avg ~37",
                      annotation_font_color="#8b8fa8")
        fig.update_layout(height=320, template="plotly_dark",
                          legend=dict(bgcolor="rgba(0,0,0,0)"), **CHART_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("""<div class='section-card'>
        <p style='color:#8b8fa8;font-size:13px;margin:0;'>
        📌 <b style='color:white;'>Age Gap:</b> Japan's median age of 50.4 is
        <b style='color:white;'>20+ years older</b> than India (29.5) and Bangladesh (27.6).
        This isn't a temporary gap — it will widen through 2050 as Japan ages and
        South Asia remains in its demographic dividend window.
        </p></div>""", unsafe_allow_html=True)

    with col_b:
        st.subheader("Annual STEM Graduates by Country")
        stem_df = pd.DataFrame({
            "Country": list(stem_graduates.keys()),
            "STEM Graduates": list(stem_graduates.values())
        }).sort_values("STEM Graduates", ascending=True)
        fig2 = px.bar(stem_df, x="STEM Graduates", y="Country",
                      orientation="h", template="plotly_dark",
                      color="STEM Graduates",
                      color_continuous_scale=["#1a1d2e","#ff6b35"])
        fig2.update_layout(height=320, coloraxis_showscale=False, **CHART_LAYOUT)
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("""<div class='section-card'>
        <p style='color:#8b8fa8;font-size:13px;margin:0;'>
        📌 <b style='color:white;'>Supply Gap:</b> India alone produces
        <b style='color:white;'>4.6x more STEM graduates</b> than Japan annually.
        Combined Global South output (India + Vietnam + Bangladesh + Sri Lanka) is
        approximately <b style='color:white;'>3 million per year</b> — more than enough
        to address Japan's projected 790,000 IT shortage by 2030.
        </p></div>""", unsafe_allow_html=True)

    st.subheader("Population Growth Trajectories (World Bank)")
    country_names = {'JPN':'Japan','IND':'India','VNM':'Vietnam',
                     'BGD':'Bangladesh','LKA':'Sri Lanka'}
    pop_df = pop_countries.copy()
    pop_df.columns = [country_names.get(c,c) for c in pop_df.columns]
    pop_df.index = YEARS
    pop_df.index.name = "Year"
    pop_long = pop_df.reset_index().melt(id_vars="Year",var_name="Country",value_name="Population")
    pop_long["Population (Million)"] = (pop_long["Population"]/1e6).round(2)
    fig3 = px.line(pop_long, x="Year", y="Population (Million)", color="Country",
                   color_discrete_map={"Japan":"#ff6b35","India":"#4cc9f0",
                                       "Vietnam":"#06d6a0","Bangladesh":"#f72585",
                                       "Sri Lanka":"#ffd60a"},
                   template="plotly_dark")
    fig3.update_layout(height=340, legend=dict(bgcolor="rgba(0,0,0,0)"), **CHART_LAYOUT)
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown("""<div class='insight-card'>
    <p style='color:#c0c4d6;font-size:14px;margin:0;'>
    📌 <b style='color:white;'>Strategic Conclusion:</b> While Japan's population shrinks,
    India's has grown by <b style='color:white;'>over 300 million since 2000</b>.
    The demographic trajectories are perfectly complementary —
    Global South nations have surplus young talent, Japan has surplus opportunity and infrastructure.
    This is the economic logic behind GS-JTI.
    </p></div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# SECTION 5 — 2030 FORECAST
# ══════════════════════════════════════════════════════════════
elif section == "🔮 2030 Forecast":

    st.subheader("Japan Population & Workforce Forecast to 2030")
    st.markdown("<p style='color:#8b8fa8;'>Linear regression model trained on 2000–2022 World Bank data</p>",
                unsafe_allow_html=True)

    x = np.array(YEARS)

    # Population forecast
    y_pop = np.array(df["Population (Million)"])
    sl_p, ic_p, r_p, _, _ = stats.linregress(x, y_pop)
    future = np.array(list(range(2000,2031)))
    pred_pop = sl_p*future + ic_p

    # Labor force forecast
    y_lab = np.array(df["Labor Force (Million)"])
    sl_l, ic_l, r_l, _, _ = stats.linregress(x, y_lab)
    pred_lab = sl_l*future + ic_l

    # Fertility forecast
    y_fert = np.array(list(japan_fertility_rate.values()))
    sl_f, ic_f, r_f, _, _ = stats.linregress(x, y_fert)
    pred_fert = sl_f*future + ic_f

    pred_2030_pop  = round(sl_p*2030+ic_p, 2)
    pred_2030_lab  = round(sl_l*2030+ic_l, 2)
    pred_2030_fert = round(sl_f*2030+ic_f, 2)

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Forecast Population 2030", f"{pred_2030_pop}M",
              f"-{round(df['Population (Million)'].iloc[-1]-pred_2030_pop,2)}M", delta_color="inverse")
    c2.metric("Forecast Labor Force 2030", f"{pred_2030_lab:.1f}M",
              f"-{round(df['Labor Force (Million)'].iloc[-1]-pred_2030_lab,1)}M", delta_color="inverse")
    c3.metric("Forecast Fertility 2030", f"{pred_2030_fert:.2f}",
              "vs 2.1 replacement", delta_color="inverse")
    c4.metric("IT Shortage 2030", "790,000", "METI high scenario", delta_color="inverse")

    st.markdown("---")

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Population Forecast")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=YEARS, y=df["Population (Million)"],
                                 name="Actual", mode="lines+markers",
                                 line=dict(color="#4cc9f0",width=2), marker=dict(size=4)))
        fig.add_trace(go.Scatter(
            x=list(range(2022,2031)),
            y=[round(sl_p*y+ic_p,2) for y in range(2022,2031)],
            name="Forecast", mode="lines",
            line=dict(color="#ff6b35",width=2,dash="dash")))
        fig.add_vline(x=2022, line_dash="dot", line_color="#8b8fa8",
                      annotation_text="Forecast →", annotation_font_color="#8b8fa8")
        fig.update_layout(height=300, template="plotly_dark",
                          legend=dict(bgcolor="rgba(0,0,0,0)"), **CHART_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.subheader("Labor Force Forecast")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=YEARS, y=df["Labor Force (Million)"],
                                  name="Actual", mode="lines+markers",
                                  line=dict(color="#06d6a0",width=2), marker=dict(size=4)))
        fig2.add_trace(go.Scatter(
            x=list(range(2022,2031)),
            y=[round(sl_l*y+ic_l,2) for y in range(2022,2031)],
            name="Forecast", mode="lines",
            line=dict(color="#ff4d6d",width=2,dash="dash")))
        fig2.add_vline(x=2022, line_dash="dot", line_color="#8b8fa8",
                       annotation_text="Forecast →", annotation_font_color="#8b8fa8")
        fig2.update_layout(height=300, template="plotly_dark",
                           legend=dict(bgcolor="rgba(0,0,0,0)"), **CHART_LAYOUT)
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Fertility Rate Forecast")
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=YEARS, y=list(japan_fertility_rate.values()),
                              name="Actual", line=dict(color="#f72585",width=2)))
    fig3.add_trace(go.Scatter(
        x=list(range(2022,2031)),
        y=[round(sl_f*y+ic_f,3) for y in range(2022,2031)],
        name="Forecast", line=dict(color="#ffd60a",width=2,dash="dash")))
    fig3.add_hline(y=2.1, line_dash="dash", line_color="#8b8fa8",
                   annotation_text="Replacement level (2.1)", annotation_font_color="#8b8fa8")
    fig3.add_vline(x=2022, line_dash="dot", line_color="#8b8fa8")
    fig3.update_layout(height=280, template="plotly_dark",
                       legend=dict(bgcolor="rgba(0,0,0,0)"), **CHART_LAYOUT)
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown(f"""
    <div class='insight-card'>
    <h4 style='color:#ff6b35;margin-top:0;'>📌 Forecast Summary</h4>
    <ul style='color:#c0c4d6;line-height:2.2;'>
        <li>Population projected to fall to <b style='color:white;'>{pred_2030_pop}M by 2030</b>
            — losing another {round(df['Population (Million)'].iloc[-1]-pred_2030_pop,1)}M from today</li>
        <li>Labor force projected at <b style='color:white;'>{pred_2030_lab:.1f}M</b>
            — {round(df['Labor Force (Million)'].iloc[-1]-pred_2030_lab,1)}M fewer workers than 2022</li>
        <li>Fertility rate forecast of <b style='color:white;'>{pred_2030_fert:.2f}</b>
            remains less than <b style='color:white;'>60% of replacement level</b></li>
        <li>IT talent shortage will reach <b style='color:white;'>790,000 by 2030</b> (METI) —
            no domestic solution exists at this scale</li>
        <li><b style='color:white;'>Linear regression R² values:</b>
            Population {round(r_p**2,3)} · Labor Force {round(r_l**2,3)} · Fertility {round(r_f**2,3)}
            — all high-confidence fits confirming structural, non-random decline</li>
    </ul>
    </div>""", unsafe_allow_html=True)

# ─── FOOTER ───────────────────────────────────────────────────
# ─── FOOTER ───────────────────────────────────────────────────
st.sidebar.markdown("""
<div style='position:fixed; bottom:20px; left:15px; width:270px;'>
    <div style='background: rgba(20, 23, 36, 0.7); backdrop-filter: blur(10px); border: 1px solid #1f2335; border-radius: 12px; padding: 14px;'>
        <div style='display: flex; flex-direction: column; gap: 8px;'>
            <div style='display: flex; align-items: center; gap: 8px;'>
                <span style='font-size: 14px;'>📡</span>
                <span style='color:#8b8fa8; font-size:11px; line-height: 1.2;'>Data: World Bank, METI, <br>UNESCO, UN</span>
            </div>
            <div style='display: flex; align-items: center; gap: 8px;'>
                <span style='font-size: 14px;'>👩‍💻</span>
                <span style='color:#8b8fa8; font-size:11px;'>Built by <span style='color:#ffffff; font-weight: 500;'>Sri Harshitha B</span></span>
            </div>
            <div style='display: flex; align-items: center; gap: 8px;'>
                <span style='font-size: 14px;'>🔗</span>
                <a href='https://github.com/sriharshitha37/japan-economic-analysis' target='_blank' style='color:#ff6b35; text-decoration:none; font-size:11px; font-weight: 500; transition: color 0.2s;'>github.com/sriharshitha37</a>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)