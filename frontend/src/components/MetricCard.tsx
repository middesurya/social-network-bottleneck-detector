import type { ReactNode } from 'react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: ReactNode;
  trend?: {
    value: number;
    label: string;
  };
  color?: 'blue' | 'green' | 'orange' | 'red' | 'purple';
}

const colorClasses = {
  blue: 'bg-blue-500/10 text-blue-500 border-blue-500/20',
  green: 'bg-green-500/10 text-green-500 border-green-500/20',
  orange: 'bg-orange-500/10 text-orange-500 border-orange-500/20',
  red: 'bg-red-500/10 text-red-500 border-red-500/20',
  purple: 'bg-purple-500/10 text-purple-500 border-purple-500/20',
};

const iconColorClasses = {
  blue: 'text-blue-500',
  green: 'text-green-500',
  orange: 'text-orange-500',
  red: 'text-red-500',
  purple: 'text-purple-500',
};

export function MetricCard({
  title,
  value,
  subtitle,
  icon,
  trend,
  color = 'blue',
}: MetricCardProps) {
  return (
    <div className="bg-slate-800 rounded-xl p-5 border border-slate-700 hover:border-slate-600 transition-colors">
      <div className="flex items-start justify-between mb-3">
        <span className="text-slate-400 text-sm font-medium">{title}</span>
        {icon && (
          <div className={`p-2 rounded-lg ${colorClasses[color]}`}>
            <span className={iconColorClasses[color]}>{icon}</span>
          </div>
        )}
      </div>
      
      <div className="flex items-end gap-2">
        <p className="text-3xl font-bold text-white">
          {typeof value === 'number' ? value.toLocaleString() : value}
        </p>
        {trend && (
          <span
            className={`text-sm font-medium mb-1 ${
              trend.value >= 0 ? 'text-green-500' : 'text-red-500'
            }`}
          >
            {trend.value >= 0 ? '+' : ''}
            {trend.value}% {trend.label}
          </span>
        )}
      </div>
      
      {subtitle && <p className="text-slate-500 text-sm mt-1">{subtitle}</p>}
    </div>
  );
}
