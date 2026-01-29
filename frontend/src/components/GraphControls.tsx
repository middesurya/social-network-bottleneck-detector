import { ZoomIn, ZoomOut, Maximize, RotateCcw, Grid3X3 } from 'lucide-react';
import { useStore } from '../store/useStore';

const layouts = [
  { id: 'cose', label: 'Force-Directed' },
  { id: 'circle', label: 'Circle' },
  { id: 'grid', label: 'Grid' },
  { id: 'breadthfirst', label: 'Hierarchical' },
  { id: 'concentric', label: 'Concentric' },
] as const;

interface GraphControlsProps {
  onZoomIn?: () => void;
  onZoomOut?: () => void;
  onFit?: () => void;
  onReset?: () => void;
}

export function GraphControls({ onZoomIn, onZoomOut, onFit, onReset }: GraphControlsProps) {
  const { currentLayout, setCurrentLayout } = useStore();

  return (
    <div className="absolute top-4 right-4 flex flex-col gap-2">
      {/* Zoom Controls */}
      <div className="bg-slate-800 rounded-lg p-1 flex flex-col gap-1 border border-slate-700">
        <button
          onClick={onZoomIn}
          className="p-2 rounded hover:bg-slate-700 transition-colors"
          title="Zoom In"
        >
          <ZoomIn className="w-4 h-4 text-slate-300" />
        </button>
        <button
          onClick={onZoomOut}
          className="p-2 rounded hover:bg-slate-700 transition-colors"
          title="Zoom Out"
        >
          <ZoomOut className="w-4 h-4 text-slate-300" />
        </button>
        <button
          onClick={onFit}
          className="p-2 rounded hover:bg-slate-700 transition-colors"
          title="Fit to Screen"
        >
          <Maximize className="w-4 h-4 text-slate-300" />
        </button>
        <button
          onClick={onReset}
          className="p-2 rounded hover:bg-slate-700 transition-colors"
          title="Reset View"
        >
          <RotateCcw className="w-4 h-4 text-slate-300" />
        </button>
      </div>

      {/* Layout Selector */}
      <div className="bg-slate-800 rounded-lg p-2 border border-slate-700">
        <div className="flex items-center gap-2 mb-2 px-1">
          <Grid3X3 className="w-4 h-4 text-slate-400" />
          <span className="text-xs text-slate-400">Layout</span>
        </div>
        <div className="flex flex-col gap-1">
          {layouts.map((layout) => (
            <button
              key={layout.id}
              onClick={() => setCurrentLayout(layout.id)}
              className={`px-2 py-1.5 text-xs rounded transition-colors text-left ${
                currentLayout === layout.id
                  ? 'bg-blue-600 text-white'
                  : 'text-slate-300 hover:bg-slate-700'
              }`}
            >
              {layout.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
