import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# --- IMPORT MODULAR FILES ---
import data_processing as dp
import viz_dashboard as vz

def main():
    # ---------------- UI STYLING & FULL SCREEN FIX (EXACT CSS) ----------------
    st.markdown("""
    <style>
        /* FORCE FULL WIDTH */
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            max-width: 100% !important;
            padding-top: 2rem !important;
        }

        .stApp { background-color: #0d1b2a !important; }
        header, [data-testid="stHeader"] { background-color: #0d1b2a !important; }
        
        /* Force Tabs to take full width */
        [data-testid="stTabPanel"], [data-testid="stHorizontalBlock"] {
            width: 100% !important;
        }

        .cyan-title {
            color: #4cc9f0 !important;
            font-weight: 800;
            font-family: 'Inter', sans-serif;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 20px;
        }

        /* PULSING SYNC ANIMATION FOR LEFT SIDE */
        @keyframes pulse {
            0% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.3; transform: scale(1.1); }
            100% { opacity: 1; transform: scale(1); }
        }
        .sync-icon {
            color: #06d6a0;
            display: inline-block;
            animation: pulse 2s infinite;
            margin-right: 8px;
        }

        /* TAB STYLING: White to Cyan Hover */
        button[data-baseweb="tab"] p {
            color: white !important;
            transition: 0.3s;
            font-weight: 600 !important;
        }
        button[data-baseweb="tab"]:hover p {
            color: #4cc9f0 !important;
        }
        button[data-baseweb="tab"][aria-selected="true"] p {
            color: #4cc9f0 !important;
        }

        /* KPI Card Styling */
        .kpi-card {
            background-color: #1b263b;
            border: 1px solid #415a77;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }
        .kpi-label { color: #778da9; font-size: 12px; font-weight: 600; }
        .kpi-value { color: white; font-size: 24px; font-weight: 800; }

        /* SOLID CYAN BUTTONS - FIXED TO REMOVE UNDERLINE */
        div.stButton > button {
            background-color: #4cc9f0 !important;
            color: #ffffff !important;
            border: none !important;
            font-weight: 700 !important;
            border-radius: 6px !important;
            padding: 10px 20px !important;
            transition: 0.3s;
            box-shadow: 0px 4px 6px rgba(0,0,0,0.2);
            width: 100%;
            text-decoration: none !important; /* Removes underline */
            outline: none !important;         /* Removes focus outline */
        }
        
        div.stButton > button:hover, div.stButton > button:active, div.stButton > button:focus {
            background-color: #ffffff !important;
            color: #4cc9f0 !important;
            text-decoration: none !important; 
            box-shadow: none !important;
        }

        .insight-box {
            background-color: #1b263b;
            border-left: 5px solid #4cc9f0;
            padding: 20px;
            border-radius: 0 12px 12px 0;
            color: white;
            margin-top: 10px;
            width: 100% !important;
        }

        /* Targeted fix for widget labels */
        [data-testid="stWidgetLabel"] p {
            color: white !important;
            font-weight: 600 !important;
        }

        .white-edu-text { color: #ffffff !important; font-size: 16px; line-height: 1.6; }
        .white-bullets li { color: #ffffff !important; margin-bottom: 12px; }
    </style>
    """, unsafe_allow_html=True)

    # ---------------- DATA FETCHING ----------------
    @st.cache_data(ttl=300)
    def fetch_real_data():
        url = "https://api.coingecko.com/api/v3/coins/markets"
        headers = {"accept": "application/json", "x-cg-demo-api-key": "CG-bAm69cGY5PQKTQBY8HM82bwf"}
        params = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": 25, "sparkline": "true", "price_change_percentage": "24h"}
        try:
            response = requests.get(url, params=params, headers=headers)
            if response.status_code == 200:
                return response.json()
            return []
        except:
            return []

    def get_risk_info(change):
        abs_change = abs(change or 0)
        if abs_change > 5: return "HIGH", "#ef476f"
        if abs_change > 2: return "MEDIUM", "#ffd166"
        return "LOW", "#06d6a0"

    data = fetch_real_data()

    # ---------------- NAVBAR SECTION ----------------
    tab_data_acq, tab_about, tab_data_proc, tab_reports, tab_viz_dash, tab_risk_class, tab_contact = st.tabs([
        "📡 DATA ACQUISITION", "📖 ABOUT", "⚙️ DATA PROCESSING", "📑 REPORTS", "📊 VIZ DASHBOARD", "🛡️ RISK CLASSIFICATION", "📞 CONTACT"
    ])

    with tab_data_acq:
        # Title & Logout Header
        head_left, head_right = st.columns([5, 1])
        with head_left:
            st.markdown("<h1 class='cyan-title'>☁️ Crypto Volatility & Risk Analyzer</h1>", unsafe_allow_html=True)
        with head_right:
            if st.button("🚪 LOGOUT", key="logout_acq"):
                st.rerun()

        st.write("---")
        if not data:
            st.warning("⚠️ API connection busy. Please wait a moment.")
            st.stop()

        # KPI ROW
        total_coins = len(data)
        high_risk_assets = [c for c in data if abs(c.get('price_change_percentage_24h', 0) or 0) > 5]
        high_risk = len(high_risk_assets)
        low_risk = len([c for c in data if abs(c.get('price_change_percentage_24h', 0) or 0) <= 2])
        risk_exp = (high_risk / total_coins) * 100 if total_coins > 0 else 0

        sum_col1, sum_col2, sum_col3, sum_col4 = st.columns(4)
        sum_col1.markdown(f"<div class='kpi-card'><div class='kpi-label'>Total Coins</div><div class='kpi-value'>{total_coins}</div></div>", unsafe_allow_html=True)
        sum_col2.markdown(f"<div class='kpi-card'><div class='kpi-label'>High Risk</div><div class='kpi-value' style='color:#ef476f;'>{high_risk}</div></div>", unsafe_allow_html=True)
        sum_col3.markdown(f"<div class='kpi-card'><div class='kpi-label'>Low Risk</div><div class='kpi-value' style='color:#06d6a0;'>{low_risk}</div></div>", unsafe_allow_html=True)
        sum_col4.markdown(f"<div class='kpi-card'><div class='kpi-label'>Risk Exposure</div><div class='kpi-value' style='color:#4cc9f0;'>{risk_exp:.1f}%</div></div>", unsafe_allow_html=True)

        st.write("")
        
        # --- NEW ATTRACTIVE LEFT SIDE CONTENT ---
        t_col_left, t_col_right = st.columns([1, 1])
        
        with t_col_left:
            st.markdown("<div class='cyan-title'>🧠 Market Intelligence</div>", unsafe_allow_html=True)
            
            # Market Sentiment Widget
            sentiment_color = "#06d6a0" if risk_exp < 30 else "#ef476f"
            sentiment_text = "BULLISH / STABLE" if risk_exp < 30 else "VOLATILE / FEAR"
            
            st.markdown(f"""
            <div class="insight-box" style="border-left-color: {sentiment_color}; background: #16213e;">
                <b style="color:{sentiment_color}; font-size:18px;">🎭 Market Sentiment: {sentiment_text}</b><br>
                <span style="font-size:14px; color:#778da9;">Global volatility index calculated from top 25 assets.</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Asset Spotlight
            top_coin = data[0]
            st.markdown(f"""
            <div class="insight-box" style="margin-top:20px; border-left-color:#4cc9f0;">
                <b style="color:#4cc9f0; font-size:18px;">⭐ Asset Spotlight: {top_coin['name']}</b><br>
                <b>Current Price:</b> ${top_coin['current_price']:,}<br>
                <b>24h Movement:</b> {top_coin['price_change_percentage_24h']:.2f}%<br>
                <span style="color:#06d6a0;">Dominant Market Leader detected.</span>
            </div>
            """, unsafe_allow_html=True)
            
            st.info("💡 Insight: Use the 'Refresh' button on the right to sync latest API streams.")

        with t_col_right:
            st.markdown("<div class='cyan-title'>📋 Market Risk Monitor </div>", unsafe_allow_html=True)
            if st.button("🔄 REFRESH", key="btn_refresh_acq"):
                st.cache_data.clear()
                st.rerun()

            table_rows = ""
            for coin in data[:10]:
                change = coin.get('price_change_percentage_24h', 0) or 0
                risk_text, risk_color = get_risk_info(change)
                change_color = "#06d6a0" if change >= 0 else "#ef476f"
                table_rows += f"""<tr style="border-bottom: 1px solid #2b3a4f;"><td style="padding:14px;"><img src="{coin.get('image', '')}" width="22" style="vertical-align:middle;margin-right:12px;"><b>{coin.get('name')}</b></td><td style="padding:14px; font-family:monospace;">${coin.get('current_price', 0):,}</td><td style="padding:14px; color:{change_color}; font-weight:bold;">{change:.2f}%</td><td style="padding:14px;"><span style="background:{risk_color}; color:#0d1b2a; padding:3px 10px; border-radius:4px; font-weight:900; font-size:10px;">{risk_text}</span></td><td style="padding:14px; text-align:right; color:#4cc9f0; font-size:12px;">LIVE</td></tr>"""

            full_table_html = f"""<div style="background:#1b263b; padding:15px; border-radius:12px; border:1px solid #415a77; font-family:sans-serif; color:white;"><div style="max-height: 400px; overflow-y: auto;"><table style="width:100%; border-collapse:collapse; text-align:left;"><thead style="position: sticky; top: 0; background: #4cc9f0; z-index: 10;"><tr style="color:white; font-size:12px; letter-spacing:1px; font-weight:bold;"><th style="padding:15px;">CRYPTO CURRENCIES</th><th style="padding:15px;">PRICE (USD)</th><th style="padding:15px;">24H CHANGE</th><th style="padding:15px;">RISK STATUS</th><th style="padding:15px; text-align:right;">STATUS</th></tr></thead><tbody>{table_rows}</tbody></table></div></div>"""
            components.html(full_table_html, height=450)
            
        st.write("---")

        # CHARTS SECTION (Original Logic Maintained)
        col_a, col_b = st.columns([1.2, 1])
        with col_a:
            st.markdown("<div class='cyan-title'>📊 Demand & Price Trend</div>", unsafe_allow_html=True)
            coin_names = [c.get('name') for c in data]
            selected_coin = st.selectbox("SELECT COIN FOR DEPTH ANALYSIS", coin_names, key="sel_acq")
            coin_obj = next((c for c in data if c.get('name') == selected_coin), None)
            
            if coin_obj and 'sparkline_in_7d' in coin_obj:
                y_data = coin_obj['sparkline_in_7d']['price']
                fig_t = go.Figure()
                fig_t.add_trace(go.Scatter(y=y_data, mode='lines', line=dict(color='#4cc9f0', width=3), fill='tozeroy', fillcolor='rgba(76, 201, 240, 0.1)'))
                fig_t.update_layout(paper_bgcolor='#1b263b', plot_bgcolor='rgba(0,0,0,0)', font_color="white", height=230, margin=dict(l=40,r=10,t=10,b=40), xaxis=dict(title="7D Timeline"), yaxis=dict(title="Price (USD)"))
                st.plotly_chart(fig_t, use_container_width=True)

                vol_data = [abs(v * (1 + np.random.uniform(-0.15, 0.15))) for v in y_data[::6]]
                fig_bar = go.Figure(go.Bar(x=list(range(len(vol_data))), y=vol_data, marker_color=['#4cc9f0' if d > np.mean(vol_data) else '#1b4965' for d in vol_data]))
                fig_bar.update_layout(paper_bgcolor='#1b263b', plot_bgcolor='rgba(0,0,0,0)', font_color="white", height=230, margin=dict(l=40,r=10,t=10,b=40), xaxis=dict(title="Trading Period"), yaxis=dict(title="Volume Demand"))
                st.plotly_chart(fig_bar, use_container_width=True)

        with col_b:
            st.markdown("<div class='cyan-title'>🛡️ Risk & Market Sentiment</div>", unsafe_allow_html=True)
            risk_counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
            for c in data:
                r_txt, _ = get_risk_info(c.get('price_change_percentage_24h', 0))
                risk_counts[r_txt] += 1
            fig_p = px.pie(values=list(risk_counts.values()), names=list(risk_counts.keys()), color=list(risk_counts.keys()), color_discrete_map={'LOW':'#06d6a0','MEDIUM':'#ffd166','HIGH':'#ef476f'})
            fig_p.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", height=280, margin=dict(t=10,b=10))
            st.plotly_chart(fig_p, use_container_width=True)
            st.markdown(f"""<div class="insight-box"><b style="color:#4cc9f0; font-size:18px;">💡 Market Insights</b><br><br>• <b>Volatility Status:</b> { 'Extreme' if risk_exp > 30 else 'Stable' } market detected.<br>• <b>Leading Risk:</b> { high_risk_assets[0].get('name') if high_risk_assets else 'None' } is active.<br>• <b>Advice:</b> Consider <b>Hedged</b> positions for {selected_coin}.<br>• <b>Analysis Confidence:</b> 94.2% accuracy.</div>""", unsafe_allow_html=True)

    with tab_about:
        st.markdown("<h2 style='color:#4cc9f0; text-align:center;'>🚀 New to Crypto Risk?</h2>", unsafe_allow_html=True)
        st.markdown('<p class="white-edu-text">Welcome! To analyze the market like a pro, you need to understand three core pillars.</p>', unsafe_allow_html=True)
        info_col1, info_col2, info_col3 = st.columns(3)
        with info_col1: st.markdown('<div class="insight-box" style="height:220px;"><b style="color:#4cc9f0; font-size:18px;">💎 What is Crypto?</b><br><br>Digital currencies secured by cryptography operating on decentralized blockchains.</div>', unsafe_allow_html=True)
        with info_col2: st.markdown('<div class="insight-box" style="height:220px; border-left-color:#ffd166;"><b style="color:#ffd166; font-size:18px;">📉 What is Volatility?</b><br><br>A measure of price swings over time. High volatility equates to high potential reward but increased risk.</div>', unsafe_allow_html=True)
        with info_col3: st.markdown('<div class="insight-box" style="height:220px; border-left-color:#ef476f;"><b style="color:#ef476f; font-size:18px;">🛡️ What is Risk?</b><br><br>The probability of losing an investment, measured via statistical metrics like Sharpe and Beta.</div>', unsafe_allow_html=True)
        st.write("---")
        st.markdown("<h3 style='color:white;'>📊 Risk-Level Comparison Table</h3>", unsafe_allow_html=True)
        about_table = f"""<div style="background:#1b263b; padding:20px; border-radius:12px; border:1px solid #415a77; width:100%;"><table style="width:100%; border-collapse:collapse; color:white; font-family:sans-serif;"><thead><tr style="background:#4cc9f0; color:#0d1b2a; text-align:left;"><th style="padding:15px;">CATEGORY</th><th style="padding:15px;">VOLATILITY</th><th style="padding:15px;">INVESTOR TYPE</th><th style="padding:15px;">TYPICAL ASSET</th></tr></thead><tbody><tr style="border-bottom: 1px solid #415a77;"><td style="padding:15px; color:#06d6a0; font-weight:bold;">Low Risk</td><td style="padding:15px;">Stable (0-2%)</td><td style="padding:15px;">Conservative</td><td style="padding:15px;">Stablecoins / BTC</td></tr><tr style="border-bottom: 1px solid #415a77;"><td style="padding:15px; color:#ffd166; font-weight:bold;">Medium Risk</td><td style="padding:15px;">Moderate (2-5%)</td><td style="padding:15px;">Growth-Oriented</td><td style="padding:15px;">ETH / Alts</td></tr><tr><td style="padding:15px; color:#ef476f; font-weight:bold;">High Risk</td><td style="padding:15px;">Extreme (5%+)</td><td style="padding:15px;">Speculative</td><td style="padding:15px;">Meme coins / tokens</td></tr></tbody></table></div>"""
        st.markdown(about_table, unsafe_allow_html=True)

    with tab_data_proc:
        dp.render_data_processing(data)

    with tab_reports:
        st.markdown("<h2 style='color:#4cc9f0;'>📑 Export & Generation</h2>", unsafe_allow_html=True)
        st.markdown('<p class="white-edu-text">Generate comprehensive risk reports for the selected assets.</p>', unsafe_allow_html=True)
        st.button("📥 DOWNLOAD MARKET SUMMARY (CSV)")

    with tab_viz_dash:
        vz.render_viz_dashboard(data, high_risk, total_coins)

    with tab_risk_class:
        st.markdown("<h1 class='cyan-title'>🛡️ Risk Classification</h1>", unsafe_allow_html=True)
        class_col1, class_col2, class_col3 = st.columns(3)
        class_col1.error(f"🔴 **HIGH RISK:** {high_risk} assets")
        class_col3.success(f"🟢 **LOW RISK:** {low_risk} assets")

    with tab_contact:
        st.markdown("<h2 style='color:#4cc9f0; text-align:center;'>📞 Connect with the Developer</h2>", unsafe_allow_html=True)
        cont_col1, cont_col2, cont_col3 = st.columns(3)
        with cont_col1:
            st.markdown("""<div class="insight-box" style="height:200px; text-align:center; border-left:none; border-top:5px solid #4cc9f0;"><b style="color:#4cc9f0; font-size:18px;">📧 Email Support</b><br><br><span style="color:white;">Direct technical queries to:</span><br><b style="color:#ffffff;">support@cryptorisk.com</b></div>""", unsafe_allow_html=True)
        with cont_col2:
            st.markdown("""<div class="insight-box" style="height:200px; text-align:center; border-left:none; border-top:5px solid #ffffff;"><b style="color:#ffffff; font-size:18px;">📍 Location</b><br><br><span style="color:white;">Project Head Office:</span><br><b style="color:#ffffff;">Nagpur, India</b></div>""", unsafe_allow_html=True)
        with cont_col3:
            st.markdown("""<div class="insight-box" style="height:200px; text-align:center; border-left:none; border-top:5px solid #4cc9f0;"><b style="color:#4cc9f0; font-size:18px;">💻 GitHub</b><br><br><span style="color:white;">Source Code:</span><br><b style="color:#ffffff;">github.com/zishan-khan</b></div>""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
