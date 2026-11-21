import React, { useState, useMemo } from 'react';
import { useNowcastStore } from '../../store/useNowcastStore';
import { RISK_LEVEL_CONFIG, RiskLevel, WeatherAlert } from '../../types/nowcast';
import { Bell, AlertTriangle, Zap, CloudLightning, ShieldAlert, Filter, Send, MapPin } from 'lucide-react';

function getIcon(eventType: string) {
  switch (eventType) {
    case 'EXTREME_LIGHTNING':
      return <Zap className="w-4 h-4" />;
    case 'HAILSTORM':
    case 'SQUALL':
      return <CloudLightning className="w-4 h-4" />;
    default:
      return <AlertTriangle className="w-4 h-4" />;
  }
}

function formatRemaining(validUntil: string): string {
  const diff = new Date(validUntil).getTime() - Date.now();
  if (diff <= 0) return 'Expired';
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m active`;
  const hrs = Math.floor(mins / 60);
  return `${hrs}h ${mins % 60}m active`;
}

export const AlertsPage: React.FC = () => {
  const { alerts } = useNowcastStore();
  const [filterLevel, setFilterLevel] = useState<string>('all');
  const [dispatched, setDispatched] = useState<Set<string>>(new Set());

  const filtered = useMemo(() => {
    if (filterLevel === 'all') return alerts;
    return alerts.filter((a) => a.riskLevel === filterLevel);
  }, [alerts, filterLevel]);

  const handleDispatch = (id: string) => {
    setDispatched((prev) => new Set(prev).add(id));
  };

  return (
    <div className="flex flex-col h-full gap-4 p-6 overflow-y-auto bg-nowcast-bg text-nowcast-text">
      <div className="flex items-center justify-between pb-4 border-b border-nowcast-border">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-nowcast-text flex items-center gap-2">
            <Bell className="w-5 h-5 text-nowcast-accent" />
            Severe Weather Alerts & Disaster Management Console
          </h1>
          <p className="text-xs text-nowcast-textMuted mt-1">
            Automated polygon-contoured alerts generated from UNet-ConvLSTM predictions (≥ 35 dBZ threshold)
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs font-bold text-nowcast-textMuted">Filter:</span>
          {['all', 'extreme', 'severe', 'high', 'moderate'].map((lvl) => (
            <button
              key={lvl}
              onClick={() => setFilterLevel(lvl)}
              className={`px-3 py-1 rounded-md text-xs font-bold capitalize transition-colors border ${
                filterLevel === lvl
                  ? 'bg-nowcast-accent/20 text-nowcast-accent border-nowcast-accent/40'
                  : 'bg-nowcast-card text-nowcast-textMuted border-nowcast-border hover:text-nowcast-text'
              }`}
            >
              {lvl}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5">
        {filtered.length === 0 ? (
          <div className="col-span-full py-16 text-center text-nowcast-textMuted text-sm">
            No alerts found matching filter criteria.
          </div>
        ) : (
          filtered.map((alert) => {
            const cfg = RISK_LEVEL_CONFIG[alert.riskLevel] || RISK_LEVEL_CONFIG.moderate;
            const isSent = dispatched.has(alert.id);

            return (
              <div
                key={alert.id}
                className="bg-nowcast-sidebar border border-nowcast-card rounded-xl p-4 flex flex-col justify-between transition-all hover:border-nowcast-border shadow-sm"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span
                      className="text-[10px] font-bold px-2 py-0.5 rounded border uppercase tracking-wider flex items-center gap-1"
                      style={{
                        backgroundColor: `${cfg.color}15`,
                        color: cfg.color,
                        borderColor: `${cfg.color}40`,
                      }}
                    >
                      {getIcon(alert.eventType)}
                      {cfg.label}
                    </span>

                    <span className="text-[10px] font-mono text-nowcast-textMuted">
                      {formatRemaining(alert.validUntil)}
                    </span>
                  </div>

                  <h3 className="text-sm font-bold text-nowcast-text mb-1 leading-snug">
                    {alert.title}
                  </h3>

                  <p className="text-xs text-nowcast-textMuted line-clamp-3 leading-relaxed mb-3">
                    {alert.description}
                  </p>
                </div>

                <div className="flex flex-col gap-2 pt-3 border-t border-nowcast-card">
                  <div className="flex justify-between text-xs text-nowcast-textMuted">
                    <span className="flex items-center gap-1">
                      <MapPin className="w-3.5 h-3.5 text-nowcast-accent" />
                      {alert.latitude.toFixed(2)}°N, {alert.longitude.toFixed(2)}°E
                    </span>
                    <span className="font-bold text-nowcast-accent">
                      {(alert.probability * 100).toFixed(0)}% Probability
                    </span>
                  </div>

                  <div className="flex items-center justify-between mt-1">
                    <span className="text-[10px] text-nowcast-textMuted">Radius: {alert.radius_km} km</span>
                    <button
                      onClick={() => handleDispatch(alert.id)}
                      disabled={isSent}
                      className={`px-3 py-1 rounded text-xs font-bold flex items-center gap-1.5 transition-colors ${
                        isSent
                          ? 'bg-nowcast-success/20 text-nowcast-success border border-nowcast-success/30 cursor-default'
                          : 'bg-nowcast-accent text-nowcast-bg hover:bg-nowcast-accentHover shadow-[0_0_10px_rgba(204,255,0,0.2)]'
                      }`}
                    >
                      <Send className="w-3 h-3" />
                      {isSent ? 'Dispatched' : 'Broadcast Alert'}
                    </button>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
