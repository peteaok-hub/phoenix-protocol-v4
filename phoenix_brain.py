import pandas as pd
import numpy as np

class MarketBrain:
    def __init__(self):
        self.key_numbers = [3, 7]

    def convert_american_to_decimal(self, odds):
        """Converts American Odds (-110) to Decimal (1.91)"""
        if odds > 0:
            return 1 + (odds / 100)
        else:
            return 1 + (100 / abs(odds))

    def convert_decimal_to_american(self, decimal_odds):
        """Converts Decimal (2.50) back to American (+150)"""
        if decimal_odds >= 2.00:
            return round((decimal_odds - 1) * 100)
        else:
            return round(-100 / (decimal_odds - 1))

    def get_implied_prob(self, odds):
        """Converts American Odds to Implied Probability"""
        if pd.isna(odds): return 0
        if odds > 0:
            return 100 / (odds + 100)
        else:
            return abs(odds) / (abs(odds) + 100)

    def calculate_vig_free_prob(self, odds):
        """Helper for standard devig"""
        return self.get_implied_prob(odds)

    def calculate_true_probability(self, sharp_odds_side_a, sharp_odds_side_b):
        """Removes the 'juice' from Pinnacle/Sharp lines."""
        prob_a = self.get_implied_prob(sharp_odds_side_a)
        prob_b = self.get_implied_prob(sharp_odds_side_b)
        
        total_implied = prob_a + prob_b
        if total_implied == 0: return 0
        
        true_prob_a = prob_a / total_implied
        return true_prob_a

    def kelly_criterion(self, true_prob, hero_odds, fractional_kelly=0.5):
        """Calculates optimal bet percentage."""
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
        """
        PARLAY ENGINE:
        Multiplies the decimal odds of all legs to find the True Payout.
        Multiplies the win probabilities to find the True Risk.
        """
        if not selected_bets:
            return 0, 0, 0
            
        total_decimal = 1.0
        combined_prob = 1.0
        
        for bet in selected_bets:
            dec = self.convert_american_to_decimal(bet['odds'])
            total_decimal *= dec
            combined_prob *= bet['prob']
            
        final_american = self.convert_decimal_to_american(total_decimal)
        
        return final_american, total_decimal, combined_prob

    def validate_teaser(self, line, teaser_points, side):
        """WONG TEASER VALIDATOR"""
        if "fav" in side.lower() or "(-)" in side.lower():
            spread = -abs(line) 
            teased_spread = spread + teaser_points
            
            if -8.5 <= spread <= -7.5 and teaser_points >= 6:
                return "✅ GOLD (WONG APPROVED)", True, f"Excellent. Moves {spread} → {teased_spread} (Crosses 3 & 7)"
            if spread < -2 and teased_spread > 2:
                 return "⚠️ YELLOW (Crosses Zero)", False, f"Risk. Teasing through Zero is mathematically weak."
            if teased_spread >= -2.5 and spread <= -7.0:
                 return "✅ GREEN (Solid)", True, "Good value. Captures key numbers."

        if "dog" in side.lower() or "(+)" in side.lower():
            spread = abs(line)
            teased_spread = spread + teaser_points
            if 1.5 <= spread <= 2.5 and teaser_points >= 6:
                return "✅ GOLD (WONG APPROVED)", True, f"Excellent. Moves +{spread} → +{teased_spread} (Crosses 3 & 7)"
            if spread >= 1.5 and teased_spread >= 7.0:
                 return "✅ GREEN (Solid)", True, "Good value. Captures key numbers."

        return "❌ RED (Math Mismatch)", False, "Avoid. Does not maximize Key Number value."