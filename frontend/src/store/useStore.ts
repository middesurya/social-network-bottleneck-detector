import { create } from 'zustand';
import type { User, SubgraphResponse, GraphStats, Community } from '../types';

interface AppState {
  // Selected entities
  selectedNode: User | null;
  selectedCommunity: Community | null;
  
  // Graph state
  graphData: SubgraphResponse | null;
  graphStats: GraphStats | null;
  
  // UI state
  sidebarOpen: boolean;
  detailsPanelOpen: boolean;
  currentLayout: 'cose' | 'circle' | 'grid' | 'breadthfirst' | 'concentric';
  
  // Filters
  filters: {
    minBottleneckScore: number;
    communityId: string | null;
    showBottlenecksOnly: boolean;
  };
  
  // Actions
  setSelectedNode: (node: User | null) => void;
  setSelectedCommunity: (community: Community | null) => void;
  setGraphData: (data: SubgraphResponse | null) => void;
  setGraphStats: (stats: GraphStats | null) => void;
  toggleSidebar: () => void;
  toggleDetailsPanel: () => void;
  setCurrentLayout: (layout: AppState['currentLayout']) => void;
  setFilters: (filters: Partial<AppState['filters']>) => void;
  resetFilters: () => void;
}

const initialFilters = {
  minBottleneckScore: 0,
  communityId: null,
  showBottlenecksOnly: false,
};

export const useStore = create<AppState>((set) => ({
  // Initial state
  selectedNode: null,
  selectedCommunity: null,
  graphData: null,
  graphStats: null,
  sidebarOpen: true,
  detailsPanelOpen: false,
  currentLayout: 'cose',
  filters: initialFilters,
  
  // Actions
  setSelectedNode: (node) => set({ selectedNode: node, detailsPanelOpen: node !== null }),
  setSelectedCommunity: (community) => set({ selectedCommunity: community }),
  setGraphData: (data) => set({ graphData: data }),
  setGraphStats: (stats) => set({ graphStats: stats }),
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  toggleDetailsPanel: () => set((state) => ({ detailsPanelOpen: !state.detailsPanelOpen })),
  setCurrentLayout: (layout) => set({ currentLayout: layout }),
  setFilters: (filters) => set((state) => ({ filters: { ...state.filters, ...filters } })),
  resetFilters: () => set({ filters: initialFilters }),
}));
