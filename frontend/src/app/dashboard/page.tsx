'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/services/api';
import { EVOpportunity, Sport, StatsSummary } from '@/types';
import { OpportunityCard } from '@/components/OpportunityCard';
import { StatsCard } from '@/components/StatsCard';
import { FilterBar } from '@/components/FilterBar';

export default function DashboardPage() {
  const router = useRouter();
  const { isAuthenticated, user, logout } = useAuth();
  const [filters, setFilters] = useState({
    sport: undefined as Sport | undefined,
    min_edge: 0,
    page: 1,
  });

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  // Fetch EV opportunities
  const { data: opportunitiesData, isLoading: opportunitiesLoading } = useQuery({
    queryKey: ['ev-opportunities', filters],
    queryFn: () =>
      apiClient.getEVOpportunities({
        sport: filters.sport,
        min_edge: filters.min_edge,
        page: filters.page,
        page_size: 20,
      }),
    enabled: isAuthenticated,
  });

  // Fetch stats
  const { data: stats } = useQuery<StatsSummary>({
    queryKey: ['stats-summary'],
    queryFn: () => apiClient.getStatsSummary(7),
    enabled: isAuthenticated,
  });

  if (!isAuthenticated || !user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              EV<span className="text-blue-600">ision</span>
            </h1>

            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm text-gray-600 dark:text-gray-400">{user.email}</p>
                <p className="text-xs text-gray-500 dark:text-gray-500 capitalize">
                  {user.subscription_tier} Plan
                </p>
              </div>
              {user.profile_picture && (
                <img
                  src={user.profile_picture}
                  alt={user.full_name || 'User'}
                  className="w-10 h-10 rounded-full"
                />
              )}
              <button
                onClick={logout}
                className="px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {/* Stats Summary */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <StatsCard
              title="Active Opportunities"
              value={stats.active_opportunities}
              icon="📊"
            />
            <StatsCard
              title="Average Edge"
              value={`${stats.average_edge.toFixed(2)}%`}
              icon="📈"
            />
            <StatsCard title="Sports Tracked" value={Object.keys(stats.by_sport).length} icon="🏆" />
          </div>
        )}

        {/* Free tier notice */}
        {user.subscription_tier === 'free' && (
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mb-6">
            <div className="flex items-center gap-3">
              <span className="text-2xl">ℹ️</span>
              <div>
                <p className="font-semibold text-blue-900 dark:text-blue-100">
                  Free Tier Limitations
                </p>
                <p className="text-sm text-blue-700 dark:text-blue-300">
                  You're limited to opportunities with 2%+ edge. Upgrade to see all opportunities
                  and access backtesting.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Filters */}
        <FilterBar filters={filters} onChange={setFilters} />

        {/* Opportunities List */}
        <div className="mt-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            EV Opportunities
          </h2>

          {opportunitiesLoading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600 dark:text-gray-400">Loading opportunities...</p>
            </div>
          ) : opportunitiesData?.opportunities.length === 0 ? (
            <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg">
              <p className="text-xl text-gray-600 dark:text-gray-400">
                No opportunities found with current filters
              </p>
            </div>
          ) : (
            <>
              <div className="space-y-4">
                {opportunitiesData?.opportunities.map((opp) => (
                  <OpportunityCard key={opp.id} opportunity={opp} />
                ))}
              </div>

              {/* Pagination */}
              {opportunitiesData && opportunitiesData.total > opportunitiesData.page_size && (
                <div className="flex justify-center gap-2 mt-6">
                  <button
                    onClick={() => setFilters({ ...filters, page: filters.page - 1 })}
                    disabled={filters.page === 1}
                    className="px-4 py-2 bg-blue-600 text-white rounded disabled:bg-gray-300 disabled:cursor-not-allowed"
                  >
                    Previous
                  </button>
                  <span className="px-4 py-2 text-gray-700 dark:text-gray-300">
                    Page {filters.page} of{' '}
                    {Math.ceil(opportunitiesData.total / opportunitiesData.page_size)}
                  </span>
                  <button
                    onClick={() => setFilters({ ...filters, page: filters.page + 1 })}
                    disabled={
                      filters.page >=
                      Math.ceil(opportunitiesData.total / opportunitiesData.page_size)
                    }
                    className="px-4 py-2 bg-blue-600 text-white rounded disabled:bg-gray-300 disabled:cursor-not-allowed"
                  >
                    Next
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </main>
    </div>
  );
}
