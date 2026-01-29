import axios from 'axios';
import type {
  User,
  SubgraphResponse,
  GraphStats,
  Bottleneck,
  BottleneckSummary,
  Community,
  AlgorithmResult,
  NLQResponse,
} from '../types';

const API_BASE = '/api/v1';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Users API
export const usersApi = {
  getUsers: async (params?: { skip?: number; limit?: number; order_by?: string }) => {
    const response = await api.get<{ users: User[]; total: number }>('/users', { params });
    return response.data;
  },

  getUser: async (userId: string) => {
    const response = await api.get<User>(`/users/${userId}`);
    return response.data;
  },

  getUserConnections: async (userId: string) => {
    const response = await api.get(`/users/${userId}/connections`);
    return response.data;
  },

  getEgoNetwork: async (userId: string, depth: number = 1) => {
    const response = await api.get(`/users/${userId}/ego-network`, { params: { depth } });
    return response.data;
  },
};

// Graph API
export const graphApi = {
  getStats: async (): Promise<GraphStats> => {
    const response = await api.get<GraphStats>('/graph/stats');
    return response.data;
  },

  getSubgraph: async (params?: {
    center_id?: string;
    community_id?: string;
    limit?: number;
    include_bottlenecks?: boolean;
    min_degree?: number;
  }): Promise<SubgraphResponse> => {
    const response = await api.get<SubgraphResponse>('/graph/subgraph', { params });
    return response.data;
  },

  getCommunitiesOverview: async () => {
    const response = await api.get('/graph/communities-overview');
    return response.data;
  },
};

// Algorithms API
export const algorithmsApi = {
  listAlgorithms: async () => {
    const response = await api.get('/algorithms');
    return response.data;
  },

  runAlgorithm: async (
    algorithmName: string,
    params?: { write_property?: boolean; sample_size?: number }
  ): Promise<AlgorithmResult> => {
    const response = await api.post<AlgorithmResult>(`/algorithms/run/${algorithmName}`, null, {
      params,
    });
    return response.data;
  },
};

// Bottlenecks API
export const bottlenecksApi = {
  getBottlenecks: async (params?: {
    limit?: number;
    min_score?: number;
    community_id?: string;
  }): Promise<{ bottlenecks: Bottleneck[]; total: number }> => {
    const response = await api.get('/bottlenecks', { params });
    return response.data;
  },

  getSummary: async (): Promise<BottleneckSummary> => {
    const response = await api.get<BottleneckSummary>('/bottlenecks/summary');
    return response.data;
  },

  getBridges: async (limit: number = 20) => {
    const response = await api.get('/bottlenecks/bridges', { params: { limit } });
    return response.data;
  },

  getImpact: async (userId: string) => {
    const response = await api.get(`/bottlenecks/${userId}/impact`);
    return response.data;
  },
};

// Communities API
export const communitiesApi = {
  getCommunities: async (params?: { limit?: number; min_size?: number }): Promise<{
    communities: Community[];
    total: number;
  }> => {
    const response = await api.get('/communities', { params });
    return response.data;
  },

  getCommunity: async (communityId: string): Promise<Community> => {
    const response = await api.get<Community>(`/communities/${communityId}`);
    return response.data;
  },

  getCommunityBottlenecks: async (communityId: string, limit: number = 10) => {
    const response = await api.get(`/communities/${communityId}/bottlenecks`, {
      params: { limit },
    });
    return response.data;
  },

  getConnectionMatrix: async () => {
    const response = await api.get('/communities/connections/matrix');
    return response.data;
  },
};

// Natural Language Query API
export const nlqApi = {
  query: async (queryText: string, maxResults: number = 10): Promise<NLQResponse> => {
    const response = await api.post<NLQResponse>('/nlq/query', {
      query: queryText,
      max_results: maxResults,
    });
    return response.data;
  },

  getExamples: async () => {
    const response = await api.get('/nlq/examples');
    return response.data;
  },
};

export default api;
