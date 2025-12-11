import requests
import pandas as pd
import streamlit as st

# --- CONFIGURATION ---
# SECURITY: Try to get key from Secrets (Web), failover to Hardcoded (Local)
try:
    API_KEY = st.secrets["API_KEY"]
except:
    API_KEY = "27f40791c1b27d53ac1dd318939837ef"

REGIONS = 'us,uk,eu,au' 
MARKETS = 'h2h,spreads' 
ODDS_FORMAT = 'american'
BOOKMAKERS = 'pinnacle,hardrockbet,betfair_ex_uk,betfair_ex_au,williamhill'

def fetch_live_market_data(sport_key='americanfootball_nfl'):
    url = f'https://api.the-odds-api.com/v4/sports/{sport_key}/odds'
    params = {
        'api_key': API_KEY,
        'regions': REGIONS,
        'markets': MARKETS,
        'oddsFormat': ODDS_FORMAT,
        'bookmakers': BOOKMAKERS
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code != 200:
            return pd.DataFrame()
        data = response.json()
        processed_data = []
        for game in data:
            matchup = f"{game['away_team']} @ {game['home_team']}"
            sharp_odds = {} 
            hero_odds = {}
            for book in game['bookmakers']:
                key = book['key']
                for market in book['markets']:
                    if market['key'] == 'h2h':
                        for outcome in market['outcomes']:
                            team = outcome['name']
                            price = outcome['price']
                            if key in ['pinnacle', 'betfair_ex_uk', 'betfair_ex_au']:
                                sharp_odds[team] = price
                            elif key == 'hardrockbet': 
                                hero_odds[team] = price
            for team, h_price in hero_odds.items():
                if team in sharp_odds:
                    processed_data.append({
                        "Matchup": matchup,
                        "Team": team,
                        "Hard Rock": h_price,
                        "Global Sharp": sharp_odds[team],
                        "Sport": sport_key
                    })
        return pd.DataFrame(processed_data)
    except:
        return pd.DataFrame()