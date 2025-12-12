import streamlit as st
import pandas as pd
import itertools
from phoenix_brain import MarketBrain
import market_feed 

# --- CONFIG ---
st.set_page_config(page_title="FOX 7.7: THE OMEGA", layout="wide", page_icon="🦊")
brain = MarketBrain()

# --- STYLING ---
st.markdown("""
    <style>
    .stApp {background-color: #0e0e0e; color: #e0e0e0; font-family: 'Roboto', sans-serif;}
    
    /* BOXES */
    .gold-box {border: 2px solid #FFD700; background-color: #1a1a00; padding: 15px; border-radius: 10px; margin-bottom: 10px;}
    .grey-box {border: 1px solid #444; background-color: #161b22; padding: 15px; border-radius: 10px; margin-bottom: 10px; opacity: 0.9;}
    
    /* PARLAY CARD */
    .parlay-card {
        background-color: #1a1a1a;
        border: 1px solid #333;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        transition: transform 0.2s;
        border-left: 5px solid #00AAFF;
    }
    .parlay-card:hover { transform: translateY(-2px); border-color: #00AAFF; }
    
    /* BADGES */
    .badge-anchor {background-color: #0044cc; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; border: 1px solid #00AAFF;}
    .badge-fighter {background-color: #663300; color: #ffcc99; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; border: 1px solid #FF9900;}
    .badge-combo {background-color: #333; color: #FFF; padding: 4px 10px; border-radius: 4px; font-weight: bold; border: 1px solid #555;}

    /* METERS */
    .meter-container {background-color: #333; border-radius: 5px; height: 8px; width: 100%; margin-top: 5px; margin-bottom: 5px;}
    .meter-fill {height: 100%; border-radius: 5px; transition: width 0.5s ease-in-out;}
    
    /* GRIDS */
    .wager-grid {display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-top: 10px; margin-bottom: 10px; background-color: #000000; padding: 10px; border-radius: 5px;}
    .wager-item { text-align: center; }
    .wager-label { color: #888; font-size: 0.8em; text-transform: uppercase; }
    .wager-value { color: #00FF00; font-weight: bold; font-size: 1.2em; }
    
    .big-odds { font-size: 2.0em; font-weight: bold; color: #00AAFF; text-align: right; }
    
    /* BUTTONS */
    div.stButton > button { width: 100%; padding: 10px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("🦊 PHOENIX PROTOCOL: THE OMEGA")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ GLOBAL CONFIG")
    league_select = st.radio("Select Market", ["NFL", "NBA"], horizontal=True)
    sport_key = 'americanfootball_nfl' if league_select == "NFL" else 'basketball_nba'
    
    st.markdown("---")
    st.header("💰 MONEY MANAGER")
    unit_size = st.number_input("Standard Unit ($)", value=100.0, step=10.0)
    
    if st.button(f"🔄 SCAN {league_select} MARKET"):
        with st.spinner(f"Scanning Global Lines..."):
            df = market_feed.fetch_live_market_data(sport_key)
            if not df.empty:
                df.to_csv("live_market.csv", index=False)
                st.success("DATA UPDATED.")
            else:
                st.error("No active games found.")

# --- LOAD DATA ---
try:
    market_df = pd.read_csv("live_market.csv")
except:
    market_df = pd.DataFrame()

# --- TABS ---
t1, t2, t3 = st.tabs(["⚡ PARLAY FORGE", "🎯 OPPORTUNITY BOARD", "🧩 TEASER HUNTER"])

# === TAB 1: PARLAY FORGE (AUTO-GENERATE) ===
with t1:
    st.subheader("⚡ PARLAY FORGE")
    st.caption("Combine Anchors ⚓ (Safe) and Fighters ⚔️ (Value) into optimal 2-Leg and 3-Leg Parlays.")
    
    if not market_df.empty:
        # 1. PREPARE ASSETS
        all_options = []
        for i, row in market_df.iterrows():
            sharp = row['Global Sharp']
            true_prob = brain.calculate_vig_free_prob(sharp)
            
            # CLASSIFY
            role = "NEUTRAL"
            if true_prob > 0.60: role = "ANCHOR"
            elif brain.kelly_criterion(true_prob, row['Hard Rock']) > 0: role = "FIGHTER"
            
            # Save for logic
            if true_prob > 0.45:
                label = f"⚓ {row['Team']} ({row['Hard Rock']})" if role == "ANCHOR" else f"⚔️ {row['Team']} ({row['Hard Rock']})"
                all_options.append({
                    "Label": label, "Team": row['Team'], "Odds": row['Hard Rock'], 
                    "Prob": true_prob, "Role": role
                })
        
        # Deduplicate
        options_df = pd.DataFrame(all_options).sort_values(by='Prob', ascending=False).drop_duplicates(subset=['Team'])
        clean_options = options_df.to_dict('records')

        # --- SECTION A: AUTO GENERATOR ---
        if st.button("🔨 AUTO-FORGE TOP 15 SLIPS", type="primary"):
            with st.spinner("Simulating Parlay Combinations..."):
                # Filter High Quality Assets
                auto_assets = [x for x in clean_options if x['Role'] in ['ANCHOR', 'FIGHTER']]
                # Fallback if strict filter fails
                if len(auto_assets) < 3: auto_assets = clean_options[:10]
                
                # Limit input for speed
                top_assets = auto_assets[:12]
                
                # Generate Combos
                combos = list(itertools.combinations(top_assets, 2)) + list(itertools.combinations(top_assets, 3))
                
                scored_parlays = []
                for combo in combos:
                    dec_odds = 1.0
                    total_prob = 1.0
                    anchor_count = sum(1 for leg in combo if leg['Role'] == "ANCHOR")
                    
                    for leg in combo:
                        dec_odds *= brain.convert_american_to_decimal(leg['Odds'])
                        total_prob *= leg['Prob']
                    
                    # Phoenix Score: Prob * 100 + Anchor Bonus
                    score = (total_prob * 100) + (anchor_count * 10)
                    scored_parlays.append({
                        "Combo": combo, "Odds": brain.convert_decimal_to_american(dec_odds),
                        "Decimal": dec_odds, "Prob": total_prob, "Score": score, "Legs": len(combo)
                    })
                
                # Sort Top 15
                top_15 = sorted(scored_parlays, key=lambda x: x['Score'], reverse=True)[:15]
                
                if top_15:
                    st.success(f"FORGED {len(top_15)} OPTIMAL TICKETS:")
                    for idx, p in enumerate(top_15):
                        wager = unit_size * 0.5 
                        payout = wager * p['Decimal']
                        profit = payout - wager
                        prob_pct = p['Prob'] * 100
                        meter_col = "#00AAFF" if prob_pct > 40 else "#FFAA00"
                        
                        legs_html = ""
                        for leg in p['Combo']:
                            badge_class = "badge-anchor" if leg['Role'] == "ANCHOR" else "badge-fighter"
                            icon = "⚓" if leg['Role'] == "ANCHOR" else "⚔️"
                            
                            legs_html += f"""
                            <div style='display:flex; justify-content:space-between; margin-bottom:4px; border-bottom:1px solid #333; padding-bottom:2px;'>
                                <span><span class='{badge_class}'>{icon} {leg['Role']}</span> <b>{leg['Team']}</b></span>
                                <span style='color:#AAA;'>{leg['Odds']}</span>
                            </div>"""
                        
                        # FLUSH LEFT HTML
                        card_html = f"""
<div class='parlay-card'>
    <div style='display:flex; justify-content:space-between; align-items:center;'>
        <span class='badge-combo'>#{idx+1} | {p['Legs']}-LEG SLIP</span>
        <span class='big-odds'>{p['Odds']}</span>
    </div>
    <hr style='border-color:#333; margin:10px 0;'>
    {legs_html}
    <hr style='border-color:#333; margin:10px 0;'>
    <div class='wager-grid'>
        <div class='wager-item'><div class='wager-label'>RISK</div><div class='wager-value'>${wager:.2f}</div></div>
        <div class='wager-item'><div class='wager-label'>PROFIT</div><div class='wager-value'>${profit:.2f}</div></div>
        <div class='wager-item'><div class='wager-label'>PAYOUT</div><div class='wager-value' style='color:#00AAFF'>${payout:.2f}</div></div>
    </div>
    <div style='margin-top:5px;'>
        <p style='text-align: center; margin-bottom:2px; font-size:0.8em;'>True Win Probability: {prob_pct:.1f}%</p>
        <div class='meter-container'><div class='meter-fill' style='width:{prob_pct}%; background-color:{meter_col};'></div></div>
    </div>
</div>"""
                        st.markdown(card_html, unsafe_allow_html=True)
                else:
                    st.warning("No high-value combos found.")

        # --- SECTION B: MANUAL BUILDER (BELOW) ---
        st.markdown("---")
        with st.expander("🛠️ MANUAL BUILDER (CUSTOM SLIP)"):
            selected_labels = st.multiselect("Select Teams:", options_df['Label'].tolist())
            
            if selected_labels:
                selected_data = []
                for label in selected_labels:
                    row = options_df[options_df['Label'] == label].iloc[0]
                    selected_data.append({"odds": row['Odds'], "prob": row['Prob']})
                
                final_amer, total_dec, combined_prob = brain.calculate_parlay_math(selected_data)
                wager = unit_size * 0.5 
                payout = wager * total_dec
                profit = payout - wager
                
                # FLUSH LEFT HTML
                manual_html = f"""
<div class='parlay-card' style='border-left: 5px solid #00FF00;'>
    <h2 style='text-align: center; color: #00FF00;'>CUSTOM SLIP</h2>
    <div class='big-odds'>{final_amer if final_amer > 0 else final_amer}</div>
    <div class='wager-grid'>
        <div class='wager-item'><div class='wager-label'>RISK</div><div class='wager-value'>${wager:.2f}</div></div>
        <div class='wager-item'><div class='wager-label'>PROFIT</div><div class='wager-value'>${profit:.2f}</div></div>
        <div class='wager-item'><div class='wager-label'>PAYOUT</div><div class='wager-value' style='color:#00FF00'>${payout:.2f}</div></div>
    </div>
    <div style='margin-top:10px;'>
        <p style='text-align: center;'>True Win Probability: {combined_prob*100:.1f}%</p>
        <div class='meter-container'><div class='meter-fill' style='width: {combined_prob*100}%; background-color: #00FF00;'></div></div>
    </div>
</div>"""
                st.markdown(manual_html, unsafe_allow_html=True)

    else:
        st.info("Market Data Empty. Click SCAN in Sidebar.")

# === TAB 2: OPPORTUNITY BOARD (VISUAL FIX) ===
with t2:
    if not market_df.empty:
        st.subheader(f"⚡ RECOMMENDED (POSITIVE EV)")
        
        # Filter Logic
        all_bets = []
        for i, row in market_df.iterrows():
            sharp = row['Global Sharp']
            hero = row['Hard Rock']
            true_prob = brain.calculate_vig_free_prob(sharp)
            kelly_perc = brain.kelly_criterion(true_prob, hero)
            
            if kelly_perc > 0:
                bet_dollars = (kelly_perc * 20 / 100) * unit_size
                final_wager = min(bet_dollars, unit_size)
                dec_odds = brain.convert_american_to_decimal(hero)
                total_payout = final_wager * dec_odds
                net_profit = total_payout - final_wager
                
                # Visuals
                prob_pct = true_prob * 100
                meter_color = "#00AAFF" if prob_pct > 65 else "#00FF00"
                badge = "<span class='badge-anchor'>⚓ ANCHOR</span>" if prob_pct > 65 else "<span class='badge-fighter'>⚔️ FIGHTER</span>"
                
                # FLUSH LEFT HTML
                gold_html = f"""
<div class='gold-box'>
    <div style='display:flex; justify-content:space-between;'><h3>{row['Team']}</h3>{badge}</div>
    <div class='wager-grid'>
        <div class='wager-item'><div class='wager-label'>WAGER</div><div class='wager-value'>${final_wager:.2f}</div></div>
        <div class='wager-item'><div class='wager-label'>PROFIT</div><div class='wager-value'>${net_profit:.2f}</div></div>
        <div class='wager-item'><div class='wager-label'>PAYOUT</div><div class='wager-value' style='color:#FFD700'>${total_payout:.2f}</div></div>
    </div>
    <div class='meter-container'><div class='meter-fill' style='width:{prob_pct}%; background-color:{meter_color};'></div></div>
    <p style='font-size:0.8em; color:#888'>Odds: {row['Hard Rock']} | Edge: {kelly_perc:.2f}%</p>
</div>"""
                st.markdown(gold_html, unsafe_allow_html=True)
    else:
        st.info("Scan Market first.")

# === TAB 3: TEASER HUNTER ===
with t3:
    st.subheader("🧩 AUTOMATED TEASER HUNTER")
    if league_select == "NFL" and not market_df.empty:
        if st.button("🕵️ HUNT TEASERS (Zero Fuel)"):
            candidates = []
            for i, row in market_df.iterrows():
                try: line = float(row.get('Spread', 0.0))
                except: line = 0.0
                if line == 0.0: continue
                side = "Favorite (-)" if line < 0 else "Underdog (+)"
                status, is_valid, msg = brain.validate_teaser(line, 6.0, side)
                if is_valid:
                    candidates.append({"Team": row['Team'], "Line": line, "Status": status, "Msg": msg})
            
            if candidates:
                st.success(f"FOUND {len(candidates)} TEASER CANDIDATES")
                for c in candidates:
                    # FLUSH LEFT HTML
                    teaser_html = f"""
<div class='gold-box'>
    <h3>{c['Team']} (Line: {c['Line']})</h3>
    <p><b>{c['Status']}</b></p>
    <p>{c['Msg']}</p>
</div>"""
                    st.markdown(teaser_html, unsafe_allow_html=True)
            else:
                st.warning("No Wong Teasers found.")
    else:
        st.info("Scan Market first.")
