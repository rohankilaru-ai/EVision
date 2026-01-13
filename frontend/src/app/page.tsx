'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import Link from 'next/link';

export default function Home() {
  const router = useRouter();
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    if (isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, router]);

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto text-center">
          {/* Header */}
          <h1 className="text-6xl font-bold text-gray-900 dark:text-white mb-6">
            EV<span className="text-blue-600">ision</span>
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 mb-8">
            Find Positive Expected Value Opportunities in Sports Betting
          </p>

          {/* Features */}
          <div className="grid md:grid-cols-3 gap-6 my-12">
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
              <div className="text-4xl mb-4">📊</div>
              <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">
                Real-Time Analysis
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Compare Kalshi markets to sportsbook odds in real-time
              </p>
            </div>

            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
              <div className="text-4xl mb-4">🎯</div>
              <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">
                EV Calculation
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Advanced vig removal and probability analysis
              </p>
            </div>

            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
              <div className="text-4xl mb-4">📈</div>
              <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">
                Kelly Criterion
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Optimal bet sizing for long-term profit
              </p>
            </div>
          </div>

          {/* CTA */}
          <div className="space-y-4">
            <Link
              href="/login"
              className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-semibold px-8 py-3 rounded-lg transition-colors"
            >
              Get Started Free
            </Link>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              No credit card required
            </p>
          </div>

          {/* How it works */}
          <div className="mt-16 text-left bg-white dark:bg-gray-800 p-8 rounded-lg shadow-lg">
            <h2 className="text-2xl font-bold mb-6 text-gray-900 dark:text-white">
              How It Works
            </h2>
            <ol className="space-y-4 text-gray-600 dark:text-gray-300">
              <li>
                <strong className="text-gray-900 dark:text-white">1. Data Collection:</strong>{' '}
                We scrape Kalshi prediction markets and sportsbook odds from free sources
              </li>
              <li>
                <strong className="text-gray-900 dark:text-white">2. Vig Removal:</strong>{' '}
                We remove the bookmaker's margin to calculate true probabilities
              </li>
              <li>
                <strong className="text-gray-900 dark:text-white">3. EV Calculation:</strong>{' '}
                We identify markets where Kalshi prices differ from true odds
              </li>
              <li>
                <strong className="text-gray-900 dark:text-white">4. Kelly Sizing:</strong>{' '}
                We calculate optimal bet sizes for long-term growth
              </li>
              <li>
                <strong className="text-gray-900 dark:text-white">5. Backtesting:</strong>{' '}
                We validate strategies with historical data
              </li>
            </ol>
          </div>
        </div>
      </div>
    </main>
  );
}
