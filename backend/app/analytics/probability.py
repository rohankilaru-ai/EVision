"""
Probability calculations, vig removal, and odds conversions
"""
from typing import Tuple, Optional
import numpy as np


class ProbabilityCalculator:
    """Handles all probability and odds conversions"""

    @staticmethod
    def american_to_implied_prob(odds: int) -> float:
        """
        Convert American odds to implied probability
        Args:
            odds: American odds (e.g., -110, +150)
        Returns:
            Implied probability (0-1)
        """
        if odds > 0:
            return 100 / (odds + 100)
        else:
            return abs(odds) / (abs(odds) + 100)

    @staticmethod
    def decimal_to_implied_prob(odds: float) -> float:
        """
        Convert decimal odds to implied probability
        Args:
            odds: Decimal odds (e.g., 1.91, 2.50)
        Returns:
            Implied probability (0-1)
        """
        return 1 / odds

    @staticmethod
    def implied_prob_to_american(prob: float) -> int:
        """
        Convert implied probability to American odds
        Args:
            prob: Probability (0-1)
        Returns:
            American odds
        """
        if prob >= 0.5:
            return int(-100 * prob / (1 - prob))
        else:
            return int(100 * (1 - prob) / prob)

    @staticmethod
    def remove_vig_additive(prob_a: float, prob_b: float) -> Tuple[float, float]:
        """
        Remove vig using additive method (normalize probabilities)
        Most common and simple method

        Args:
            prob_a: Implied probability of outcome A
            prob_b: Implied probability of outcome B
        Returns:
            Tuple of (devigged_prob_a, devigged_prob_b)
        """
        total = prob_a + prob_b
        return (prob_a / total, prob_b / total)

    @staticmethod
    def remove_vig_multiplicative(prob_a: float, prob_b: float) -> Tuple[float, float]:
        """
        Remove vig using multiplicative method
        Assumes equal vig on both sides

        Args:
            prob_a: Implied probability of outcome A
            prob_b: Implied probability of outcome B
        Returns:
            Tuple of (devigged_prob_a, devigged_prob_b)
        """
        overround = prob_a + prob_b
        vig_factor = np.sqrt(1 / overround)

        return (prob_a * vig_factor, prob_b * vig_factor)

    @staticmethod
    def remove_vig_power(prob_a: float, prob_b: float, k: float = 1.0) -> Tuple[float, float]:
        """
        Remove vig using power method
        More sophisticated, accounts for different vig on favorites vs underdogs

        Args:
            prob_a: Implied probability of outcome A
            prob_b: Implied probability of outcome B
            k: Power parameter (default 1.0)
        Returns:
            Tuple of (devigged_prob_a, devigged_prob_b)
        """
        prob_a_k = prob_a ** k
        prob_b_k = prob_b ** k
        total = prob_a_k + prob_b_k

        return (prob_a_k / total, prob_b_k / total)

    @staticmethod
    def get_vig_percentage(prob_a: float, prob_b: float) -> float:
        """
        Calculate the vig (overround) percentage

        Args:
            prob_a: Implied probability of outcome A
            prob_b: Implied probability of outcome B
        Returns:
            Vig percentage (e.g., 4.5 for 4.5% vig)
        """
        return (prob_a + prob_b - 1) * 100

    @staticmethod
    def consensus_probability(probabilities: list, method: str = 'mean') -> float:
        """
        Calculate consensus probability from multiple sources

        Args:
            probabilities: List of probabilities from different sources
            method: 'mean', 'median', or 'weighted_mean'
        Returns:
            Consensus probability
        """
        if method == 'mean':
            return np.mean(probabilities)
        elif method == 'median':
            return np.median(probabilities)
        elif method == 'weighted_mean':
            # Could add weights here if we trust certain books more
            return np.mean(probabilities)
        else:
            return np.mean(probabilities)


class EVCalculator:
    """Expected Value calculations"""

    @staticmethod
    def calculate_ev(
        true_prob: float,
        kalshi_price: float,
        kalshi_fee: float = 0.0
    ) -> float:
        """
        Calculate expected value of a Kalshi bet

        Args:
            true_prob: True probability of outcome (0-1)
            kalshi_price: Kalshi YES price (0-100 cents)
            kalshi_fee: Transaction fee as decimal (e.g., 0.07 for 7%)
        Returns:
            Expected value in cents per $1 wagered
        """
        # Convert kalshi price to probability
        kalshi_prob = kalshi_price / 100

        # Calculate payout if win (100 - price paid)
        payout = 100 - kalshi_price

        # Calculate EV
        ev = (true_prob * payout) - ((1 - true_prob) * kalshi_price) - (kalshi_fee * 100)

        return ev

    @staticmethod
    def calculate_ev_percentage(
        true_prob: float,
        kalshi_price: float,
        kalshi_fee: float = 0.0
    ) -> float:
        """
        Calculate EV as percentage of stake

        Args:
            true_prob: True probability of outcome (0-1)
            kalshi_price: Kalshi YES price (0-100 cents)
            kalshi_fee: Transaction fee as decimal
        Returns:
            EV percentage (e.g., 5.2 for 5.2% edge)
        """
        ev = EVCalculator.calculate_ev(true_prob, kalshi_price, kalshi_fee)
        return (ev / kalshi_price) * 100

    @staticmethod
    def calculate_edge(true_prob: float, kalshi_price: float) -> float:
        """
        Calculate edge (difference between true prob and market price)

        Args:
            true_prob: True probability (0-1)
            kalshi_price: Kalshi price (0-100)
        Returns:
            Edge in percentage points
        """
        kalshi_prob = kalshi_price / 100
        return (true_prob - kalshi_prob) * 100


class KellyCalculator:
    """Kelly Criterion calculations for optimal bet sizing"""

    @staticmethod
    def kelly_criterion(
        probability: float,
        odds: float,
        kelly_fraction: float = 1.0
    ) -> float:
        """
        Calculate optimal bet size using Kelly Criterion

        Args:
            probability: True probability of winning (0-1)
            odds: Decimal odds (e.g., 2.0 for even money)
            kelly_fraction: Fraction of Kelly to bet (0-1, typically 0.25-0.5 for safety)
        Returns:
            Percentage of bankroll to bet (0-1)
        """
        # Kelly formula: f = (bp - q) / b
        # where:
        #   f = fraction of bankroll to bet
        #   b = decimal odds - 1 (net odds)
        #   p = probability of winning
        #   q = probability of losing (1-p)

        b = odds - 1
        p = probability
        q = 1 - probability

        if b <= 0 or p <= 0:
            return 0.0

        kelly = (b * p - q) / b

        # Apply fractional Kelly
        kelly = max(0, kelly * kelly_fraction)

        # Cap at 25% for safety
        kelly = min(kelly, 0.25)

        return kelly

    @staticmethod
    def kelly_for_kalshi(
        true_prob: float,
        kalshi_price: float,
        kelly_fraction: float = 0.25
    ) -> float:
        """
        Calculate Kelly bet size for Kalshi binary contract

        Args:
            true_prob: True probability (0-1)
            kalshi_price: Kalshi YES price (0-100)
            kelly_fraction: Fractional Kelly (default 0.25 for quarter Kelly)
        Returns:
            Percentage of bankroll to bet
        """
        # For binary contract: decimal odds = 100 / price
        decimal_odds = 100 / kalshi_price

        return KellyCalculator.kelly_criterion(true_prob, decimal_odds, kelly_fraction)

    @staticmethod
    def kelly_percentage(
        true_prob: float,
        kalshi_price: float,
        kelly_fraction: float = 0.25
    ) -> float:
        """
        Get Kelly bet size as percentage (e.g., 5.2 for 5.2%)

        Args:
            true_prob: True probability (0-1)
            kalshi_price: Kalshi YES price (0-100)
            kelly_fraction: Fractional Kelly
        Returns:
            Percentage to bet
        """
        kelly = KellyCalculator.kelly_for_kalshi(true_prob, kalshi_price, kelly_fraction)
        return kelly * 100
