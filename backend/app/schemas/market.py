from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from ..models.market import Sport


class KalshiMarketBase(BaseModel):
    market_id: str
    event_ticker: str
    title: str
    sport: Optional[Sport]
    yes_price: float
    no_price: float
    volume: int = 0
    open_interest: int = 0


class KalshiMarketResponse(KalshiMarketBase):
    id: int
    event_time: Optional[datetime]
    is_active: bool
    scraped_at: datetime

    class Config:
        from_attributes = True


class SportsbookOddsBase(BaseModel):
    sportsbook: str
    sport: Sport
    event_name: str
    home_ml: Optional[int]
    away_ml: Optional[int]


class SportsbookOddsResponse(SportsbookOddsBase):
    id: int
    odds_time: datetime
    scraped_at: datetime

    class Config:
        from_attributes = True


class EVOpportunityBase(BaseModel):
    kalshi_market_id: str
    sport: Sport
    event_name: str
    kalshi_price: float
    implied_prob_kalshi: float
    sportsbook_odds: int
    implied_prob_sportsbook: float
    devigged_prob: float
    edge: float
    ev: float
    ev_percentage: float


class EVOpportunityResponse(EVOpportunityBase):
    id: int
    kelly_fraction: Optional[float]
    kelly_percentage: Optional[float]
    confidence_score: Optional[float]
    event_time: Optional[datetime]
    time_to_event_hours: Optional[float]
    is_recommended: bool
    calculated_at: datetime

    class Config:
        from_attributes = True


class EVOpportunityList(BaseModel):
    opportunities: List[EVOpportunityResponse]
    total: int
    page: int
    page_size: int


class BacktestRequest(BaseModel):
    sport: Optional[Sport] = None
    start_date: datetime
    end_date: datetime
    min_edge: float = 0.0
    max_time_to_event_hours: Optional[float] = None


class BacktestResult(BaseModel):
    total_opportunities: int
    total_trades: int
    win_rate: float
    total_profit: float
    roi: float
    avg_ev: float
    sharpe_ratio: Optional[float]
    max_drawdown: Optional[float]
