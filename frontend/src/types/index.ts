/**
 * TypeScript types for EVision
 */

export type SubscriptionTier = 'free' | 'paid';

export type Sport = 'nfl' | 'nba' | 'mlb' | 'nhl' | 'ncaaf' | 'ncaab' | 'soccer' | 'other';

export interface User {
  id: number;
  email: string;
  full_name?: string;
  profile_picture?: string;
  subscription_tier: SubscriptionTier;
  subscription_start_date?: string;
  subscription_end_date?: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  last_login?: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface KalshiMarket {
  id: number;
  market_id: string;
  event_ticker: string;
  title: string;
  sport?: Sport;
  yes_price: number;
  no_price: number;
  volume: number;
  open_interest: number;
  event_time?: string;
  is_active: boolean;
  scraped_at: string;
}

export interface SportsbookOdds {
  id: number;
  sportsbook: string;
  sport: Sport;
  event_name: string;
  home_ml?: number;
  away_ml?: number;
  odds_time: string;
  scraped_at: string;
}

export interface EVOpportunity {
  id: number;
  kalshi_market_id: string;
  sport: Sport;
  event_name: string;
  market_description?: string;
  kalshi_price: number;
  implied_prob_kalshi: number;
  sportsbook_odds: number;
  implied_prob_sportsbook: number;
  devigged_prob: number;
  edge: number;
  ev: number;
  ev_percentage: number;
  kelly_fraction?: number;
  kelly_percentage?: number;
  confidence_score?: number;
  event_time?: string;
  time_to_event_hours?: number;
  is_recommended: boolean;
  calculated_at: string;
}

export interface EVOpportunityList {
  opportunities: EVOpportunity[];
  total: number;
  page: number;
  page_size: number;
}

export interface BacktestRequest {
  sport?: Sport;
  start_date: string;
  end_date: string;
  min_edge?: number;
  max_time_to_event_hours?: number;
}

export interface BacktestResult {
  total_opportunities: number;
  total_trades: number;
  win_rate: number;
  total_profit: number;
  roi: number;
  avg_ev: number;
  sharpe_ratio?: number;
  max_drawdown?: number;
}

export interface StatsSummary {
  active_opportunities: number;
  average_edge: number;
  by_sport: Record<string, number>;
  period_days: number;
}
