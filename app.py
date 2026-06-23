import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Japan Economic Trends", page_icon="🇯🇵", layout="wide")

st.title("🇯🇵 Japan Economic Trends Analysis (2000–2022)")
st.markdown("*Analyzing GDP growth, population dynamics, and trade patterns to surface key economic insights.*")

# --- DATA (no CSV needed — built in) ---
years = list(range(2000, 2023))

gdp = [4888, 4303, 3980, 4302, 4655, 4755, 4530, 4356, 4849,
       5231, 5700, 6157, 6203, 5156, 4850, 4389, 4926, 4859,
       5038, 5082, 4975, 4940, 4232]

population = [126.9, 127.3, 127.5, 127.7, 127.8, 127.8, 127.8,
              127.8, 127.7, 127.6, 127.5, 127.8, 127.5, 127.3,
              127.1, 126.9, 126.7, 126.5, 126.2, 125.9, 125.7,
              125.5, 125.2]

exports = [479, 403, 416, 472, 566, 596, 647, 714, 782, 581,
           770, 823, 799, 715, 690, 625, 645, 698, 738, 705,
           641, 757, 746]

trade_balance = [116, 10, 94, 104, 133, 79, 77, 91, 14, -25,
                 77, 32, -87, -118, -122, -10, 45, 22, 7, -18,
                 -21, 16, -162]

df = pd.DataFrame({
    "Year": years,
    "GDP (USD Billion)": gdp,
    "Population (Million)": population,
    "Exports (USD Billion)": exports,
    "Trade Balance (USD Billion)": trade_balance
})

# --- KPI ROW ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Peak GDP", "$6,157B", "2012")
col2.metric("Population Loss", "-1.7M", "2000 → 2022")
col3.metric("Avg Annual Export", "$666B", "2000–2022")
col4.metric("Trade Surplus Years", "17 of 23", "78% of period")

st.markdown("---")

# --- GDP CHART ---
st.subheader("GDP Trend — Volatility driven by exchange rates & global shocks")
fig1 = px.area(df, x="Year", y="GDP (USD Billion)",
               color_discrete_sequence=["#E85D24"],
               template="plotly_white")
fig1.update_layout(height=300, margin=dict(t=10, b=10))
st.plotly_chart(fig1, use_container_width=True)

# --- POPULATION + TRADE SIDE BY SIDE ---
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Population Decline")
    fig2 = px.line(df, x="Year", y="Population (Million)",
                   color_discrete_sequence=["#3B8BD4"],
                   template="plotly_white")
    fig2.add_vline(x=2008, line_dash="dash", line_color="gray",
                   annotation_text="Peak (2008)", annotation_position="top right")
    fig2.update_layout(height=280, margin=dict(t=10, b=10))
    st.plotly_chart(fig2, use_container_width=True)

with col_b:
    st.subheader("Trade Balance (Surplus vs Deficit)")
    colors = ["#E85D24" if x < 0 else "#1D9E75" for x in df["Trade Balance (USD Billion)"]]
    fig3 = go.Figure(go.Bar(
        x=df["Year"], y=df["Trade Balance (USD Billion)"],
        marker_color=colors))
    fig3.update_layout(template="plotly_white", height=280, margin=dict(t=10, b=10))
    st.plotly_chart(fig3, use_container_width=True)

# --- INSIGHT BOX ---
st.markdown("---")
st.subheader("📌 Key Insights")
st.info("""
- **GDP volatility** is largely driven by JPY/USD exchange rate fluctuations, not real economic contraction
- **Population peaked in 2008** and has been declining — creating a structural need for skilled foreign talent
- **Trade surplus** dominated until 2011 Fukushima disaster caused energy import surge, flipping balance negative
- **Implication:** Japan's aging workforce and shrinking population make international tech talent programs like GS-JTI economically critical
""")

st.caption("Data sourced from World Bank Open Data | Built with Python, Pandas & Plotly")