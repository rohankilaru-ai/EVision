"""
Sportsbook odds scrapers for free sources
"""
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import logging
import re

from .base import BaseScraper
from ..models.market import SportsbookOdds, Sport

logger = logging.getLogger(__name__)


class TheOddsAPIScraper(BaseScraper):
    """
    Scraper for The Odds API (free tier)
    https://the-odds-api.com/
    """

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(use_selenium=False)
        self.api_key = api_key
        self.base_url = "https://api.the-odds-api.com/v4"

    def scrape_sport_odds(self, sport: str, market: str = 'h2h') -> List[Dict]:
        """
        Scrape odds for a specific sport

        Args:
            sport: Sport key (e.g., 'americanfootball_nfl', 'basketball_nba')
            market: Market type ('h2h', 'spreads', 'totals')
        Returns:
            List of odds data
        """
        if not self.api_key:
            logger.warning("No API key provided for The Odds API")
            return []

        odds_data = []

        try:
            url = f"{self.base_url}/sports/{sport}/odds"
            params = {
                'apiKey': self.api_key,
                'regions': 'us',
                'markets': market,
                'oddsFormat': 'american'
            }

            response = self.get_json(url, params=params)

            for game in response:
                parsed = self._parse_odds(game, market)
                if parsed:
                    odds_data.extend(parsed)

            logger.info(f"Scraped {len(odds_data)} odds from The Odds API for {sport}")

        except Exception as e:
            logger.error(f"Error scraping The Odds API: {e}")

        return odds_data

    def _parse_odds(self, game_data: Dict, market: str) -> List[Dict]:
        """Parse odds data from API response"""
        odds_list = []

        try:
            event_id = game_data.get('id')
            home_team = game_data.get('home_team')
            away_team = game_data.get('away_team')
            commence_time = datetime.fromisoformat(
                game_data.get('commence_time').replace('Z', '+00:00')
            )

            # Determine sport
            sport_key = game_data.get('sport_key', '')
            sport = self._map_sport(sport_key)

            # Parse each bookmaker's odds
            for bookmaker in game_data.get('bookmakers', []):
                sportsbook = bookmaker.get('title')

                for market_data in bookmaker.get('markets', []):
                    if market_data.get('key') != market:
                        continue

                    odds_dict = {
                        'sportsbook': sportsbook,
                        'source_site': 'TheOddsAPI',
                        'sport': sport,
                        'event_id': event_id,
                        'event_name': f"{away_team} @ {home_team}",
                        'home_team': home_team,
                        'away_team': away_team,
                        'event_time': commence_time,
                        'odds_time': datetime.utcnow(),
                        'is_opening': False,  # TheOddsAPI provides current odds
                        'is_closing': False,
                        'raw_data': game_data
                    }

                    # Parse based on market type
                    if market == 'h2h':
                        for outcome in market_data.get('outcomes', []):
                            if outcome['name'] == home_team:
                                odds_dict['home_ml'] = outcome['price']
                            elif outcome['name'] == away_team:
                                odds_dict['away_ml'] = outcome['price']

                    elif market == 'spreads':
                        for outcome in market_data.get('outcomes', []):
                            if outcome['name'] == home_team:
                                odds_dict['home_spread'] = outcome.get('point')
                                odds_dict['home_spread_odds'] = outcome['price']
                            elif outcome['name'] == away_team:
                                odds_dict['away_spread'] = outcome.get('point')
                                odds_dict['away_spread_odds'] = outcome['price']

                    elif market == 'totals':
                        for outcome in market_data.get('outcomes', []):
                            odds_dict['total_line'] = outcome.get('point')
                            if outcome['name'] == 'Over':
                                odds_dict['over_odds'] = outcome['price']
                            elif outcome['name'] == 'Under':
                                odds_dict['under_odds'] = outcome['price']

                    odds_list.append(odds_dict)

        except Exception as e:
            logger.error(f"Error parsing odds data: {e}")

        return odds_list

    def _map_sport(self, sport_key: str) -> Sport:
        """Map API sport key to our Sport enum"""
        mapping = {
            'americanfootball_nfl': Sport.NFL,
            'basketball_nba': Sport.NBA,
            'baseball_mlb': Sport.MLB,
            'icehockey_nhl': Sport.NHL,
            'americanfootball_ncaaf': Sport.NCAAF,
            'basketball_ncaab': Sport.NCAAB,
            'soccer': Sport.SOCCER
        }
        return mapping.get(sport_key, Sport.OTHER)


class OddsPortalScraper(BaseScraper):
    """
    Scraper for OddsPortal.com
    Note: This is for educational purposes. Always check robots.txt and terms of service.
    """

    def __init__(self):
        super().__init__(use_selenium=True)
        self.base_url = "https://www.oddsportal.com"

    def scrape_sport_page(self, sport: Sport, league: str) -> List[Dict]:
        """
        Scrape odds from OddsPortal sport page

        Args:
            sport: Sport enum
            league: League identifier (e.g., 'nfl', 'nba')
        Returns:
            List of odds data
        """
        odds_data = []

        try:
            # Construct URL based on sport/league
            url = f"{self.base_url}/{league.lower()}/"

            soup = self.get_soup(url)

            # Parse match rows (structure depends on OddsPortal's HTML)
            # This is a simplified example - actual implementation needs to match current HTML structure
            matches = soup.find_all('div', class_='eventRow')

            for match in matches:
                parsed = self._parse_match_row(match, sport)
                if parsed:
                    odds_data.append(parsed)

            logger.info(f"Scraped {len(odds_data)} matches from OddsPortal {league}")

        except Exception as e:
            logger.error(f"Error scraping OddsPortal: {e}")

        return odds_data

    def _parse_match_row(self, match_element, sport: Sport) -> Optional[Dict]:
        """
        Parse individual match row
        Note: This is a template - needs to be updated based on actual HTML structure
        """
        try:
            # Extract match details
            # This is highly dependent on OddsPortal's current HTML structure
            # You'll need to inspect the page and adjust selectors accordingly

            event_name = match_element.find('a', class_='name').text.strip()

            # Extract teams
            teams = event_name.split(' - ')
            home_team = teams[0] if len(teams) > 1 else None
            away_team = teams[1] if len(teams) > 1 else None

            # Extract odds (example - adjust based on actual structure)
            odds_cells = match_element.find_all('div', class_='odds-cell')

            return {
                'sportsbook': 'Average',  # OddsPortal shows averages
                'source_site': 'OddsPortal',
                'sport': sport,
                'event_id': '',  # Generate or extract
                'event_name': event_name,
                'home_team': home_team,
                'away_team': away_team,
                'event_time': None,  # Extract from page
                'home_ml': None,  # Parse from odds_cells
                'away_ml': None,
                'odds_time': datetime.utcnow(),
                'is_opening': False,
                'is_closing': True,  # OddsPortal often shows closing lines
            }

        except Exception as e:
            logger.error(f"Error parsing match row: {e}")
            return None


class ConsensusOddsScraper:
    """
    Aggregate odds from multiple sources to get consensus probability
    """

    def __init__(self, db: Session):
        self.db = db

    def get_consensus_odds(
        self,
        event_id: str,
        min_books: int = 3
    ) -> Optional[Dict]:
        """
        Calculate consensus odds from multiple sportsbooks

        Args:
            event_id: Event identifier
            min_books: Minimum number of books required
        Returns:
            Dict with consensus odds or None
        """
        # Query all odds for this event
        odds = self.db.query(SportsbookOdds).filter(
            SportsbookOdds.event_id == event_id
        ).all()

        if len(odds) < min_books:
            return None

        # Calculate consensus
        home_ml_values = [o.home_ml for o in odds if o.home_ml]
        away_ml_values = [o.away_ml for o in odds if o.away_ml]

        if not home_ml_values or not away_ml_values:
            return None

        # Use median for robustness
        import numpy as np
        consensus_home_ml = int(np.median(home_ml_values))
        consensus_away_ml = int(np.median(away_ml_values))

        return {
            'event_id': event_id,
            'home_ml': consensus_home_ml,
            'away_ml': consensus_away_ml,
            'num_books': len(odds),
            'home_ml_range': (min(home_ml_values), max(home_ml_values)),
            'away_ml_range': (min(away_ml_values), max(away_ml_values))
        }
