"""
Markets API routes
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime, timedelta

from ..core.database import get_db
from ..models.market import KalshiMarket, SportsbookOdds, EVOpportunity, Sport
from ..models.user import User, SubscriptionTier
from ..schemas.market import (
    KalshiMarketResponse,
    SportsbookOddsResponse,
    EVOpportunityResponse,
    EVOpportunityList,
    BacktestRequest,
    BacktestResult as BacktestResultSchema
)
from ..analytics.backtesting import Backtester
from .auth import get_current_active_user

router = APIRouter(prefix="/markets", tags=["Markets"])


@router.get("/kalshi", response_model=List[KalshiMarketResponse])
async def get_kalshi_markets(
    sport: Optional[Sport] = None,
    is_active: bool = True,
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get Kalshi markets

    Args:
        sport: Filter by sport
        is_active: Filter active markets only
        limit: Max number of results
    Returns:
        List of Kalshi markets
    """
    query = db.query(KalshiMarket).filter(KalshiMarket.is_active == is_active)

    if sport:
        query = query.filter(KalshiMarket.sport == sport)

    markets = query.order_by(KalshiMarket.scraped_at.desc()).limit(limit).all()

    return [KalshiMarketResponse.from_orm(m) for m in markets]


@router.get("/sportsbook-odds", response_model=List[SportsbookOddsResponse])
async def get_sportsbook_odds(
    sport: Optional[Sport] = None,
    sportsbook: Optional[str] = None,
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get sportsbook odds

    Args:
        sport: Filter by sport
        sportsbook: Filter by sportsbook name
        limit: Max number of results
    Returns:
        List of sportsbook odds
    """
    query = db.query(SportsbookOdds)

    if sport:
        query = query.filter(SportsbookOdds.sport == sport)

    if sportsbook:
        query = query.filter(SportsbookOdds.sportsbook == sportsbook)

    odds = query.order_by(SportsbookOdds.scraped_at.desc()).limit(limit).all()

    return [SportsbookOddsResponse.from_orm(o) for o in odds]


@router.get("/ev-opportunities", response_model=EVOpportunityList)
async def get_ev_opportunities(
    sport: Optional[Sport] = None,
    min_edge: float = Query(0.0, ge=0.0),
    min_ev: float = Query(0.0, ge=0.0),
    is_active: bool = True,
    is_recommended: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get EV opportunities

    Args:
        sport: Filter by sport
        min_edge: Minimum edge percentage
        min_ev: Minimum EV percentage
        is_active: Filter active opportunities only
        is_recommended: Filter recommended bets
        page: Page number
        page_size: Items per page
    Returns:
        Paginated list of EV opportunities
    """
    # Free tier gets limited results
    if current_user.subscription_tier == SubscriptionTier.FREE:
        page_size = min(page_size, 10)
        # Free users only see opportunities with higher edge
        min_edge = max(min_edge, 2.0)

    query = db.query(EVOpportunity).filter(
        and_(
            EVOpportunity.is_active == is_active,
            EVOpportunity.edge >= min_edge,
            EVOpportunity.ev_percentage >= min_ev
        )
    )

    if sport:
        query = query.filter(EVOpportunity.sport == sport)

    if is_recommended is not None:
        query = query.filter(EVOpportunity.is_recommended == is_recommended)

    # Count total
    total = query.count()

    # Paginate
    opportunities = query.order_by(
        EVOpportunity.ev_percentage.desc()
    ).offset((page - 1) * page_size).limit(page_size).all()

    return EVOpportunityList(
        opportunities=[EVOpportunityResponse.from_orm(o) for o in opportunities],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/ev-opportunities/{opportunity_id}", response_model=EVOpportunityResponse)
async def get_ev_opportunity(
    opportunity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get specific EV opportunity by ID

    Args:
        opportunity_id: Opportunity ID
    Returns:
        EV opportunity details
    """
    opportunity = db.query(EVOpportunity).filter(
        EVOpportunity.id == opportunity_id
    ).first()

    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    return EVOpportunityResponse.from_orm(opportunity)


@router.post("/backtest", response_model=BacktestResultSchema)
async def run_backtest(
    backtest_request: BacktestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Run backtest on historical EV opportunities

    PAID TIER ONLY

    Args:
        backtest_request: Backtest parameters
    Returns:
        Backtest results
    """
    # Require paid subscription for backtesting
    if current_user.subscription_tier != SubscriptionTier.PAID:
        raise HTTPException(
            status_code=403,
            detail="Backtesting requires paid subscription"
        )

    backtester = Backtester(db)

    result = backtester.run_backtest(
        start_date=backtest_request.start_date,
        end_date=backtest_request.end_date,
        min_edge=backtest_request.min_edge,
        max_time_to_event_hours=backtest_request.max_time_to_event_hours,
        sport=backtest_request.sport
    )

    result_dict = result.to_dict()

    return BacktestResultSchema(
        total_opportunities=result_dict['total_opportunities'],
        total_trades=result_dict['total_trades'],
        win_rate=result_dict['win_rate'],
        total_profit=result_dict['total_profit'],
        roi=result_dict['roi'],
        avg_ev=result_dict['avg_ev'],
        sharpe_ratio=result_dict['sharpe_ratio'],
        max_drawdown=result_dict['max_drawdown']
    )


@router.get("/stats/summary")
async def get_stats_summary(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get summary statistics

    Args:
        days: Number of days to look back
    Returns:
        Summary statistics
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    # Count active opportunities
    active_opps = db.query(EVOpportunity).filter(
        and_(
            EVOpportunity.is_active == True,
            EVOpportunity.calculated_at >= cutoff_date
        )
    ).count()

    # Average edge
    from sqlalchemy import func
    avg_edge = db.query(func.avg(EVOpportunity.edge)).filter(
        and_(
            EVOpportunity.is_active == True,
            EVOpportunity.calculated_at >= cutoff_date
        )
    ).scalar() or 0.0

    # Count by sport
    by_sport = {}
    for sport in Sport:
        count = db.query(EVOpportunity).filter(
            and_(
                EVOpportunity.sport == sport,
                EVOpportunity.is_active == True,
                EVOpportunity.calculated_at >= cutoff_date
            )
        ).count()
        if count > 0:
            by_sport[sport.value] = count

    return {
        'active_opportunities': active_opps,
        'average_edge': round(avg_edge, 2),
        'by_sport': by_sport,
        'period_days': days
    }
