import { X, Users, UserPlus, Activity, Layers } from 'lucide-react';
import { useStore } from '../store/useStore';

const getScoreColor = (score: number | undefined): string => {
  if (!score) return 'text-slate-400';
  if (score >= 0.7) return 'text-red-500';
  if (score >= 0.5) return 'text-orange-500';
  if (score >= 0.3) return 'text-yellow-500';
  return 'text-green-500';
};

const getScoreLabel = (score: number | undefined): string => {
  if (!score) return 'N/A';
  if (score >= 0.7) return 'Critical';
  if (score >= 0.5) return 'High';
  if (score >= 0.3) return 'Medium';
  return 'Low';
};

export function NodeDetails() {
  const { selectedNode, setSelectedNode, detailsPanelOpen } = useStore();

  if (!detailsPanelOpen || !selectedNode) return null;

  return (
    <div className="absolute top-4 left-4 w-80 bg-slate-800 rounded-lg border border-slate-700 shadow-xl overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-slate-700">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center text-white font-bold">
            {selectedNode.username?.[0]?.toUpperCase() || '?'}
          </div>
          <div>
            <h3 className="font-semibold text-white">
              {selectedNode.display_name || selectedNode.username}
            </h3>
            <p className="text-sm text-slate-400">@{selectedNode.username}</p>
          </div>
        </div>
        <button
          onClick={() => setSelectedNode(null)}
          className="p-1.5 rounded hover:bg-slate-700 transition-colors"
        >
          <X className="w-4 h-4 text-slate-400" />
        </button>
      </div>

      {/* Stats */}
      <div className="p-4 space-y-4">
        {/* Connection Stats */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-slate-700/50 rounded-lg p-3">
            <div className="flex items-center gap-2 text-slate-400 mb-1">
              <Users className="w-4 h-4" />
              <span className="text-xs">Followers</span>
            </div>
            <p className="text-lg font-semibold text-white">
              {selectedNode.follower_count?.toLocaleString() || 0}
            </p>
          </div>
          <div className="bg-slate-700/50 rounded-lg p-3">
            <div className="flex items-center gap-2 text-slate-400 mb-1">
              <UserPlus className="w-4 h-4" />
              <span className="text-xs">Following</span>
            </div>
            <p className="text-lg font-semibold text-white">
              {selectedNode.following_count?.toLocaleString() || 0}
            </p>
          </div>
        </div>

        {/* Bottleneck Score */}
        {selectedNode.bottleneck_score !== undefined && (
          <div className="bg-slate-700/50 rounded-lg p-3">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2 text-slate-400">
                <Activity className="w-4 h-4" />
                <span className="text-xs">Bottleneck Score</span>
              </div>
              <span
                className={`text-xs font-medium px-2 py-0.5 rounded ${getScoreColor(
                  selectedNode.bottleneck_score
                )} bg-slate-600`}
              >
                {getScoreLabel(selectedNode.bottleneck_score)}
              </span>
            </div>
            <div className="flex items-end gap-2">
              <p className={`text-2xl font-bold ${getScoreColor(selectedNode.bottleneck_score)}`}>
                {(selectedNode.bottleneck_score * 100).toFixed(1)}%
              </p>
            </div>
            {/* Score bar */}
            <div className="mt-2 h-2 bg-slate-600 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all ${
                  selectedNode.bottleneck_score >= 0.7
                    ? 'bg-red-500'
                    : selectedNode.bottleneck_score >= 0.5
                    ? 'bg-orange-500'
                    : selectedNode.bottleneck_score >= 0.3
                    ? 'bg-yellow-500'
                    : 'bg-green-500'
                }`}
                style={{ width: `${selectedNode.bottleneck_score * 100}%` }}
              />
            </div>
          </div>
        )}

        {/* Other Metrics */}
        <div className="space-y-2">
          {selectedNode.pagerank !== undefined && (
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-400">PageRank</span>
              <span className="text-white font-mono">
                {selectedNode.pagerank.toFixed(6)}
              </span>
            </div>
          )}
          {selectedNode.betweenness_centrality !== undefined && (
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-400">Betweenness</span>
              <span className="text-white font-mono">
                {selectedNode.betweenness_centrality.toFixed(6)}
              </span>
            </div>
          )}
          {selectedNode.bridge_score !== undefined && (
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-400">Bridge Score</span>
              <span className="text-white font-mono">
                {selectedNode.bridge_score.toFixed(4)}
              </span>
            </div>
          )}
        </div>

        {/* Community */}
        {selectedNode.community_id && (
          <div className="flex items-center gap-2 pt-2 border-t border-slate-700">
            <Layers className="w-4 h-4 text-slate-400" />
            <span className="text-sm text-slate-400">Community:</span>
            <span className="text-sm text-white font-mono">{selectedNode.community_id}</span>
          </div>
        )}
      </div>
    </div>
  );
}
