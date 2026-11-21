import React from 'react';
import { Zap, Activity, ShieldCheck, Flame } from 'lucide-react';

interface LightningPanelProps {
  totalStrikes?: number;
  cgCount?: number;
  icCount?: number;
  flashRatePerMin?: number;
}

export const LightningPanel: React.FC<LightningPanelProps> = ({
  totalStrikes = 187,
  cgCount = 112,
  icCount = 75,
  flashRatePerMin = 22,
}) => {
  const cgPercent = Math.round((cgCount / Math.max(1, totalStrikes)) * 100);
  const icPercent = 100 - cgPercent;

  return (
    <div className="flex flex-col gap-3.5 bg-nowcast-sidebar border border-nowcast-card rounded-xl p-4 text-nowcast-text">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Zap className="w-4 h-4 text-nowcast-accent" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-nowcast-text">
            Lightning Detection (ILDN / GLD360)
          </h3>
        </div>
        <span className="flex items-center gap-1.5 text-[10px] text-nowcast-danger font-medium bg-nowcast-danger/10 px-2 py-0.5 rounded border border-nowcast-danger/20">
          <span className="w-2 h-2 rounded-full bg-nowcast-danger animate-ping" />
          Severe Density
        </span>
      </div>

      <div className="grid grid-cols-2 gap-2">
        <div className="bg-nowcast-card p-3 rounded-lg border border-nowcast-border flex flex-col justify-between">
          <span className="text-[10px] font-bold text-nowcast-textMuted uppercase">
            30-Min Strike Count
          </span>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-2xl font-bold font-mono text-nowcast-text">{totalStrikes}</span>
            <span className="text-[10px] text-nowcast-danger font-bold">flashes</span>
          </div>
        </div>

        <div className="bg-nowcast-card p-3 rounded-lg border border-nowcast-border flex flex-col justify-between">
          <span className="text-[10px] font-bold text-nowcast-textMuted uppercase">
            Flash Rate
          </span>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-2xl font-bold font-mono text-nowcast-accent">{flashRatePerMin}</span>
            <span className="text-[10px] text-nowcast-accent font-bold">/ min</span>
          </div>
        </div>
      </div>

      <div className="flex flex-col gap-2 bg-nowcast-card p-3 rounded-lg border border-nowcast-border">
        <div className="flex justify-between text-xs font-bold">
          <span className="flex items-center gap-1 text-nowcast-warning">
            <span className="w-2 h-2 rounded-full bg-nowcast-warning" />
            Cloud-to-Ground (CG)
          </span>
          <span className="font-mono">{cgCount} ({cgPercent}%)</span>
        </div>

        <div className="w-full h-2 rounded-full bg-nowcast-border overflow-hidden flex">
          <div
            className="h-full bg-nowcast-warning"
            style={{ width: `${cgPercent}%` }}
          />
          <div
            className="h-full bg-nowcast-info"
            style={{ width: `${icPercent}%` }}
          />
        </div>

        <div className="flex justify-between text-xs font-bold">
          <span className="flex items-center gap-1 text-nowcast-info">
            <span className="w-2 h-2 rounded-full bg-nowcast-info" />
            Intra-Cloud (IC)
          </span>
          <span className="font-mono">{icCount} ({icPercent}%)</span>
        </div>
      </div>

      <div className="flex items-center justify-between text-[11px] text-nowcast-textMuted pt-1 border-t border-nowcast-card">
        <span>Average Peak Current:</span>
        <span className="font-mono font-bold text-nowcast-text">-32.4 kA</span>
      </div>
    </div>
  );
};
