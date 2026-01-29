// User types
export interface User {
  id: string;
  username: string;
  display_name?: string;
  bio?: string;
  follower_count: number;
  following_count: number;
  tweet_count?: number;
  verified?: boolean;
  betweenness_centrality?: number;
  pagerank?: number;
  bottleneck_score?: number;
  bridge_score?: number;
  community_id?: string;
  is_bottleneck?: boolean;
}

// Graph types
export interface CytoscapeNode {
  data: {
    id: string;
    label: string;
    [key: string]: unknown;
  };
  position?: { x: number; y: number };
  classes?: string;
}

export interface CytoscapeEdge {
  data: {
    id: string;
    source: string;
    target: string;
    type?: string;
    [key: string]: unknown;
  };
  classes?: string;
}

export interface SubgraphResponse {
  nodes: CytoscapeNode[];
  edges: CytoscapeEdge[];
  metadata: {
    node_count: number;
    edge_count: number;
    filters: Record<string, unknown>;
  };
}

export interface GraphStats {
  user_count: number;
  follows_count: number;
  community_count: number;
  tweet_count: number;
  avg_followers?: number;
  avg_following?: number;
  density?: number;
}

// Bottleneck types
export interface Bottleneck {
  user: User;
  bottleneck_score: number;
  betweenness_centrality: number;
  bridge_score: number;
  connected_communities: string[];
  influence_radius: number;
}

export interface BottleneckSummary {
  total_analyzed: number;
  bottleneck_count: number;
  avg_bottleneck_score: number;
  max_bottleneck_score: number;
  min_bottleneck_score: number;
  score_std_dev?: number;
}

// Community types
export interface Community {
  id: string;
  name?: string;
  member_count: number;
  internal_edges?: number;
  external_edges?: number;
  internal_density?: number;
  top_members?: User[];
}

// Algorithm types
export interface AlgorithmResult {
  algorithm: string;
  status: 'completed' | 'failed' | 'running';
  execution_time_ms: number;
  nodes_processed: number;
  results_summary: Record<string, unknown>;
  message?: string;
}

// NLQ types
export interface NLQResponse {
  query: string;
  generated_cypher: string;
  results: Record<string, unknown>[];
  explanation?: string;
  confidence?: number;
}

// API Response types
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}
