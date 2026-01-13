from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, Text, Enum
from sqlalchemy.sql import func
from datetime import datetime
import enum
from ..core.database import Base


class MarketSource(str, enum.Enum):
    KALSHI = "kalshi"
    SPORTSBOOK = "sportsbook"


class Sport(str, enum.Enum):
    NFL = "nfl"
    NBA = "nba"
    MLB = "mlb"
    NHL = "nhl"
    NCAAF = "ncaaf"
    NCAAB = "ncaab"
    SOCCER = "soccer"
    OTHER = "other"


class KalshiMarket(Base):
    """Kalshi prediction market data"""
    __tablename__ = "kalshi_markets"

    id = Column(Integer, primary_key=True, index=True)

    # Market identification
    market_id = Column(String, unique=True, index=True, nullable=False)
    event_ticker = Column(String, index=True, nullable=False)
    title = Column(String, nullable=False)
    sport = Column(Enum(Sport), nullable=True)

    # Pricing
    yes_price = Column(Float, nullable=False)  # Current YES price (0-100)
    no_price = Column(Float, nullable=False)   # Current NO price (0-100)
    yes_bid = Column(Float, nullable=True)
    yes_ask = Column(Float, nullable=True)
    no_bid = Column(Float, nullable=True)
    no_ask = Column(Float, nullable=True)

    # Market details
    volume = Column(Integer, default=0)
    open_interest = Column(Integer, default=0)
    liquidity = Column(Float, nullable=True)

    # Event details
    event_time = Column(DateTime, nullable=True)
    close_time = Column(DateTime, nullable=True)
    settle_time = Column(DateTime, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    is_settled = Column(Boolean, default=False)
    outcome = Column(Boolean, nullable=True)  # True = YES won, False = NO won

    # Metadata
    raw_data = Column(JSON, nullable=True)  # Store full API response

    # Timestamps
    scraped_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<KalshiMarket(id='{self.market_id}', title='{self.title}')>"


class SportsbookOdds(Base):
    """Sportsbook odds data"""
    __tablename__ = "sportsbook_odds"

    id = Column(Integer, primary_key=True, index=True)

    # Source & identification
    sportsbook = Column(String, index=True, nullable=False)  # e.g., 'DraftKings', 'FanDuel'
    source_site = Column(String, nullable=False)  # e.g., 'OddsPortal'
    sport = Column(Enum(Sport), nullable=False)

    # Event details
    event_id = Column(String, index=True, nullable=False)
    event_name = Column(String, nullable=False)
    home_team = Column(String, nullable=True)
    away_team = Column(String, nullable=True)
    event_time = Column(DateTime, nullable=True)

    # Odds (American format)
    home_ml = Column(Integer, nullable=True)  # Moneyline home
    away_ml = Column(Integer, nullable=True)  # Moneyline away
    draw_ml = Column(Integer, nullable=True)  # Draw (for soccer, etc.)

    # Spread
    home_spread = Column(Float, nullable=True)
    home_spread_odds = Column(Integer, nullable=True)
    away_spread = Column(Float, nullable=True)
    away_spread_odds = Column(Integer, nullable=True)

    # Total
    total_line = Column(Float, nullable=True)
    over_odds = Column(Integer, nullable=True)
    under_odds = Column(Integer, nullable=True)

    # Odds type
    is_opening = Column(Boolean, default=False)
    is_closing = Column(Boolean, default=False)

    # Metadata
    raw_data = Column(JSON, nullable=True)

    # Timestamps
    odds_time = Column(DateTime, nullable=False)  # When these odds were valid
    scraped_at = Column(DateTime, server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<SportsbookOdds(sportsbook='{self.sportsbook}', event='{self.event_name}')>"


class EVOpportunity(Base):
    """Calculated EV opportunities"""
    __tablename__ = "ev_opportunities"

    id = Column(Integer, primary_key=True, index=True)

    # References
    kalshi_market_id = Column(String, index=True, nullable=False)
    sportsbook_odds_id = Column(Integer, nullable=True)

    # Market details
    sport = Column(Enum(Sport), nullable=False)
    event_name = Column(String, nullable=False)
    market_description = Column(Text, nullable=True)

    # Pricing
    kalshi_price = Column(Float, nullable=False)
    implied_prob_kalshi = Column(Float, nullable=False)

    sportsbook_odds = Column(Integer, nullable=False)
    implied_prob_sportsbook = Column(Float, nullable=False)
    devigged_prob = Column(Float, nullable=False)  # After vig removal

    # EV Calculation
    edge = Column(Float, nullable=False)  # Edge in percentage
    ev = Column(Float, nullable=False)    # Expected value
    ev_percentage = Column(Float, nullable=False)  # EV as % of stake

    # Kelly Criterion
    kelly_fraction = Column(Float, nullable=True)
    kelly_percentage = Column(Float, nullable=True)

    # Confidence & Quality
    confidence_score = Column(Float, nullable=True)  # 0-100
    liquidity_score = Column(Float, nullable=True)

    # Event timing
    event_time = Column(DateTime, nullable=True)
    time_to_event_hours = Column(Float, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    is_recommended = Column(Boolean, default=False)

    # Outcome tracking (for backtesting)
    actual_outcome = Column(Boolean, nullable=True)
    profit_loss = Column(Float, nullable=True)

    # Timestamps
    calculated_at = Column(DateTime, server_default=func.now(), nullable=False)
    expires_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<EVOpportunity(event='{self.event_name}', ev={self.ev:.2f}%, edge={self.edge:.2f}%)>"
