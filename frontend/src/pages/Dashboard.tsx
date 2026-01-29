import { useQuery } from '@tanstack/react-query';
import { Users, Network, AlertTriangle, Layers, Play, Loader2 } from 'lucide-react';
import { MetricCard } from '../components/MetricCard';
import { BottleneckCard } from '../components/BottleneckCard';
import { graphApi, bottlenecksApi, algorithmsApi } from '../services/api';
import { useState } from 'react';

export function Dashboard() {
  const [runningAlgorithm, setRunningAlgorithm] = useState<string | null>(null);

  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['graphStats'],
    queryFn: graphApi.getStats,
  });

  const { data: bottlenecksData, isLoading: bottlenecksLoading } = useQuery({
    queryKey: ['topBottlenecks'],
    queryFn: () => bottlenecksApi.getBottlenecks({ limit: 5 }),
  });

  const { data: summary } = useQuery({
    queryKey: ['bottleneckSummary'],
    queryFn: bottlenecksApi.getSummary,
  });

  const runAlgorithm = async (name: string) => {
    setRunningAlgorithm(name);
    try {
      await algorithmsApi.runAlgorithm(name);
      // Refetch data after algorithm runs
      window.location.reload();
    } catch (error) {
      console.error('Algorithm failed:', error);
    } finally {
      setRunningAlgorithm(null);
    }
  };

  const algorithms = [
    { name: 'pagerank', label: 'PageRank' },
    { name: 'betweenness', label: 'Betweenness' },
    { name: 'louvain', label: 'Community Detection' },
    { name: 'bottleneck', label: 'Bottleneck Score' },
  ];

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Dashboard</h1>
        <p className="text-slate-400">
          Monitor network health and identify critical bottleneck nodes
        </p>
      </div>

      {/* Quick Actions */}
      <div className="mb-8 p-4 bg-slate-800 rounded-xl border border-slate-700">
        <h3 className="text-sm font-medium text-slate-400 mb-3">Run Algorithms</h3>
        <div className="flex flex-wrap gap-2">
          {algorithms.map((algo) => (
            <button
              key={algo.name}
              onClick={() => runAlgorithm(algo.name)}
              disabled={runningAlgorithm !== null}
              className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-sm text-white flex items-center gap-2 transition-colors disabled:opacity-50"
            >
              {runningAlgorithm === algo.name ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Play className="w-4 h-4" />
              )}
              {algo.label}
            </button>
          ))}
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <MetricCard
          title="Total Users"
          value={statsLoading ? '...' : stats?.user_count || 0}
          subtitle="In the network"
          icon={<Users className="w-5 h-5" />}
          color="blue"
        />
        <MetricCard
          title="Connections"
          value={statsLoading ? '...' : stats?.follows_count || 0}
          subtitle="Total relationships"
          icon={<Network className="w-5 h-5" />}
          color="green"
        />
        <MetricCard
          title="Bottlenecks"
          value={summary?.bottleneck_count || 0}
          subtitle="Critical nodes identified"
          icon={<AlertTriangle className="w-5 h-5" />}
          color="red"
        />
        <MetricCard
          title="Communities"
          value={stats?.community_count || 0}
          subtitle="Detected clusters"
          icon={<Layers className="w-5 h-5" />}
          color="purple"
        />
      </div>

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Bottlenecks */}
        <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-white">Top Bottlenecks</h2>
            <a
              href="/bottlenecks"
              className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
            >
              View all →
            </a>
          </div>
          
          {bottlenecksLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-6 h-6 text-slate-400 animate-spin" />
            </div>
          ) : bottlenecksData?.bottlenecks?.length ? (
            <div className="space-y-3">
              {bottlenecksData.bottlenecks.map((bottleneck, index) => (
                <BottleneckCard
                  key={bottleneck.user.id}
                  bottleneck={bottleneck}
                  rank={index + 1}
                />
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-slate-400">
              <AlertTriangle className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p>No bottlenecks detected yet</p>
              <p className="text-sm mt-1">Run the algorithms to analyze the network</p>
            </div>
          )}
        </div>

        {/* Summary Stats */}
        <div className="space-y-6">
          {/* Bottleneck Distribution */}
          <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-5">
            <h2 className="text-lg font-semibold text-white mb-4">Bottleneck Analysis</h2>
            
            {summary ? (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-slate-700/50 rounded-lg p-4">
                    <p className="text-slate-400 text-sm mb-1">Average Score</p>
                    <p className="text-2xl font-bold text-white">
                      {summary.avg_bottleneck_score
                        ? (summary.avg_bottleneck_score * 100).toFixed(1) + '%'
                        : 'N/A'}
                    </p>
                  </div>
                  <div className="bg-slate-700/50 rounded-lg p-4">
                    <p className="text-slate-400 text-sm mb-1">Max Score</p>
                    <p className="text-2xl font-bold text-red-400">
                      {summary.max_bottleneck_score
                        ? (summary.max_bottleneck_score * 100).toFixed(1) + '%'
                        : 'N/A'}
                    </p>
                  </div>
                </div>
                
                <div className="bg-slate-700/50 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-slate-400 text-sm">Nodes Analyzed</p>
                    <p className="text-white font-semibold">{summary.total_analyzed}</p>
                  </div>
                  <div className="h-2 bg-slate-600 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-blue-500 rounded-full"
                      style={{
                        width: `${
                          summary.total_analyzed > 0
                            ? (summary.bottleneck_count / summary.total_analyzed) * 100
                            : 0
                        }%`,
                      }}
                    />
                  </div>
                  <p className="text-xs text-slate-500 mt-2">
                    {summary.bottleneck_count} identified as bottlenecks (
                    {summary.total_analyzed > 0
                      ? ((summary.bottleneck_count / summary.total_analyzed) * 100).toFixed(1)
                      : 0}
                    %)
                  </p>
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-slate-400">
                <p>Run the bottleneck algorithm to see analysis</p>
              </div>
            )}
          </div>

          {/* Quick Tips */}
          <div className="bg-gradient-to-br from-blue-900/30 to-purple-900/30 rounded-xl border border-blue-500/20 p-5">
            <h2 className="text-lg font-semibold text-white mb-3">💡 Quick Tips</h2>
            <ul className="space-y-2 text-sm text-slate-300">
              <li className="flex items-start gap-2">
                <span className="text-blue-400">1.</span>
                <span>Run PageRank and Betweenness first to calculate centrality metrics</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-400">2.</span>
                <span>Run Community Detection to identify clusters</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-400">3.</span>
                <span>Finally run Bottleneck Score to identify critical nodes</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-400">4.</span>
                <span>Use the Explorer to visualize the network structure</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
