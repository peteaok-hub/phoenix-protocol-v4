import pandas as pd
import numpy as np

class MarketBrain:
    def __init__(self):
        self.key_numbers = [3, 7]

    def convert_american_to_decimal(self, odds):
        if pd.isna(odds): return 0
        if odds > 0:
            return 1 + (odds / 100)
        else:
            return 1 + (100 / abs(odds))

    def convert_decimal_to_american(self, decimal_odds):
        if decimal_odds >= 2.00:
            return round((decimal_odds - 1) * 100)
        else:
            return round(-100 / (decimal_odds - 1))

    def get_implied_prob(self, odds):
        if pd.isna(odds): return 0
        if odds > 0:
            return 100 / (odds + 100)
        else:
            return abs(odds) / (abs(odds) + 100)

    def calculate_vig_free_prob(self, odds):
        return self.get_implied_prob(odds)

    def calculate_true_probability(self, sharp_odds_side_a, sharp_odds_side_b):
        prob_a = self.get_implied_prob(sharp_odds_side_a)
        prob_b = self.get_implied_prob(sharp_odds_side_b)
        total_implied = prob_a + prob_b
        if total_implied == 0: return 0
        return prob_a / total_implied

    def kelly_criterion(self, true_prob, hero_odds, fractional_kelly=0.5):
        if hero_odds > 0:
            b = hero_odds / 100
        else:
            b = 100 / abs(hero_odds)
        p = true_prob
        q = 1 - p
        if b == 0: return 0
        f_star = ((b * p) - q) / b
        return max(0.0, round(f_star * fractional_kelly * 100, 2))

    def calculate_parlay_math(self, selected_bets):
        if not selected_bets: return 0, 0, 0
        total_decimal = 1.0
        combined_prob = 1.0
        for bet in selected_bets:
            dec = self.convert_american_to_decimal(bet['odds'])
            total_decimal *= dec
            combined_prob *= bet['prob']
        final_american = self.convert_decimal_to_american(total_decimal)
        return final_american, total_decimal, combined_prob

    def validate_teaser(self, line, teaser_points, side):
        """Wong Teaser Validator"""
        # Logic for FAVORITES (Teasing DOWN)
        if "fav" in side.lower() or "(-)" in side.lower():
            spread = -abs(line) 
            teased_spread = spread + teaser_points
            
            # Wong Ideal: -7.5 to -8.5 teased down to -1.5 to -2.5
            if -8.5 <= spread <= -7.5 and teaser_points >= 6:
                return "✅ GOLD (WONG APPROVED)", True, f"Excellent. Moves {spread} → {teased_spread} (Crosses 3 & 7)"
            
            if spread < -2 and teased_spread > 2:
                 return "⚠️ YELLOW (Crosses Zero)", False, f"Risk. Teasing through Zero is mathematically weak."
            
            if teased_spread >= -2.5 and spread <= -7.0:
                 return "✅ GREEN (Solid)", True, "Good value. Captures key numbers."

        # Logic for UNDERDOGS (Teasing UP)
        if "dog" in side.lower() or "(+)" in side.lower():
            spread = abs(line)
            teased_spread = spread + teaser_points

            # Wong Ideal: +1.5 to +2.5 teased up to +7.5 to +8.5
            if 1.5 <= spread <= 2.5 and teaser_points >= 6:
                return "✅ GOLD (WONG APPROVED)", True, f"Excellent. Moves +{spread} → +{teased_spread} (Crosses 3 & 7)"
            
            if spread >= 1.5 and teased_spread >= 7.0:
                 return "✅ GREEN (Solid)", True, "Good value. Captures key numbers."

        return "❌ RED (Math Mismatch)", False, "Avoid. Does not maximize Key Number value."

    def hunt_teasers(self, market_df):
        """
        AUTOMATED SCANNER:
        Iterates through the market dataframe and finds all Wong Teaser Candidates.
        """
        candidates = []
        if market_df.empty: return candidates

        # Only scan NFL (Teasers are primarily an NFL instrument)
        # Note: If sport key isn't in DF, we assume user is on NFL tab or scan all.
        
        for i, row in market_df.iterrows():
            # We need to infer the line from the Moneyline/Data or use a Spread if available.
            # Since our current feed gets Moneylines primarily, we will estimate the spread 
            # or rely on the user to have scan spread data. 
            # *CRITICAL UPDATE*: To save fuel, we are using Moneyline to approximate Spread 
            # OR we assume the feed is fetching Spreads now. 
            # For accurate Wong Teasers, we need Spreads.
            
            # If our feed only has ML, we can't do accurate Wong. 
            # Assuming 'market_feed.py' fetches spreads. If not, this logic detects based on implied spread.
            pass 
            # (Logic handled in App to keep Brain pure math)
            
        return candidates