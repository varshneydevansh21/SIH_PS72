import React, { useMemo } from 'react';
import { Cloud, Zap, AlertTriangle, MapPin, Settings2, Plus, Minus, Layers } from 'lucide-react';
import { NowcastMap } from './NowcastMap';
import { useNowcastStore } from '../../store/useNowcastStore';
import { RISK_LEVEL_CONFIG, type RiskLevel } from '../../types/nowcast';

function formatRelativeTime(iso: string): string {
  const diff = new Date(iso).getTime() - Date.now();
  if (diff <= 0) return 'Expired';
  const minutes = Math.floor(diff / 60_000);
  if (minutes < 60) return `${minutes}m remaining`;
  const hours = Math.floor(minutes / 60);
  return `${hours}h ${minutes % 60}m remaining`;
}



const MAP_LAYERS = [
  { id: 'thunderstorm', label: 'Thunderstorm Probability' },
  { id: 'lightning', label: 'Lightning Probability' },
  { id: 'composite', label: 'Composite View' },
  { id: 'observations', label: 'Observations' },
] as const;

export function DashboardView() {
  const { alerts, cells, lightningStrokes, selectedLayer, setSelectedLayer, fetchActiveAlerts, fetchLatestNowcast, fetchRadarAndLightning } = useNowcastStore();
  const [isFullScreen, setIsFullScreen] = React.useState(false);
  
  React.useEffect(() => {
    fetchActiveAlerts();
    fetchLatestNowcast();
    fetchRadarAndLightning();
    
    // Auto-refresh every 5 minutes
    const interval = setInterval(() => {
      fetchActiveAlerts();
      fetchLatestNowcast();
      fetchRadarAndLightning();
    }, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [fetchActiveAlerts, fetchLatestNowcast, fetchRadarAndLightning]);
  
  const sortedAlerts = useMemo(() => {
    const order: Record<RiskLevel, number> = { extreme: 0, severe: 1, high: 2, moderate: 3, low: 4, minimal: 5 };
    return [...alerts].sort((a, b) => order[a.riskLevel] - order[b.riskLevel]);
  }, [alerts]);

  const statsData = useMemo(() => [
    {
      title: 'Active Thunderstorm Cells',
      value: cells ? cells.length.toString() : '0',
      trend: null,
      trendColor: 'text-nowcast-success',
      caption: 'current scan',
      icon: Cloud,
      iconColor: 'text-blue-400',
    },
    {
      title: 'Lightning Events',
      value: lightningStrokes ? lightningStrokes.length.toString() : '0',
      trend: null,
      trendColor: 'text-nowcast-danger',
      caption: 'last 30 minutes',
      icon: Zap,
      iconColor: 'text-nowcast-accent',
    },
    {
      title: 'High Risk Areas',
      value: alerts ? alerts.filter(a => a.riskLevel === 'extreme' || a.riskLevel === 'severe').length.toString() : '0',
      trend: null,
      trendColor: '',
      caption: '> 70% probability',
      icon: AlertTriangle,
      iconColor: 'text-nowcast-danger',
    },
    {
      title: 'Coverage Area',
      value: 'North India',
      trend: null,
      trendColor: '',
      caption: '(Active Region)',
      icon: MapPin,
      iconColor: 'text-blue-400',
    },
  ], [cells, lightningStrokes, alerts]);

  return (
    <div className="flex flex-col h-full gap-3 p-4 overflow-y-auto">
      {/* Top Stats Cards */}
      <div className="grid grid-cols-4 gap-2 shrink-0">
        {statsData.map((stat) => (
          <div key={stat.title} className="bg-nowcast-sidebar border border-nowcast-card rounded-xl p-2 flex flex-col justify-between">
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-1.5">
                <stat.icon className={`w-3.5 h-3.5 ${stat.iconColor}`} />
                <span className="text-[9px] text-nowcast-textMuted font-bold uppercase tracking-wider">{stat.title}</span>
              </div>
            </div>
            <div className="flex items-baseline gap-2">
              <span className={`font-bold ${stat.trend === null && isNaN(Number(stat.value)) ? 'text-base' : 'text-xl'}`}>{stat.value}</span>
              {stat.trend && (
                <span className={`text-xs font-medium flex items-center ${stat.trendColor}`}>{stat.trend}</span>
              )}
            </div>
            <span className="text-[10px] text-nowcast-textMuted mt-0.5">{stat.caption}</span>
          </div>
        ))}
      </div>

      {/* Main Content Area */}
      <div className={`flex gap-4 flex-1 min-h-[500px] ${isFullScreen ? 'fixed inset-0 z-[5000] bg-nowcast-bg p-4' : ''}`}>
        {/* Map Section */}
        <div className="flex-1 bg-nowcast-sidebar border border-nowcast-card rounded-xl overflow-hidden relative flex flex-col">
          {/* Map Tabs */}
          <div className="flex items-center gap-2 p-3 bg-nowcast-sidebar border-b border-nowcast-card shrink-0 z-10 relative">
            {MAP_LAYERS.map((layer) => (
              <button
                key={layer.id}
                onClick={() => setSelectedLayer(layer.id)}
                className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors border ${
                  selectedLayer === layer.id
                    ? 'bg-nowcast-accent/10 text-nowcast-accent border-nowcast-accent/20'
                    : 'text-nowcast-textMuted hover:bg-nowcast-card border-transparent'
                }`}
              >
                {layer.label}
              </button>
            ))}
            <div className="flex-1" />
            <button 
              onClick={() => setIsFullScreen(!isFullScreen)}
              className="px-3 py-1.5 rounded-md text-sm font-medium text-nowcast-textMuted hover:bg-nowcast-card border border-nowcast-card transition-colors flex items-center gap-2"
            >
              {isFullScreen ? 'Exit Full Screen' : 'Full Screen'}
            </button>
          </div>
          
          <div className="flex-1 relative">
            <NowcastMap />
            
            {/* Overlay UI on top of Map */}
            <div className="absolute top-4 right-4 z-[400] bg-black/60 backdrop-blur-md text-white px-3 py-1.5 rounded text-xs border border-white/10 shadow-lg">
              Valid Time: 14:45 UTC (+15 min)
            </div>

            {/* Map controls moved to NowcastMap */}
            {/* Legend */}
            <div className="absolute bottom-4 left-4 z-[400] bg-nowcast-sidebar/90 backdrop-blur-md border border-nowcast-card rounded-lg p-3 shadow-lg w-64">
              <div className="text-xs font-medium text-nowcast-text mb-2">Thunderstorm Probability (%)</div>
              <div className="h-3 w-full rounded-sm bg-gradient-to-r from-[#170B3B] via-[#85165E] to-[#FCA311]"></div>
              <div className="flex justify-between text-[10px] text-nowcast-textMuted mt-1">
                <span>0</span>
                <span>20</span>
                <span>40</span>
                <span>60</span>
                <span>80</span>
                <span>100</span>
              </div>
            </div>
          </div>
        </div>

        {/* Active Warnings Panel */}
        <div className="w-80 bg-nowcast-sidebar border border-nowcast-card rounded-xl p-5 flex flex-col gap-4 shrink-0 overflow-y-auto">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-semibold text-nowcast-text flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-nowcast-warning" />
              Active Warnings
            </h3>
            <span className="bg-nowcast-card text-xs font-medium px-2 py-0.5 rounded-full border border-nowcast-border">
              {alerts.length} Total
            </span>
          </div>

          <div className="flex flex-col gap-3">
            {sortedAlerts.length === 0 ? (
              <div className="text-sm text-nowcast-textMuted text-center py-8">
                No active warnings in this region.
              </div>
            ) : (
              sortedAlerts.map((alert) => {
                const cfg = RISK_LEVEL_CONFIG[alert.riskLevel];
                return (
                  <div
                    key={alert.id}
                    className={`
                      flex flex-col gap-1.5 p-3 rounded-lg border
                      shadow-sm ${cfg.bgClass} ${cfg.borderClass}
                    `}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className={`text-xs font-bold uppercase tracking-wider ${cfg.textClass}`}>
                          {cfg.label} Risk
                        </span>
                      </div>
                      <span className="text-[10px] text-nowcast-textMuted font-medium">
                        {formatRelativeTime(alert.validUntil)}
                      </span>
                    </div>
                    
                    <p className="text-sm font-bold text-nowcast-text leading-tight mt-1">
                      {alert.title}
                    </p>
                    <p className="text-xs text-nowcast-textMuted line-clamp-2 leading-relaxed">
                      {alert.description}
                    </p>
                    
                    <div className="flex items-center justify-between mt-2 pt-2 border-t border-nowcast-card/50">
                      <span className="text-xs text-nowcast-textMuted">Thunderstorm Probability</span>
                      <span className={`text-xs font-bold ${cfg.textClass}`}>
                        {(alert.probability * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
