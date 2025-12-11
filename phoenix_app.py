import streamlit as st
import pandas as pd
from phoenix_brain import MarketBrain
import market_feed 

st.set_page_config(page_title="FOX 6.0: TEASER HUNTER", layout="wide", page_icon="🦊")
brain = MarketBrain()

st.markdown("""
    <style>
    .stApp {background-color: #0e1117; color: white;}
    .gold-box {border: 2px solid #FFD700; background-color: #1a1a00; padding: 15px; border-radius: 10px; margin-bottom: 10px;}
    .grey-box {border: 1px solid #444; background-color: #161b22; padding: 15px; border-radius: 10px; margin-bottom: 10px; opacity: 0.9;}
    .parlay-card {border: 2px solid #00AAFF; background-color: #001a33; padding: 20px; border-radius: 15px; margin-top: 20px;}
    .wager-grid {display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-top: 10px; margin-bottom: 10px; background-color: #000000; padding: 10px; border-radius: 5px;}
    .wager-item { text-align: center; }
    .wager-label { color: #888; font-size: 0.8em; text-transform: uppercase; }
    .wager-value { color: #00FF00; font-weight: bold; font-size: 1.2em; }
    .big-odds { font-size: 2.5em; font-weight: bold; color: #00AAFF; text-align: center; }
    </style>
""", unsafe_allow_html=True)

st.title("🦊 PHOENIX PROTOCOL: TEASER HUNTER")

with st.sidebar:
    st.header("⚙️ GLOBAL CONFIG")
    league_select = st.radio("Select Market", ["NFL", "NBA"], horizontal=True)
    if league_select == "NFL": sport_key = 'americanfootball_nfl'
    else: sport_key = 'basketball_nba'
    
    st.markdown("---")
    st.header("💰 MONEY MANAGER")
    unit_size = st.number_input("Standard Unit ($)", value=100.0, step=10.0)
    
    st.markdown("---")
    if st.button(f"🔄 SCAN {league_select} MARKET"):
        with st.spinner(f"Scanning Spreads & Lines..."):
            df = market_feed.fetch_live_market_data(sport_key)
            if not df.empty:
                df.to_csv("live_market.csv", index=False)
                st.success("DATA UPDATED.")
            else:
                st.error("No games found.")

try:
    market_df = pd.read_csv("live_market.csv")
except:
    market_df = pd.DataFrame()

# --- TABS ---
t1, t2, t3 = st.tabs(["🎯 GAME BOARD", "🔗 PARLAY FORGE", "🧩 TEASER HUNTER"])

# === TAB 1: GAME BOARD ===
with t1:
    if not market_df.empty:
        all_bets = []
        for i, row in market_df.iterrows():
            # Basic EV Logic using Moneyline or Spread Price
            sharp = row['Global Sharp']
            hero = row['Hard Rock']
            true_prob = brain.calculate_vig_free_prob(sharp)
            kelly = brain.kelly_criterion(true_prob, hero)
            
            # Display logic same as V5... (Simplified here for brevity)
            if kelly > 0:
                all_bets.append({"Team": row['Team'], "HR": hero, "Edge": kelly})
        
        if all_bets:
            st.subheader("⚡ RECOMMENDED BETS")
            for bet in all_bets:
                st.markdown(f"<div class='gold-box'><h3>{bet['Team']}</h3><p>Odds: {bet['HR']} | Edge: {bet['Edge']}%</p></div>", unsafe_allow_html=True)
        else:
            st.info("No Moneyline Edges. Check Teaser Hunter.")
    else:
        st.info("Scan Games First.")

# === TAB 2: PARLAY FORGE ===
with t2:
    st.subheader("🔗 THE PARLAY FORGE")
    if not market_df.empty:
        # Filter Anchors
        potential_anchors = []
        for i, row in market_df.iterrows():
            sharp = row['Global Sharp']
            true_prob = brain.calculate_vig_free_prob(sharp)
            if true_prob > 0.60: 
                potential_anchors.append({"Team": row['Team'], "Odds": row['Hard Rock'], "Prob": true_prob})
        
        if potential_anchors:
            anchors_df = pd.DataFrame(potential_anchors).sort_values(by='Prob', ascending=False)
            options = [f"{row['Team']} ({row['Odds']})" for i, row in anchors_df.iterrows()]
            selected = st.multiselect("Select Legs:", options)
            
            if selected:
                # (Parlay math same as V5)
                st.info("Calculation Active (See V5 Logic)")
    else:
        st.info("Scan Games First.")

# === TAB 3: TEASER HUNTER (AUTOMATED) ===
with t3:
    st.subheader("🧩 AUTOMATED TEASER HUNTER")
    st.info("Scanning for Wong Criteria: Favorites (-7.5 to -8.5) and Underdogs (+1.5 to +2.5).")
    
    if league_select == "NFL" and not market_df.empty:
        if st.button("🕵️ HUNT TEASERS (Zero Fuel)"):
            candidates = []
            
            for i, row in market_df.iterrows():
                team = row['Team']
                line = row['Spread']
                
                # Determine Side
                side = "Favorite (-)" if line < 0 else "Underdog (+)"
                
                # Run Brain Validation (Standard 6pt Teaser)
                status, is_valid, msg = brain.validate_teaser(line, 6.0, side)
                
                if is_valid:
                    candidates.append({
                        "Team": team,
                        "Line": line,
                        "Status": status,
                        "Msg": msg
                    })
            
            if candidates:
                st.success(f"FOUND {len(candidates)} TEASER CANDIDATES")
                for c in candidates:
                    st.markdown(f"""
                    <div class='gold-box'>
                        <h3>{c['Team']} (Line: {c['Line']})</h3>
                        <p><b>{c['Status']}</b></p>
                        <p>{c['Msg']}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("No Wong Teasers found in current lines.")
    elif league_select != "NFL":
        st.warning("Teasers are an NFL Strategy. Switch League to NFL.")
    else:
        st.info("Scan Market first.")