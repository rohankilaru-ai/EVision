import { EVOpportunity } from '@/types';
import { format } from 'date-fns';

interface OpportunityCardProps {
  opportunity: EVOpportunity;
}

export function OpportunityCard({ opportunity }: OpportunityCardProps) {
  const getEdgeColor = (edge: number) => {
    if (edge >= 10) return 'text-green-600 bg-green-50 dark:text-green-400 dark:bg-green-900/20';
    if (edge >= 5) return 'text-blue-600 bg-blue-50 dark:text-blue-400 dark:bg-blue-900/20';
    return 'text-yellow-600 bg-yellow-50 dark:text-yellow-400 dark:bg-yellow-900/20';
  };

  const getSportEmoji = (sport: string) => {
    const emojis: Record<string, string> = {
      nfl: '🏈',
      nba: '🏀',
      mlb: '⚾',
      nhl: '🏒',
      ncaaf: '🏈',
      ncaab: '🏀',
      soccer: '⚽',
      other: '🎯',
    };
    return emojis[sport] || '🎯';
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-2xl">{getSportEmoji(opportunity.sport)}</span>
            <span className="text-xs font-semibold uppercase text-gray-500 dark:text-gray-400">
              {opportunity.sport}
            </span>
            {opportunity.is_recommended && (
              <span className="px-2 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 text-xs font-semibold rounded">
                ⭐ Recommended
              </span>
            )}
          </div>

          <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">
            {opportunity.event_name}
          </h3>

          {opportunity.market_description && (
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
              {opportunity.market_description}
            </p>
          )}

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <p className="text-gray-500 dark:text-gray-400">Kalshi Price</p>
              <p className="font-semibold text-gray-900 dark:text-white">
                {opportunity.kalshi_price.toFixed(1)}¢
              </p>
              <p className="text-xs text-gray-500">
                ({(opportunity.implied_prob_kalshi * 100).toFixed(1)}%)
              </p>
            </div>

            <div>
              <p className="text-gray-500 dark:text-gray-400">True Prob</p>
              <p className="font-semibold text-gray-900 dark:text-white">
                {(opportunity.devigged_prob * 100).toFixed(1)}%
              </p>
              <p className="text-xs text-gray-500">Devigged</p>
            </div>

            <div>
              <p className="text-gray-500 dark:text-gray-400">Edge</p>
              <p className={`font-bold text-lg ${getEdgeColor(opportunity.edge)}`}>
                +{opportunity.edge.toFixed(2)}%
              </p>
            </div>

            <div>
              <p className="text-gray-500 dark:text-gray-400">EV</p>
              <p className="font-bold text-lg text-green-600 dark:text-green-400">
                +{opportunity.ev_percentage.toFixed(2)}%
              </p>
            </div>
          </div>

          {opportunity.kelly_percentage && opportunity.kelly_percentage > 0 && (
            <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                <strong className="text-gray-900 dark:text-white">Kelly Bet Size:</strong>{' '}
                {opportunity.kelly_percentage.toFixed(2)}% of bankroll
              </p>
            </div>
          )}

          {opportunity.event_time && (
            <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
              Event: {format(new Date(opportunity.event_time), 'MMM d, yyyy h:mm a')}
              {opportunity.time_to_event_hours && (
                <span className="ml-2">
                  ({opportunity.time_to_event_hours.toFixed(1)} hours away)
                </span>
              )}
            </div>
          )}
        </div>

        {opportunity.confidence_score && (
          <div className="ml-4 text-center">
            <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">
              {opportunity.confidence_score.toFixed(0)}
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400">Confidence</div>
          </div>
        )}
      </div>
    </div>
  );
}
