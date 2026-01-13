"""
Kalshi market scraper
"""
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import logging

from .base import BaseScraper
from ..models.market import KalshiMarket, Sport
from ..core.config import settings

logger = logging.getLogger(__name__)


class KalshiScraper(BaseScraper):
    """Scraper for Kalshi prediction markets"""

    def __init__(self):
        super().__init__(use_selenium=False)
        self.base_url = settings.KALSHI_BASE_URL
        # Kalshi has a public API we can use
        self.api_url = "https://api.elections.kalshi.com/trade-api/v2"

    def scrape_sports_markets(self) -> List[Dict]:
        """
        Scrape sports markets from Kalshi

        Returns:
            List of market data dictionaries
        """
        markets = []

        try:
            # Get all active markets
            # Note: Kalshi's public API structure - adjust based on actual API
            response = self.get_json(f"{self.api_url}/markets", params={
                'status': 'active',
                'limit': 200
            })

            if 'markets' in response:
                for market_data in response['markets']:
                    # Filter for sports-related markets
                    if self._is_sports_market(market_data):
                        parsed = self._parse_market(market_data)
                        if parsed:
                            markets.append(parsed)

            logger.info(f"Scraped {len(markets)} sports markets from Kalshi")

        except Exception as e:
            logger.error(f"Error scraping Kalshi markets: {e}")

        return markets

    def scrape_market_details(self, market_id: str) -> Optional[Dict]:
        """
        Get detailed information for a specific market

        Args:
            market_id: Kalshi market ID
        Returns:
            Market data dict or None
        """
        try:
            response = self.get_json(f"{self.api_url}/markets/{market_id}")
            return self._parse_market(response.get('market', {}))
        except Exception as e:
            logger.error(f"Error scraping market {market_id}: {e}")
            return None

    def _is_sports_market(self, market_data: Dict) -> bool:
        """Check if market is sports-related"""
        title = market_data.get('title', '').lower()
        category = market_data.get('category', '').lower()

        sports_keywords = ['nfl', 'nba', 'mlb', 'nhl', 'ncaa', 'soccer', 'football',
                          'basketball', 'baseball', 'hockey', 'game', 'match', 'win']

        return (
            'sports' in category or
            any(keyword in title for keyword in sports_keywords)
        )

    def _parse_market(self, market_data: Dict) -> Optional[Dict]:
        """Parse market data into our format"""
        try:
            # Extract pricing - Kalshi uses YES/NO contracts
            yes_price = market_data.get('yes_ask', market_data.get('last_price', 50))
            no_price = 100 - yes_price

            # Determine sport
            sport = self._determine_sport(market_data.get('title', ''))

            parsed = {
                'market_id': market_data.get('ticker', market_data.get('id')),
                'event_ticker': market_data.get('event_ticker', ''),
                'title': market_data.get('title', ''),
                'sport': sport,
                'yes_price': yes_price,
                'no_price': no_price,
                'yes_bid': market_data.get('yes_bid'),
                'yes_ask': market_data.get('yes_ask'),
                'no_bid': market_data.get('no_bid'),
                'no_ask': market_data.get('no_ask'),
                'volume': market_data.get('volume', 0),
                'open_interest': market_data.get('open_interest', 0),
                'event_time': self._parse_datetime(market_data.get('event_date')),
                'close_time': self._parse_datetime(market_data.get('close_date')),
                'is_active': market_data.get('status') == 'active',
                'raw_data': market_data
            }

            return parsed

        except Exception as e:
            logger.error(f"Error parsing market data: {e}")
            return None

    def _determine_sport(self, title: str) -> Optional[Sport]:
        """Determine sport from market title"""
        title_lower = title.lower()

        if any(kw in title_lower for kw in ['nfl', 'football']) and 'ncaa' not in title_lower:
            return Sport.NFL
        elif any(kw in title_lower for kw in ['nba', 'basketball']) and 'ncaa' not in title_lower:
            return Sport.NBA
        elif 'mlb' in title_lower or 'baseball' in title_lower:
            return Sport.MLB
        elif 'nhl' in title_lower or 'hockey' in title_lower:
            return Sport.NHL
        elif 'ncaa' in title_lower and 'football' in title_lower:
            return Sport.NCAAF
        elif 'ncaa' in title_lower and 'basketball' in title_lower:
            return Sport.NCAAB
        elif 'soccer' in title_lower or 'premier league' in title_lower:
            return Sport.SOCCER
        else:
            return Sport.OTHER

    def _parse_datetime(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string"""
        if not date_str:
            return None

        try:
            # Adjust format based on actual Kalshi API response
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return None

    def save_markets_to_db(self, db: Session, markets: List[Dict]):
        """Save or update markets in database"""
        for market_data in markets:
            existing = db.query(KalshiMarket).filter(
                KalshiMarket.market_id == market_data['market_id']
            ).first()

            if existing:
                # Update existing
                for key, value in market_data.items():
                    if key != 'raw_data':  # Skip raw_data for updates
                        setattr(existing, key, value)
            else:
                # Create new
                market = KalshiMarket(**market_data)
                db.add(market)

        db.commit()
        logger.info(f"Saved {len(markets)} markets to database")
