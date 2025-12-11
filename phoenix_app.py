import streamlit as st
import pandas as pd
from phoenix_brain import MarketBrain
import market_feed 

# --- CONFIG ---
st.set_page_config(page_title="FOX 7.0: THE APEX", layout="wide", page_icon="🦊")
brain = MarketBrain()

# --- STYLING ---
st.markdown("""
    <style>
    .stApp {background-color: #0e1117; color: white;}
    
    /* GOLD BOX: Positive EV */
    .gold-box {border: 2px solid #FFD700; background-color: #1a1a00; padding: 15px; border-radius: 10px; margin-bottom: 10px;}
    
    /* GREY BOX: Gut Check / No Edge */
    .grey-box {border: 1px solid #444; background-color: #161b22; padding: 15px; border-radius: 10px; margin-bottom: 10px; opacity: 0.9;}
    
    /* PARLAY CARD: Blue Ticket */
    .parlay-card {border: 2px solid #00AAFF; background-color: #001a33; padding: 20px; border-radius: 15px; margin-top: 20px;}
    
    /* GRIDS */
    .wager-grid {display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-top: 10px; margin-bottom: 10px; background-color: #000000; padding: 10px; border-radius: 5px;}
    .wager-item { text-align: center; }
    .wager-label { color: #888; font-size: 0.8em; text-transform: uppercase; }
    .wager-value { color: #00FF00; font-weight: bold; font-size: 1.2em; }
    
    .big-odds { font-size: 2.5em; font-weight: bold; color: #00AAFF; text-align: center; }
    </style>
""", unsafe_allow_html=True)

st.title("🦊 PHOENIX PROTOCOL: THE APEX")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ GLOBAL CONFIG")
    league_select = st.radio("Select Market", ["NFL", "NBA", "EPL (Soccer)"], horizontal=True)
    if league_select == "NFL": sport_key = 'americanfootball_nfl'
    elif league_select == "NBA": sport_key = 'basketball_nba'
    else: sport_key = 'soccer_epl'
    
    st.markdown("---")
    st.header("💰 MONEY MANAGER")
    unit_size = st.number_input("Standard Unit ($)", value=100.0, step=10.0)
    
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
except:
    market_df = pd.DataFrame()

# --- TABS ---
t1, t2, t3 = st.tabs([f"🎯 OPPORTUNITY BOARD", "🔗 PARLAY FORGE", "🧩 TEASER HUNTER"])

# === TAB 1: OPPORTUNITY BOARD (V5 VISUALS RESTORED) ===
with t1:
    if not market_df.empty:
        all_bets = []
        for i, row in market_df.iterrows():
            sharp = row['Global Sharp']
            hero = row['Hard Rock']
            true_prob = brain.calculate_vig_free_prob(sharp)
            kelly_perc = brain.kelly_criterion(true_prob, hero)
            edge_val = kelly_perc if kelly_perc > 0 else (true_prob - brain.get_implied_prob(hero)) * 100
            
            # Financials
            aggression_factor = 20 
            bet_dollars = (kelly_perc * aggression_factor / 100) * unit_size if kelly_perc > 0 else unit_size
            final_wager = min(bet_dollars, unit_size)
            dec_odds = brain.convert_american_to_decimal(hero)
            total_payout = final_wager * dec_odds
            net_profit = total_payout - final_wager
            
            all_bets.append({
                "Matchup": row['Matchup'],
                "Team": row['Team'],
                "Hard Rock": hero,
                "Sharp": sharp,
                "Wager": final_wager,
                "Profit": net_profit,
                "Payout": total_payout,
                "Prob": true_prob,
                "Edge": edge_val,
                "Is_Green": kelly_perc > 0
            })

        # SORT & SPLIT
        bets_df = pd.DataFrame(all_bets).sort_values(by='Edge', ascending=False)
        unique_bets = bets_df.drop_duplicates(subset=['Matchup'], keep='first')
        
        gold_bets = unique_bets[unique_bets['Is_Green'] == True]
        grey_bets = unique_bets[unique_bets['Is_Green'] == False]
        
        # 1. GOLD ZONE
        if not gold_bets.empty:
            st.subheader(f"⚡ RECOMMENDED {league_select} BETS (POSITIVE EV)")
            for i, bet in gold_bets.iterrows():
                st.markdown(f"""
<div class='gold-box'>
    <h3>{bet['Team']} ({bet['Matchup']})</h3>
    <div class='wager-grid'>
        <div class='wager-item'><div class='wager-label'>WAGER</div><div class='wager-value'>${bet['Wager']:.2f}</div></div>
        <div class='wager-item'><div class='wager-label'>PROFIT</div><div class='wager-value'>${bet['Profit']:.2f}</div></div>
        <div class='wager-item'><div class='wager-label'>PAYOUT</div><div class='wager-value' style='color:#FFD700'>${bet['Payout']:.2f}</div></div>
    </div>
    <p>Odds: {bet['Hard Rock']} | Edge: +{bet['Edge']:.2f}% | Prob: {bet['Prob']*100:.1f}%</p>
</div>""", unsafe_allow_html=True)
        
        # 2. GREY ZONE (RESTORED)
        st.subheader("📋 ALL MARKET ACTIONS (GUT CHECK)")
        for i, bet in grey_bets.iterrows():
            st.markdown(f"""
<div class='grey-box'>
    <h4>{bet['Team']} ({bet['Matchup']})</h4>
    <p>Hard Rock: <b>{bet['Hard Rock']}</b> | Sharp Market: {bet['Sharp']}</p>
    <p style='color: #FF4444;'>House Edge: {bet['Edge']:.2f}% (Negative EV)</p>
</div>""", unsafe_allow_html=True)

    else:
        st.info("Market Data Empty. Click SCAN in Sidebar.")

# === TAB 2: PARLAY FORGE (V5.1 ANCHORS RESTORED) ===
with t2:
    st.subheader("🔗 THE PARLAY FORGE")
    st.markdown("Combine **Anchors ⚓** (Safe) and **Fighters ⚔️** (Value) to build your slip.")
    
    if not market_df.empty:
        # Build List with Anchors/Fighters Logic
        all_options = []
        for i, row in market_df.iterrows():
            sharp = row['Global Sharp']
            true_prob = brain.calculate_vig_free_prob(sharp)
            
            # LABEL LOGIC RESTORED
            if true_prob > 0.60:
                label = f"⚓ ANCHOR | {row['Team']} ({row['Hard Rock']}) | {true_prob*100:.1f}% Safe"
            else:
                label = f"⚔️ FIGHTER | {row['Team']} ({row['Hard Rock']}) | {true_prob*100:.1f}% Prob"
                
            all_options.append({
                "Label": label,
                "Team": row['Team'], 
                "Odds": row['Hard Rock'], 
                "Prob": true_prob
            })
        
        if all_options:
            options_df = pd.DataFrame(all_options).sort_values(by='Prob', ascending=False)
            
            # MULTISELECT RESTORED
            selected_labels = st.multiselect("Select Legs to Forge:", options_df['Label'].tolist())
            
            if selected_labels:
                selected_data = []
                st.markdown("---")
                
                # Retrieve data
                for label in selected_labels:
                    row = options_df[options_df['Label'] == label].iloc[0]
                    selected_data.append({"odds": row['Odds'], "prob": row['Prob']})
                
                # Math
                final_amer, total_dec, combined_prob = brain.calculate_parlay_math(selected_data)
                wager = unit_size * 0.5 
                payout = wager * total_dec
                profit = payout - wager
                
                # BLUE TICKET RESTORED
                st.markdown(f"""
<div class='parlay-card'>
    <h2 style='text-align: center; color: #00AAFF;'>COMBINED ODDS</h2>
    <div class='big-odds'>{final_amer if final_amer > 0 else final_amer}</div>
    <div class='wager-grid'>
        <div class='wager-item'><div class='wager-label'>RISK</div><div class='wager-value'>${wager:.2f}</div></div>
        <div class='wager-item'><div class='wager-label'>PROFIT</div><div class='wager-value'>${profit:.2f}</div></div>
        <div class='wager-item'><div class='wager-label'>TOTAL</div><div class='wager-value' style='color:#00AAFF'>${payout:.2f}</div></div>
    </div>
    <hr>
    <p style='text-align: center; font-size: 1.2em;'><b>True Win Probability: {combined_prob*100:.1f}%</b></p>
</div>""", unsafe_allow_html=True)

                if combined_prob > 0.50:
                    st.success("✅ DIAMOND FORGE: This parlay is mathematically stronger than a coin flip.")
                elif combined_prob > 0.30:
                    st.warning("⚠️ STANDARD RISK: Decent payout potential, but variance is high.")
                else:
                    st.error("🔥 HIGH VOLATILITY: This is a lottery ticket. Bet small.")
        else:
            st.info("No games found.")
    else:
        st.info("Scan Market first.")

# === TAB 3: TEASER HUNTER (AUTOMATED) ===
with t3:
    st.subheader("🧩 AUTOMATED TEASER HUNTER")
    st.info("Scanning for Wong Criteria: Favorites (-7.5 to -8.5) and Underdogs (+1.5 to +2.5).")
    
    if league_select == "NFL" and not market_df.empty:
        if st.button("🕵️ HUNT TEASERS (Zero Fuel)"):
            candidates = []
            for i, row in market_df.iterrows():
                line = row.get('Spread', 0.0) 
                if line == 0.0: continue
                
                side = "Favorite (-)" if line < 0 else "Underdog (+)"
                status, is_valid, msg = brain.validate_teaser(line, 6.0, side)
                
                if is_valid:
                    candidates.append({"Team": row['Team'], "Line": line, "Status": status, "Msg": msg})
            
            if candidates:
                st.success(f"FOUND {len(candidates)} TEASER CANDIDATES")
                for c in candidates:
                    st.markdown(f"""
                    <div class='gold-box'>
                        <h3>{c['Team']} (Line: {c['Line']})</h3>
                        <p><b>{c['Status']}</b></p>
                        <p>{c['Msg']}</p>
                    </div>""", unsafe_allow_html=True)
            else:
                st.warning("No Wong Teasers found in current lines.")
    elif league_select != "NFL":
        st.warning("Teasers are an NFL Strategy. Switch League to NFL.")
    else:
        st.info("Scan Market first.")