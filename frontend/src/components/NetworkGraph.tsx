import { useEffect, useRef, useCallback } from 'react';
import CytoscapeComponent from 'react-cytoscapejs';
import type { Core, ElementDefinition, Stylesheet } from 'cytoscape';
import { useStore } from '../store/useStore';
import type { SubgraphResponse } from '../types';

interface NetworkGraphProps {
  data: SubgraphResponse;
  onNodeSelect?: (nodeData: Record<string, unknown>) => void;
}

// Color palette for communities
const COMMUNITY_COLORS = [
  '#3b82f6', // blue
  '#22c55e', // green
  '#f59e0b', // amber
  '#ef4444', // red
  '#8b5cf6', // violet
  '#ec4899', // pink
  '#06b6d4', // cyan
  '#84cc16', // lime
];

const getCommunityColor = (communityId: string | undefined): string => {
  if (!communityId) return '#64748b';
  const index = Math.abs(communityId.split('').reduce((acc, c) => acc + c.charCodeAt(0), 0));
  return COMMUNITY_COLORS[index % COMMUNITY_COLORS.length];
};

const getBottleneckColor = (score: number | undefined): string => {
  if (!score) return '#64748b';
  if (score >= 0.7) return '#ef4444'; // critical
  if (score >= 0.5) return '#f97316'; // high
  if (score >= 0.3) return '#eab308'; // medium
  return '#22c55e'; // low
};

const stylesheet: Stylesheet[] = [
  {
    selector: 'node',
    style: {
      'background-color': '#64748b',
      'label': 'data(label)',
      'color': '#fff',
      'text-valign': 'bottom',
      'text-halign': 'center',
      'font-size': '10px',
      'text-margin-y': 5,
      'width': 30,
      'height': 30,
      'border-width': 2,
      'border-color': '#475569',
    },
  },
  {
    selector: 'node[bottleneck_score]',
    style: {
      'width': 'mapData(bottleneck_score, 0, 1, 30, 60)',
      'height': 'mapData(bottleneck_score, 0, 1, 30, 60)',
    },
  },
  {
    selector: 'node.bottleneck',
    style: {
      'border-width': 4,
      'border-color': '#ef4444',
    },
  },
  {
    selector: 'node:selected',
    style: {
      'border-width': 4,
      'border-color': '#3b82f6',
      'background-color': '#60a5fa',
    },
  },
  {
    selector: 'edge',
    style: {
      'width': 1,
      'line-color': '#475569',
      'curve-style': 'bezier',
      'target-arrow-shape': 'triangle',
      'target-arrow-color': '#475569',
      'arrow-scale': 0.8,
      'opacity': 0.6,
    },
  },
  {
    selector: 'edge:selected',
    style: {
      'line-color': '#3b82f6',
      'target-arrow-color': '#3b82f6',
      'opacity': 1,
    },
  },
];

export function NetworkGraph({ data, onNodeSelect }: NetworkGraphProps) {
  const cyRef = useRef<Core | null>(null);
  const { currentLayout, setSelectedNode } = useStore();

  // Convert data to Cytoscape elements
  const elements: ElementDefinition[] = [
    ...data.nodes.map((node) => ({
      data: {
        ...node.data,
        backgroundColor: node.data.is_bottleneck
          ? getBottleneckColor(node.data.bottleneck_score as number)
          : getCommunityColor(node.data.community_id as string),
      },
      classes: node.classes,
    })),
    ...data.edges.map((edge) => ({
      data: edge.data,
      classes: edge.classes,
    })),
  ];

  // Apply dynamic styles based on data
  const dynamicStylesheet: Stylesheet[] = [
    ...stylesheet,
    {
      selector: 'node',
      style: {
        'background-color': 'data(backgroundColor)',
      },
    },
  ];

  const handleNodeTap = useCallback(
    (event: { target: { data: () => Record<string, unknown> } }) => {
      const nodeData = event.target.data();
      setSelectedNode(nodeData as unknown as import('../types').User);
      onNodeSelect?.(nodeData);
    },
    [onNodeSelect, setSelectedNode]
  );

  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;

    // Add event listeners
    cy.on('tap', 'node', handleNodeTap);

    // Run layout
    cy.layout({
      name: currentLayout,
      animate: true,
      animationDuration: 500,
      fit: true,
      padding: 50,
    }).run();

    return () => {
      cy.removeListener('tap', 'node', handleNodeTap);
    };
  }, [currentLayout, handleNodeTap]);

  return (
    <CytoscapeComponent
      elements={elements}
      stylesheet={dynamicStylesheet}
      cy={(cy) => {
        cyRef.current = cy;
      }}
      className="cytoscape-container"
      layout={{ name: currentLayout }}
      wheelSensitivity={0.3}
      minZoom={0.1}
      maxZoom={3}
    />
  );
}
