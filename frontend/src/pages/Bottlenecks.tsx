import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { AlertTriangle, Filter, Loader2, ArrowUpDown } from 'lucide-react';
import { BottleneckCard } from '../components/BottleneckCard';
import { bottlenecksApi, communitiesApi } from '../services/api';

export function Bottlenecks() {
  const [minScore, setMinScore] = useState(0);
  const [selectedCommunity, setSelectedCommunity] = useState<string | null>(null);
  const [limit, setLimit] = useState(20);

  const { data, isLoading, error } = useQuery({
    queryKey: ['bottlenecks', minScore, selectedCommunity, limit],
    queryFn: () =>
      bottlenecksApi.getBottlenecks({
        min_score: minScore,
        community_id: selectedCommunity || undefined,
        limit,
      }),
  });

  const { data: communitiesData } = useQuery({
    queryKey: ['communities'],
    queryFn: () => communitiesApi.getCommunities({ limit: 50 }),
  });

  const { data: summary } = useQuery({
    queryKey: ['bottleneckSummary'],
    queryFn: bottlenecksApi.getSummary,
  });

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <AlertTriangle className="w-8 h-8 text-orange-500" />
          <h1 className="text-3xl font-bold text-white">Bottleneck Nodes</h1>
        </div>
        <p className="text-slate-400">
          Critical nodes that connect different parts of the network. Removing these would significantly
          fragment the graph.
        </p>
      </div>

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
            <p className="text-slate-400 text-sm">Total Analyzed</p>
            <p className="text-2xl font-bold text-white">{summary.total_analyzed}</p>
          </div>
          <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
            <p className="text-slate-400 text-sm">Bottlenecks Found</p>
            <p className="text-2xl font-bold text-orange-500">{summary.bottleneck_count}</p>
          </div>
          <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
            <p className="text-slate-400 text-sm">Average Score</p>
            <p className="text-2xl font-bold text-white">
              {summary.avg_bottleneck_score
                ? (summary.avg_bottleneck_score * 100).toFixed(1) + '%'
                : 'N/A'}
            </p>
          </div>
          <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
            <p className="text-slate-400 text-sm">Max Score</p>
            <p className="text-2xl font-bold text-red-500">
              {summary.max_bottleneck_score
                ? (summary.max_bottleneck_score * 100).toFixed(1) + '%'
                : 'N/A'}
            </p>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-slate-800 rounded-xl border border-slate-700 p-4 mb-6">
        <div className="flex items-center gap-2 mb-4">
          <Filter className="w-4 h-4 text-slate-400" />
          <span className="text-sm font-medium text-slate-400">Filters</span>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Min Score Filter */}
          <div>
            <label className="block text-sm text-slate-400 mb-2">
              Minimum Score: {(minScore * 100).toFixed(0)}%
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={minScore}
              onChange={(e) => setMinScore(parseFloat(e.target.value))}
              className="w-full accent-blue-500"
            />
          </div>

          {/* Community Filter */}
          <div>
            <label className="block text-sm text-slate-400 mb-2">Community</label>
            <select
              value={selectedCommunity || ''}
              onChange={(e) => setSelectedCommunity(e.target.value || null)}
              className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
            >
              <option value="">All Communities</option>
              {communitiesData?.communities.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name || c.id} ({c.member_count} members)
                </option>
              ))}
            </select>
          </div>

          {/* Limit */}
          <div>
            <label className="block text-sm text-slate-400 mb-2">Show</label>
            <select
              value={limit}
              onChange={(e) => setLimit(parseInt(e.target.value))}
              className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
            >
              <option value="10">10 results</option>
              <option value="20">20 results</option>
              <option value="50">50 results</option>
              <option value="100">100 results</option>
            </select>
          </div>
        </div>
      </div>

      {/* Results */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
        </div>
      ) : error ? (
        <div className="text-center py-12">
          <p className="text-red-400">Failed to load bottlenecks</p>
        </div>
      ) : data?.bottlenecks?.length ? (
        <div>
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm text-slate-400">
              Showing {data.bottlenecks.length} of {data.total} bottlenecks
            </p>
            <button className="flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors">
              <ArrowUpDown className="w-4 h-4" />
              Sort by score
            </button>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {data.bottlenecks.map((bottleneck, index) => (
              <BottleneckCard
                key={bottleneck.user.id}
                bottleneck={bottleneck}
                rank={index + 1}
              />
            ))}
          </div>
        </div>
      ) : (
        <div className="text-center py-12">
          <AlertTriangle className="w-12 h-12 text-slate-600 mx-auto mb-4" />
          <p className="text-slate-400 mb-2">No bottlenecks found</p>
          <p className="text-slate-500 text-sm">
            {minScore > 0
              ? 'Try lowering the minimum score filter'
              : 'Run the bottleneck algorithm from the dashboard'}
          </p>
        </div>
      )}
    </div>
  );
}
