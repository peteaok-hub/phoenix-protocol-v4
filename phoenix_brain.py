import pandas as pd
import numpy as np
import os
from datetime import datetime

class MarketBrain:
    def __init__(self):
        self.key_numbers = [3, 7]

    def convert_american_to_decimal(self, odds):
        if pd.isna(odds) or odds == 0: return 0.0
        if odds > 0:
            return 1 + (odds / 100)
        else:
            return 1 + (100 / abs(odds))

    def convert_decimal_to_american(self, decimal_odds):
        if decimal_odds <= 1: return -10000
        if decimal_odds >= 2.00:
            return round((decimal_odds - 1) * 100)
        else:
            return round(-100 / (decimal_odds - 1))

    def get_implied_prob(self, odds):
        if pd.isna(odds) or odds == 0: return 0.0
        if odds > 0:
            return 100 / (odds + 100)
        else:
            return abs(odds) / (abs(odds) + 100)

    def calculate_vig_free_prob(self, odds):
        return self.get_implied_prob(odds)

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

    def kelly_criterion(self, true_prob, hero_odds, fractional_kelly=0.5):
        if hero_odds == 0: return 0
        if hero_odds > 0:
            b = hero_odds / 100
        else:
            b = 100 / abs(hero_odds)
        
        p = true_prob
        q = 1 - p
        
        if b == 0: return 0
        f_star = ((b * p) - q) / b
        return max(0.0, round(f_star * fractional_kelly * 100, 2))

    def validate_teaser(self, line, teaser_points, side):
        # NEW: PLAIN ENGLISH EXPLANATIONS
        if "Fav" in side or "-" in side:
            # Teasing a Favorite DOWN (e.g. -8.5 to -2.5)
            spread = -abs(line) 
            teased_spread = spread + teaser_points
            
            # Wong Criteria: Must cross -7 and -3
            if -8.9 <= spread <= -7.1:
                return "GOLD: ELITE VALUE", True, f"Perfect. Moves line through the Key Numbers 3 & 7."
            
            if -9.5 <= spread <= -6.0:
                 return "SILVER: SOLID VALUE", True, f"Good Play. Captures key numbers."

        if "Dog" in side or "+" in side:
            # Teasing an Underdog UP (e.g. +1.5 to +7.5)
            spread = abs(line)
            
            # Wong Criteria: Must cross 3 and 7
            if 1.1 <= spread <= 2.9:
                return "GOLD: ELITE VALUE", True, f"Perfect. Moves line through the Key Numbers 3 & 7."
            
            if 0.5 <= spread <= 3.5:
                 return "SILVER: SOLID VALUE", True, f"Good Play. Captures key numbers."

        return "NO EDGE", False, "Does not cross key numbers."