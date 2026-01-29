import { AlertTriangle, Users, Layers } from 'lucide-react';
import type { Bottleneck } from '../types';

interface BottleneckCardProps {
  bottleneck: Bottleneck;
  onClick?: () => void;
  rank?: number;
}

const getScoreBadgeColor = (score: number): string => {
  if (score >= 0.7) return 'bg-red-500/20 text-red-400 border-red-500/30';
  if (score >= 0.5) return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
  if (score >= 0.3) return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
  return 'bg-green-500/20 text-green-400 border-green-500/30';
};

const getScoreLabel = (score: number): string => {
  if (score >= 0.7) return 'Critical';
  if (score >= 0.5) return 'High';
  if (score >= 0.3) return 'Medium';
  return 'Low';
};

export function BottleneckCard({ bottleneck, onClick, rank }: BottleneckCardProps) {
  const { user, bottleneck_score, connected_communities, influence_radius } = bottleneck;

  return (
    <div
      onClick={onClick}
      className="bg-slate-800 rounded-lg border border-slate-700 p-4 hover:border-slate-600 transition-all cursor-pointer group"
    >
      <div className="flex items-start gap-3">
        {/* Rank or Avatar */}
        <div className="flex-shrink-0">
          {rank !== undefined ? (
            <div className="w-10 h-10 rounded-full bg-slate-700 flex items-center justify-center text-slate-300 font-bold">
              #{rank}
            </div>
          ) : (
            <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center text-white font-bold">
              {user.username?.[0]?.toUpperCase() || '?'}
            </div>
          )}
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h4 className="font-semibold text-white truncate group-hover:text-blue-400 transition-colors">
              {user.display_name || user.username}
            </h4>
            <span
              className={`text-xs px-2 py-0.5 rounded-full border ${getScoreBadgeColor(
                bottleneck_score
              )}`}
            >
              {getScoreLabel(bottleneck_score)}
            </span>
          </div>
          <p className="text-sm text-slate-400 truncate">@{user.username}</p>

          {/* Metrics */}
          <div className="flex items-center gap-4 mt-3 text-xs text-slate-400">
            <div className="flex items-center gap-1">
              <AlertTriangle className="w-3.5 h-3.5" />
              <span>{(bottleneck_score * 100).toFixed(1)}%</span>
            </div>
            <div className="flex items-center gap-1">
              <Layers className="w-3.5 h-3.5" />
              <span>{connected_communities.length} communities</span>
            </div>
            <div className="flex items-center gap-1">
              <Users className="w-3.5 h-3.5" />
              <span>{influence_radius} reach</span>
            </div>
          </div>
        </div>

        {/* Score visualization */}
        <div className="flex-shrink-0 w-16 h-16">
          <svg viewBox="0 0 36 36" className="w-full h-full">
            <path
              d="M18 2.0845
                a 15.9155 15.9155 0 0 1 0 31.831
                a 15.9155 15.9155 0 0 1 0 -31.831"
              fill="none"
              stroke="#334155"
              strokeWidth="3"
            />
            <path
              d="M18 2.0845
                a 15.9155 15.9155 0 0 1 0 31.831
                a 15.9155 15.9155 0 0 1 0 -31.831"
              fill="none"
              stroke={
                bottleneck_score >= 0.7
                  ? '#ef4444'
                  : bottleneck_score >= 0.5
                  ? '#f97316'
                  : bottleneck_score >= 0.3
                  ? '#eab308'
                  : '#22c55e'
              }
              strokeWidth="3"
              strokeDasharray={`${bottleneck_score * 100}, 100`}
              strokeLinecap="round"
              className="transition-all duration-500"
            />
            <text
              x="18"
              y="20.5"
              textAnchor="middle"
              className="fill-white text-[8px] font-bold"
            >
              {(bottleneck_score * 100).toFixed(0)}
            </text>
          </svg>
        </div>
      </div>
    </div>
  );
}
