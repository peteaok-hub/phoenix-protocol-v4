import requests
import pandas as pd
import streamlit as st

try:
    API_KEY = st.secrets["API_KEY"]
except:
    API_KEY = "27f40791c1b27d53ac1dd318939837ef"

REGIONS = 'us,uk,eu,au'
ODDS_FORMAT = 'american'
BOOKMAKERS = 'pinnacle,hardrockbet'

def fetch_live_market_data(sport_key='americanfootball_nfl'):
    # FETCH SPREADS AND MONEYLINE
    url = f'https://api.the-odds-api.com/v4/sports/{sport_key}/odds'
    params = {
        'api_key': API_KEY,
        'regions': REGIONS,
        'markets': 'h2h,spreads', # Grabbing Spreads is CRITICAL for Teasers
        'oddsFormat': ODDS_FORMAT,
        'bookmakers': BOOKMAKERS
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code != 200: return pd.DataFrame()
        
        data = response.json()
        processed_data = []
        
        for game in data:
            matchup = f"{game['away_team']} @ {game['home_team']}"
            
            # Holders
            hr_ml = None
            hr_spread = None
            sharp_ml = None
            
            # Extract Data
            for book in game['bookmakers']:
                if book['key'] == 'hardrockbet':
                    for market in book['markets']:
                        if market['key'] == 'h2h': hr_ml = market['outcomes']
                        if market['key'] == 'spreads': hr_spread = market['outcomes']
                elif book['key'] == 'pinnacle':
                    for market in book['markets']:
                        if market['key'] == 'h2h': sharp_ml = market['outcomes']

            # Process Spreads for Teaser Hunter
            if hr_spread:
                for outcome in hr_spread:
                    team = outcome['name']
                    line = outcome['point']
                    price = outcome['price']
                    
                    # Find matching ML for context (optional)
                    ml_price = 0
                    if hr_ml:
                        for ml in hr_ml:
                            if ml['name'] == team: ml_price = ml['price']
                    
                    # Find Sharp ML for Edge Calc
                    s_price = 0
                    if sharp_ml:
                        for s in sharp_ml:
                            if s['name'] == team: s_price = s['price']

                    processed_data.append({
                        "Matchup": matchup,
                        "Team": team,
                        "Hard Rock": ml_price if ml_price != 0 else price, # Default to spread price if ML missing
                        "Global Sharp": s_price if s_price != 0 else price,
                        "Spread": line, # THE KEY VARIABLE
                        "Spread Price": price
                    })

        return pd.DataFrame(processed_data)
    except:
        return pd.DataFrame()