import { Sport } from '@/types';

interface FilterBarProps {
  filters: {
    sport: Sport | undefined;
    min_edge: number;
    page: number;
  };
  onChange: (filters: any) => void;
}

export function FilterBar({ filters, onChange }: FilterBarProps) {
  const sports: (Sport | undefined)[] = [
    undefined,
    'nfl',
    'nba',
    'mlb',
    'nhl',
    'ncaaf',
    'ncaab',
    'soccer',
  ];

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
      <div className="flex flex-wrap gap-4">
        <div className="flex-1 min-w-[200px]">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Sport
          </label>
          <select
            value={filters.sport || ''}
            onChange={(e) =>
              onChange({ ...filters, sport: e.target.value || undefined, page: 1 })
            }
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="">All Sports</option>
            {sports.slice(1).map((sport) => (
              <option key={sport} value={sport}>
                {sport?.toUpperCase()}
              </option>
            ))}
          </select>
        </div>

        <div className="flex-1 min-w-[200px]">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Minimum Edge
          </label>
          <select
            value={filters.min_edge}
            onChange={(e) => onChange({ ...filters, min_edge: Number(e.target.value), page: 1 })}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="0">No minimum</option>
            <option value="1">1%+</option>
            <option value="2">2%+</option>
            <option value="3">3%+</option>
            <option value="5">5%+</option>
            <option value="10">10%+</option>
          </select>
        </div>

        <div className="flex items-end">
          <button
            onClick={() => onChange({ sport: undefined, min_edge: 0, page: 1 })}
            className="px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white border border-gray-300 dark:border-gray-600 rounded-md"
          >
            Reset Filters
          </button>
        </div>
      </div>
    </div>
  );
}
