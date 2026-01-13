"""
Backtesting framework for EV strategies
"""
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_
import numpy as np
import pandas as pd

from ..models.market import EVOpportunity, Sport
from .probability import EVCalculator, KellyCalculator


class BacktestResult:
    """Container for backtest results"""

    def __init__(self):
        self.trades: List[Dict] = []
        self.total_opportunities = 0
        self.total_trades = 0
        self.wins = 0
        self.losses = 0
        self.total_profit = 0.0
        self.total_wagered = 0.0
        self.daily_pnl: Dict[str, float] = {}

    @property
    def win_rate(self) -> float:
        if self.total_trades == 0:
            return 0.0
        return (self.wins / self.total_trades) * 100

    @property
    def roi(self) -> float:
        if self.total_wagered == 0:
            return 0.0
        return (self.total_profit / self.total_wagered) * 100

    @property
    def avg_ev(self) -> float:
        if not self.trades:
            return 0.0
        return np.mean([t['ev_percentage'] for t in self.trades])

    @property
    def sharpe_ratio(self) -> Optional[float]:
        if not self.trades or len(self.trades) < 2:
            return None

        returns = [t['profit'] / t['stake'] for t in self.trades if t['stake'] > 0]
        if not returns:
            return None

        mean_return = np.mean(returns)
        std_return = np.std(returns)

        if std_return == 0:
            return None

        # Annualize (assuming ~250 trading days)
        sharpe = (mean_return / std_return) * np.sqrt(250)
        return sharpe

    @property
    def max_drawdown(self) -> Optional[float]:
        if not self.trades:
            return None

        cumulative = 0
        peak = 0
        max_dd = 0

        for trade in self.trades:
            cumulative += trade['profit']
            if cumulative > peak:
                peak = cumulative
            drawdown = peak - cumulative
            if drawdown > max_dd:
                max_dd = drawdown

        return max_dd

    def to_dict(self) -> Dict:
        return {
            'total_opportunities': self.total_opportunities,
            'total_trades': self.total_trades,
            'wins': self.wins,
            'losses': self.losses,
            'win_rate': self.win_rate,
            'total_profit': self.total_profit,
            'total_wagered': self.total_wagered,
            'roi': self.roi,
            'avg_ev': self.avg_ev,
            'sharpe_ratio': self.sharpe_ratio,
            'max_drawdown': self.max_drawdown,
            'trades': self.trades
        }


class Backtester:
    """Backtest EV strategies using historical data"""

    def __init__(self, db: Session):
        self.db = db

    def run_backtest(
        self,
        start_date: datetime,
        end_date: datetime,
        min_edge: float = 0.0,
        max_time_to_event_hours: Optional[float] = None,
        min_confidence: Optional[float] = None,
        sport: Optional[Sport] = None,
        kelly_fraction: float = 0.25,
        bankroll: float = 1000.0
    ) -> BacktestResult:
        """
        Run backtest with specified filters

        Args:
            start_date: Start date for backtest
            end_date: End date for backtest
            min_edge: Minimum edge percentage to take trade
            max_time_to_event_hours: Max hours before event to take trade
            min_confidence: Minimum confidence score
            sport: Filter by sport
            kelly_fraction: Fractional Kelly to use for sizing
            bankroll: Starting bankroll
        Returns:
            BacktestResult
        """
        result = BacktestResult()

        # Build query
        query = self.db.query(EVOpportunity).filter(
            and_(
                EVOpportunity.calculated_at >= start_date,
                EVOpportunity.calculated_at <= end_date,
                EVOpportunity.actual_outcome.isnot(None),  # Only settled markets
                EVOpportunity.edge >= min_edge
            )
        )

        if max_time_to_event_hours:
            query = query.filter(EVOpportunity.time_to_event_hours <= max_time_to_event_hours)

        if min_confidence:
            query = query.filter(EVOpportunity.confidence_score >= min_confidence)

        if sport:
            query = query.filter(EVOpportunity.sport == sport)

        opportunities = query.order_by(EVOpportunity.calculated_at).all()

        result.total_opportunities = len(opportunities)

        current_bankroll = bankroll

        for opp in opportunities:
            # Calculate bet size using Kelly
            kelly_size = KellyCalculator.kelly_for_kalshi(
                opp.devigged_prob,
                opp.kalshi_price,
                kelly_fraction
            )

            stake = current_bankroll * kelly_size

            # Skip if stake too small
            if stake < 1.0:
                continue

            # Calculate profit/loss
            won = opp.actual_outcome
            if won:
                profit = stake * ((100 - opp.kalshi_price) / opp.kalshi_price)
                result.wins += 1
            else:
                profit = -stake
                result.losses += 1

            current_bankroll += profit

            # Record trade
            trade = {
                'date': opp.calculated_at,
                'event': opp.event_name,
                'sport': opp.sport.value,
                'kalshi_price': opp.kalshi_price,
                'edge': opp.edge,
                'ev_percentage': opp.ev_percentage,
                'stake': stake,
                'kelly_size': kelly_size,
                'outcome': won,
                'profit': profit,
                'bankroll': current_bankroll
            }
            result.trades.append(trade)
            result.total_trades += 1
            result.total_profit += profit
            result.total_wagered += stake

            # Track daily P&L
            date_key = opp.calculated_at.strftime('%Y-%m-%d')
            result.daily_pnl[date_key] = result.daily_pnl.get(date_key, 0) + profit

        return result

    def analyze_by_regime(
        self,
        start_date: datetime,
        end_date: datetime,
        min_edge: float = 0.0
    ) -> Dict[str, BacktestResult]:
        """
        Analyze performance across different regimes

        Returns:
            Dict of regime -> BacktestResult
        """
        results = {}

        # By sport
        for sport in Sport:
            result = self.run_backtest(
                start_date, end_date,
                min_edge=min_edge,
                sport=sport
            )
            if result.total_trades > 0:
                results[f'sport_{sport.value}'] = result

        # By edge buckets
        edge_buckets = [
            ('small_edge', 0.0, 2.0),
            ('medium_edge', 2.0, 5.0),
            ('large_edge', 5.0, 10.0),
            ('huge_edge', 10.0, 100.0)
        ]

        for name, min_e, max_e in edge_buckets:
            # Query with edge filter
            query = self.db.query(EVOpportunity).filter(
                and_(
                    EVOpportunity.calculated_at >= start_date,
                    EVOpportunity.calculated_at <= end_date,
                    EVOpportunity.actual_outcome.isnot(None),
                    EVOpportunity.edge >= min_e,
                    EVOpportunity.edge < max_e
                )
            )

            opps = query.all()
            if len(opps) > 10:  # Only include if enough samples
                # Run mini backtest
                result = BacktestResult()
                result.total_opportunities = len(opps)

                for opp in opps:
                    if opp.actual_outcome:
                        result.wins += 1
                    else:
                        result.losses += 1
                    result.total_trades += 1

                results[f'edge_{name}'] = result

        return results

    def monte_carlo_simulation(
        self,
        opportunities: List[EVOpportunity],
        num_simulations: int = 1000,
        kelly_fraction: float = 0.25,
        bankroll: float = 1000.0
    ) -> Dict:
        """
        Run Monte Carlo simulation on opportunity set

        Args:
            opportunities: List of EV opportunities
            num_simulations: Number of simulation runs
            kelly_fraction: Fractional Kelly
            bankroll: Starting bankroll
        Returns:
            Dict with simulation statistics
        """
        final_bankrolls = []

        for _ in range(num_simulations):
            current_bankroll = bankroll

            for opp in opportunities:
                kelly_size = KellyCalculator.kelly_for_kalshi(
                    opp.devigged_prob,
                    opp.kalshi_price,
                    kelly_fraction
                )
                stake = current_bankroll * kelly_size

                if stake < 1.0:
                    continue

                # Simulate outcome based on true probability
                won = np.random.random() < opp.devigged_prob

                if won:
                    profit = stake * ((100 - opp.kalshi_price) / opp.kalshi_price)
                else:
                    profit = -stake

                current_bankroll += profit

            final_bankrolls.append(current_bankroll)

        return {
            'mean_final_bankroll': np.mean(final_bankrolls),
            'median_final_bankroll': np.median(final_bankrolls),
            'std_final_bankroll': np.std(final_bankrolls),
            'min_final_bankroll': np.min(final_bankrolls),
            'max_final_bankroll': np.max(final_bankrolls),
            'probability_profit': np.mean([b > bankroll for b in final_bankrolls]),
            'percentile_5': np.percentile(final_bankrolls, 5),
            'percentile_25': np.percentile(final_bankrolls, 25),
            'percentile_75': np.percentile(final_bankrolls, 75),
            'percentile_95': np.percentile(final_bankrolls, 95)
        }
