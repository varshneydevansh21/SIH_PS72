import React, { useState } from 'react';
import { AlertTriangle, Zap, X, ShieldAlert } from 'lucide-react';
import { WeatherAlert, RISK_LEVEL_CONFIG } from '../../types/nowcast';

interface AlertTickerProps {
  alerts: WeatherAlert[];
}

export const AlertTicker: React.FC<AlertTickerProps> = ({ alerts }) => {
  const [dismissed, setDismissed] = useState<Set<string>>(new Set());

  const activeAlerts = alerts
    .filter((a) => !dismissed.has(a.id))
    .filter((a) => a.riskLevel === 'extreme' || a.riskLevel === 'severe' || a.riskLevel === 'high');

  if (activeAlerts.length === 0) {
    return null;
  }

  const current = activeAlerts[0];
  const config = RISK_LEVEL_CONFIG[current.riskLevel] || RISK_LEVEL_CONFIG.moderate;

  return (
    <div className="w-full bg-nowcast-sidebar border-b border-nowcast-danger/30 px-4 py-2 flex items-center justify-between shadow-[0_4px_12px_rgba(255,71,87,0.15)] animate-pulse-risk">
      <div className="flex items-center gap-3 overflow-hidden">
        <div className="flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-nowcast-danger/20 text-nowcast-danger border border-nowcast-danger/40">
          <ShieldAlert className="w-3.5 h-3.5 text-nowcast-danger" />
          <span>Active Warning</span>
        </div>

        <div className="flex items-center gap-2 truncate">
          <span className="text-xs font-bold text-nowcast-text truncate">
            {current.title}
          </span>
          <span className="text-xs text-nowcast-textMuted hidden md:inline truncate">
            — {current.description}
          </span>
        </div>
      </div>

      <div className="flex items-center gap-3 shrink-0">
        <span
          className="text-[10px] font-bold px-2 py-0.5 rounded border"
          style={{
            backgroundColor: `${config.color}20`,
            color: config.color,
            borderColor: `${config.color}50`,
          }}
        >
          {config.label}
        </span>
        <button
          onClick={() => setDismissed((prev) => new Set(prev).add(current.id))}
          className="text-nowcast-textMuted hover:text-nowcast-text p-1 rounded hover:bg-nowcast-card transition-colors"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
};
