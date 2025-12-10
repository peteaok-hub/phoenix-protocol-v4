import streamlit as st
import pandas as pd
from phoenix_brain import MarketBrain
import market_feed 

# --- CONFIG ---
st.set_page_config(page_title="FOX 5.0: WORLD STAGE", layout="wide", page_icon="🌎")
brain = MarketBrain()

# --- STYLING ---
st.markdown("""
    <style>
    .stApp {background-color: #0e1117; color: white;}
    .gold-box {
        border: 2px solid #FFD700; 
        background-color: #1a1a00; 
        padding: 15px; 
        border-radius: 10px; 
        margin-bottom: 10px;
    }
    .wager-grid {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 10px;
        margin-top: 10px;
        margin-bottom: 10px;
        background-color: #000000;
        padding: 10px;
        border-radius: 5px;
    }
    .wager-item { text-align: center; }
    .wager-label { color: #888; font-size: 0.8em; text-transform: uppercase; }
    .wager-value { color: #00FF00; font-weight: bold; font-size: 1.2em; }
    .reason-text {color: #AAAAAA; font-style: italic; font-size: 0.9em;}
    </style>
""", unsafe_allow_html=True)

st.title("🌎 PHOENIX PROTOCOL: WORLD STAGE")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ GLOBAL CONFIG")
    # NEW: SOCCER ADDED
    league_select = st.radio("Select Market", ["NFL", "NBA", "EPL (Soccer)"], horizontal=True)
    
    # Map Selection to API Key
    if league_select == "NFL": sport_key = 'americanfootball_nfl'
    elif league_select == "NBA": sport_key = 'basketball_nba'
    else: sport_key = 'soccer_epl'
    
    st.markdown("---")
    st.header("💰 MONEY MANAGER")
    unit_size = st.number_input("Max Bet Per Game ($)", value=100.0, step=10.0)
    
    st.markdown("---")
    if st.button(f"🔄 SCAN {league_select} MARKET"):
        with st.spinner(f"Scanning Global Lines for {league_select}..."):
            df = market_feed.fetch_live_market_data(sport_key)
            if not df.empty:
                df.to_csv("live_market.csv", index=False)
                st.success(f"{league_select} DATA UPDATED.")
            else:
                st.error("No active games found.")

# --- LOAD DATA ---
try:
    market_df = pd.read_csv("live_market.csv")
    schedule = market_df['Matchup'].unique().tolist() if not market_df.empty else ["No Data - Click Scan"]
except:
    schedule = ["No Data - Click Scan"]

# --- TABS ---
tab1, tab2 = st.tabs([f"🎯 GLOBAL OPPORTUNITY BOARD", f"🧩 TEASER TOOL"])

# === TAB 1: AUTOPILOT ===
with tab1:
    try:
        if not market_df.empty:
            st.subheader(f"⚡ RECOMMENDED {league_select} BETS")
            found_plays = False
            
            for i, row in market_df.iterrows():
                sharp = row['Global Sharp']
                hero = row['Hard Rock']
                
                true_prob = brain.calculate_vig_free_prob(sharp)
                kelly_perc = brain.kelly_criterion(true_prob, hero)
                
                # Bet Sizing
                aggression_factor = 20 
                bet_dollars = (kelly_perc * aggression_factor / 100) * unit_size
                final_wager = min(bet_dollars, unit_size)
                
                # Profits
                dec_odds = brain.convert_american_to_decimal(hero)
                total_payout = final_wager * dec_odds
                net_profit = total_payout - final_wager
                
                if kelly_perc > 0:
                    found_plays = True
                    html_block = f"""
<div class='gold-box'>
    <h3>{row['Team']} ({row['Matchup']})</h3>
    <p><b>Hard Rock: {hero}</b> vs Global Sharp: {sharp}</p>
    <div class='wager-grid'>
        <div class='wager-item'>
            <div class='wager-label'>WAGER (RISK)</div>
            <div class='wager-value'>${final_wager:.2f}</div>
        </div>
        <div class='wager-item'>
            <div class='wager-label'>TO WIN (PROFIT)</div>
            <div class='wager-value'>${net_profit:.2f}</div>
        </div>
        <div class='wager-item'>
            <div class='wager-label'>TOTAL PAYOUT</div>
            <div class='wager-value' style='color: #FFD700;'>${total_payout:.2f}</div>
        </div>
    </div>
    <p><b>Win Probability: {true_prob*100:.1f}%</b> | Edge: {kelly_perc}%</p>
    <p class='reason-text'>Reason: Hard Rock Price ({hero}) beats Global Market ({sharp}).</p>
</div>
"""
                    st.markdown(html_block, unsafe_allow_html=True)
            
            if not found_plays:
                st.info("No global edges found right now.")
            
            with st.expander("View Global Market Lines"):
                st.dataframe(market_df)
        else:
            st.info("Market Data Empty. Click SCAN in Sidebar.")
    except:
        st.info("System Ready. Click SCAN in Sidebar.")

# === TAB 2: TEASER TOOL ===
with tab2:
    if "Soccer" in league_select:
        st.warning("⚠️ TEASERS NOT AVAILABLE FOR SOCCER")
        st.info("Teasers are a US Sports instrument (NFL/NBA). Please switch leagues to use this tool.")
    else:
        st.subheader(f"🛡️ WONG STRATEGY: {league_select}")
        selected_game = st.selectbox("1. Select Target Game", schedule)
        
        try:
            vis_team, home_team = selected_game.split(" @ ")
            teams = [vis_team, home_team]
        except:
            teams = ["Away Team", "Home Team"]

        c1, c2, c3 = st.columns(3)
        with c1:
            target_team = st.radio("Who are you betting?", teams, horizontal=True)
        with c2:
            t_line = st.number_input(f"Enter Line for {target_team}", value=0.0, step=0.5)
            t_points = st.selectbox("Teaser Points", [6.0, 6.5, 7.0, 10.0])
        with c3:
            if t_line < 0:
                pos_type = "Favorite (-)"
                new_line = -abs(t_line) + t_points
                display_line = f"{new_line}" if new_line < 0 else f"+{new_line}"
                st.info("Detected: FAVORITE")
            else:
                pos_type = "Underdog (+)"
                new_line = t_line + t_points
                display_line = f"+{new_line}"
                st.info("Detected: UNDERDOG")
            st.metric("Teased Line", display_line)

        status, is_valid, msg = brain.validate_teaser(t_line, t_points, pos_type)
        if is_valid:
            t_html = f"<div class='gold-box'><h3>{status}</h3><p>{msg}</p></div>"
            st.markdown(t_html, unsafe_allow_html=True)
        else:
            st.error(f"{status}: {msg}")