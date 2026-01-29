import { useQuery } from '@tanstack/react-query';
import { Loader2 } from 'lucide-react';
import { NetworkGraph } from '../components/NetworkGraph';
import { GraphControls } from '../components/GraphControls';
import { NodeDetails } from '../components/NodeDetails';
import { graphApi } from '../services/api';
import { useStore } from '../store/useStore';

export function Explorer() {
  const { filters } = useStore();

  const { data, isLoading, error } = useQuery({
    queryKey: ['subgraph', filters],
    queryFn: () =>
      graphApi.getSubgraph({
        limit: 100,
        include_bottlenecks: true,
        community_id: filters.communityId || undefined,
        min_degree: filters.showBottlenecksOnly ? 1 : 0,
      }),
  });

  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 text-blue-500 animate-spin mx-auto mb-4" />
          <p className="text-slate-400">Loading graph data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-400 mb-2">Failed to load graph</p>
          <p className="text-slate-500 text-sm">
            Make sure the backend is running and Neo4j is connected
          </p>
        </div>
      </div>
    );
  }

  if (!data || data.nodes.length === 0) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <p className="text-slate-400 mb-2">No data to display</p>
          <p className="text-slate-500 text-sm">
            Import some data and run the algorithms first
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full relative">
      {/* Graph */}
      <NetworkGraph data={data} />
      
      {/* Controls */}
      <GraphControls />
      
      {/* Node Details Panel */}
      <NodeDetails />
      
      {/* Stats Overlay */}
      <div className="absolute bottom-4 left-4 bg-slate-800/90 backdrop-blur-sm rounded-lg px-4 py-2 border border-slate-700">
        <div className="flex items-center gap-4 text-sm">
          <div>
            <span className="text-slate-400">Nodes: </span>
            <span className="text-white font-medium">{data.metadata.node_count}</span>
          </div>
          <div className="w-px h-4 bg-slate-700" />
          <div>
            <span className="text-slate-400">Edges: </span>
            <span className="text-white font-medium">{data.metadata.edge_count}</span>
          </div>
        </div>
      </div>
      
      {/* Legend */}
      <div className="absolute bottom-4 right-4 bg-slate-800/90 backdrop-blur-sm rounded-lg p-3 border border-slate-700">
        <p className="text-xs text-slate-400 mb-2">Bottleneck Score</p>
        <div className="flex items-center gap-3 text-xs">
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-full bg-green-500" />
            <span className="text-slate-300">Low</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-full bg-yellow-500" />
            <span className="text-slate-300">Med</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-full bg-orange-500" />
            <span className="text-slate-300">High</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-full bg-red-500" />
            <span className="text-slate-300">Critical</span>
          </div>
        </div>
      </div>
    </div>
  );
}
