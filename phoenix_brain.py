import streamlit as st
import pandas as pd
import itertools
from phoenix_brain import MarketBrain
import market_feed 

# --- CONFIG ---
st.set_page_config(page_title="FOX 7.9: NEON GENESIS", layout="wide", page_icon="🦊")
brain = MarketBrain()

# --- STYLING (NEON CYBERPUNK THEME) ---
st.markdown("""
    <style>
    /* MAIN BG */
    .stApp {
        background-color: #0e0e12; /* Deep dark indigo-black */
        color: #e0e0ff; /* Slightly bluish white text */
        font-family: 'Roboto', sans-serif;
    }
    
    /* HEADERS */
    h1, h2, h3 { color: #ffffff !important; text-shadow: 0 0 10px rgba(0, 229, 255, 0.3); }

    /* BOXES - High Vis */
    .gold-box {
        border: 2px solid #39FF14; /* Neon Lime Border */
        background-color: #111a11; /* Dark Green BG */
        padding: 15px; border-radius: 10px; margin-bottom: 10px;
        box-shadow: 0 0 15px rgba(57, 255, 20, 0.2); /* Green Glow */
    }
    .grey-box {
        border: 1px solid #BD00FF; /* Neon Purple Border */
        background-color: #1a1122; /* Dark Purple BG */
        padding: 15px; border-radius: 10px; margin-bottom: 10px; opacity: 0.9;
    }
    
    /* PARLAY CARD - The Main Event */
    .parlay-card {
        background-color: #13131a; /* Deep Hex BG */
        border: 1px solid #333;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        transition: transform 0.2s, box-shadow 0.2s;
        border-left: 5px solid #00E5FF; /* Electric Cyan Accent */
    }
    .parlay-card:hover { 
        transform: translateY(-2px); 
        border-color: #00E5FF; 
        box-shadow: 0 0 25px rgba(0, 229, 255, 0.3); /* Cyan Glow */
    }
    
    /* BADGES - High Contrast Neon */
    .badge-anchor {
        background-color: #00E5FF; color: #000000; /* Cyan BG, Black Text */
        padding: 3px 10px; border-radius: 4px; font-size: 0.8em; font-weight: bold; 
        box-shadow: 0 0 10px rgba(0, 229, 255, 0.5);
    }
    .badge-fighter {
        background-color: #BD00FF; color: #ffffff; /* Purple BG, White Text */
        padding: 3px 10px; border-radius: 4px; font-size: 0.8em; font-weight: bold;
        box-shadow: 0 0 10px rgba(189, 0, 255, 0.5);
    }
    .badge-combo {
        background-color: #222233; color: #00E5FF; 
        padding: 4px 10px; border-radius: 4px; font-weight: bold; 
        border: 1px solid #00E5FF;
    }

    /* METERS */
    .meter-container {background-color: #222; border-radius: 5px; height: 8px; width: 100%; margin-top: 5px; margin-bottom: 5px;}
    .meter-fill {height: 100%; border-radius: 5px; transition: width 0.5s ease-in-out;}
    
    /* GRIDS */
    .wager-grid {display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-top: 10px; margin-bottom: 10px; background-color: #0a0a0f; padding: 10px; border-radius: 5px; border: 1px solid #333;}
    .wager-item { text-align: center; }
    .wager-label { color: #aaaadd; font-size: 0.8em; text-transform: uppercase; letter-spacing: 1px;}
    .wager-value { color: #39FF14; font-weight: bold; font-size: 1.2em; text-shadow: 0 0 5px rgba(57, 255, 20, 0.5);} /* Neon Green Text */
    
    .big-odds { font-size: 2.0em; font-weight: bold; color: #00E5FF; text-align: right; text-shadow: 0 0 10px rgba(0, 229, 255, 0.5);}
    
    /* BUTTONS - Gradient */
    div.stButton > button { 
        width: 100%; padding: 12px; font-weight: bold; border-radius: 8px; border: none;
        background: linear-gradient(90deg, #BD00FF 0%, #00E5FF 100%); /* Purple to Cyan Gradient */
        color: white;
        text-transform: uppercase; letter-spacing: 2px;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        box-shadow: 0 0 20px rgba(189, 0, 255, 0.7);
    }
    hr { border-color: #333; }
    </style>
""", unsafe_allow_html=True)

st.title("🦊 PHOENIX PROTOCOL: NEON GENESIS")

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

# === TAB 1: PARLAY FORGE (AUTO + MANUAL) ===
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
                if role == "NEUTRAL": label = f"🛡️ {row['Team']} ({row['Hard Rock']})"
                
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
                auto_assets = [x for x in clean_options if x['Role'] in ['ANCHOR', 'FIGHTER']]
                if len(auto_assets) < 3: auto_assets = clean_options[:10]
                top_assets = auto_assets[:12]
                
                combos = list(itertools.combinations(top_assets, 2)) + list(itertools.combinations(top_assets, 3))
                
                scored_parlays = []
                for combo in combos:
                    dec_odds = 1.0
                    total_prob = 1.0
                    anchor_count = sum(1 for leg in combo if "ANCHOR" in leg['Label'])
                    
                    for leg in combo:
                        dec_odds *= brain.convert_american_to_decimal(leg['Odds'])
                        total_prob *= leg['Prob']
                    
                    score = (total_prob * 100) + (anchor_count * 10)
                    scored_parlays.append({
                        "Combo": combo, "Odds": brain.convert_decimal_to_american(dec_odds),
                        "Decimal": dec_odds, "Prob": total_prob, "Score": score, "Legs": len(combo)
                    })
                
                top_15 = sorted(scored_parlays, key=lambda x: x['Score'], reverse=True)[:15]
                
                if top_15:
                    st.success(f"FORGED {len(top_15)} OPTIMAL TICKETS:")
                    for idx, p in enumerate(top_15):
                        wager = unit_size * 0.5 
                        payout = wager * p['Decimal']
                        profit = payout - wager
                        prob_pct = p['Prob'] * 100
                        meter_col = "#00E5FF" if prob_pct > 50 else "#BD00FF"
                        
                        legs_html = ""
                        for leg in p['Combo']:
                            badge_class = "badge-anchor" if "ANCHOR" in leg['Label'] else "badge-fighter"
                            icon = "⚓" if "ANCHOR" in leg['Label'] else "⚔️"
                            team_name = leg['Team']
                            
                            # FLUSH LEFT HTML (Fixes Glitch)
                            legs_html += f"""
<div style='display:flex; justify-content:space-between; margin-bottom:4px; border-bottom:1px solid #333; padding-bottom:2px;'>
    <span><span class='{badge_class}'>{icon}</span> <b>{team_name}</b></span>
    <span style='color:#AAA;'>{leg['Odds']}</span>
</div>"""
                        
                        # FLUSH LEFT HTML (Fixes Glitch)
                        card_html = f"""
<div class='parlay-card'>
    <div style='display:flex; justify-content:space-between; align-items:center;'>
        <span class='badge-combo'>#{idx+1} | {p['Legs']}-LEG SLIP</span>
        <span class='big-odds'>{p['Odds']}</span>
    </div>
    <hr>
    {legs_html}
    <hr>
    <div class='wager-grid'>
        <div class='wager-item'><div class='wager-label'>RISK</div><div class='wager-value'>${wager:.2f}</div></div>
        <div class='wager-item'><div class='wager-label'>PROFIT</div><div class='wager-value'>${profit:.2f}</div></div>
        <div class='wager-item'><div class='wager-label'>PAYOUT</div><div class='wager-value' style='color:#00E5FF'>${payout:.2f}</div></div>
    </div>
    <div style='margin-top:5px;'>
        <p style='text-align: center; margin-bottom:2px; font-size:0.8em;'>True Win Probability: {prob_pct:.1f}%</p>
        <div class='meter-container'><div class='meter-fill' style='width:{prob_pct}%; background-color:{meter_col}; box-shadow: 0 0 10px {meter_col};'></div></div>
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
                meter_col = "#00E5FF" if combined_prob > 0.5 else "#BD00FF"
                
                # FLUSH LEFT HTML
                manual_html = f"""
<div class='parlay-card' style='border-left: 5px solid #39FF14;'>
    <h2 style='text-align: center; color: #39FF14; text-shadow: 0 0 10px rgba(57, 255, 20, 0.5);'>CUSTOM SLIP</h2>
    <div class='big-odds' style='color:#39FF14; text-shadow: 0 0 10px rgba(57, 255, 20, 0.5);'>{final_amer if final_amer > 0 else final_amer}</div>
    <div class='wager-grid'>
        <div class='wager-item'><div class='wager-label'>RISK</div><div class='wager-value'>${wager:.2f}</div></div>
        <div class='wager-item'><div class='wager-label'>PROFIT</div><div class='wager-value'>${profit:.2f}</div></div>
        <div class='wager-item'><div class='wager-label'>PAYOUT</div><div class='wager-value' style='color:#39FF14'>${payout:.2f}</div></div>
    </div>
    <div style='margin-top:10px;'>
        <p style='text-align: center;'>True Win Probability: {combined_prob*100:.1f}%</p>
        <div class='meter-container'><div class='meter-fill' style='width: {combined_prob*100}%; background-color: {meter_col}; box-shadow: 0 0 10px {meter_col};'></div></div>
    </div>
</div>"""
                st.markdown(manual_html, unsafe_allow_html=True)

    else:
        st.info("Market Data Empty. Click SCAN in Sidebar.")

# === TAB 2: OPPORTUNITY BOARD (RESTORED) ===
with t2:
    if not market_df.empty:
        st.subheader(f"⚡ RECOMMENDED (POSITIVE EV)")
        
        found_bets = False
        for i, row in market_df.iterrows():
            sharp = row['Global Sharp']
            hero = row['Hard Rock']
            true_prob = brain.calculate_vig_free_prob(sharp)
            kelly_perc = brain.kelly_criterion(true_prob, hero)
            
            if kelly_perc > 0:
                found_bets = True
                bet_dollars = (kelly_perc * 20 / 100) * unit_size
                final_wager = min(bet_dollars, unit_size)
                dec_odds = brain.convert_american_to_decimal(hero)
                total_payout = final_wager * dec_odds
                net_profit = total_payout - final_wager
                
                # Visuals
                prob_pct = true_prob * 100
                meter_color = "#00E5FF" if prob_pct > 65 else "#BD00FF"
                badge = "<span class='badge-anchor'>⚓ ANCHOR</span>" if prob_pct > 65 else "<span class='badge-fighter'>⚔️ FIGHTER</span>"
                
                # FLUSH LEFT HTML
                gold_html = f"""
<div class='gold-box'>
    <div style='display:flex; justify-content:space-between;'><h3>{row['Team']}</h3>{badge}</div>
    <div class='wager-grid' style='border:none; background-color:transparent;'>
        <div class='wager-item'><div class='wager-label'>WAGER</div><div class='wager-value'>${final_wager:.2f}</div></div>
        <div class='wager-item'><div class='wager-label'>PROFIT</div><div class='wager-value'>${net_profit:.2f}</div></div>
        <div class='wager-item'><div class='wager-label'>PAYOUT</div><div class='wager-value' style='color:#00E5FF'>${total_payout:.2f}</div></div>
    </div>
    <div class='meter-container'><div class='meter-fill' style='width:{prob_pct}%; background-color:{meter_color}; box-shadow: 0 0 10px {meter_color};'></div></div>
    <p style='font-size:0.8em; color:#aaaadd'>Odds: {row['Hard Rock']} | Edge: +{kelly_perc:.2f}%</p>
</div>"""
                st.markdown(gold_html, unsafe_allow_html=True)
        
        if not found_bets:
            st.info("No Math Edges found right now. Check Parlay Forge.")
    else:
        st.info("Scan Market first.")

# === TAB 3: TEASER HUNTER (Standard) ===
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
<div class='gold-box' style='border-color:#00E5FF; box-shadow: 0 0 15px rgba(0, 229, 255, 0.2);'>
    <h3 style='color:#00E5FF !important;'>{c['Team']} (Line: {c['Line']})</h3>
    <p><b style='color:#39FF14;'>{c['Status']}</b></p>
    <p style='color:#aaaadd;'>{c['Msg']}</p>
</div>"""
                    st.markdown(teaser_html, unsafe_allow_html=True)
            else:
                st.warning("No Wong Teasers found.")
    elif league_select != "NFL":
        st.warning("Teasers are an NFL Strategy.")
    else:
        st.info("Scan Market first.")
