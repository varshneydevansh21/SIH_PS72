import React, { useState } from 'react';
import { RadarPanel } from '../Dashboard/RadarPanel';
import { LightningPanel } from '../Dashboard/LightningPanel';
import { Satellite, Wind, Thermometer, Radio, CheckCircle2 } from 'lucide-react';

export const ObservationsPage: React.FC = () => {
  const [selectedStation, setSelectedStation] = useState<string>('DEL');

  return (
    <div className="flex flex-col h-full gap-4 p-6 overflow-y-auto bg-nowcast-bg text-nowcast-text">
      <div className="flex items-center justify-between pb-4 border-b border-nowcast-border">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-nowcast-text flex items-center gap-2">
            <Radio className="w-5 h-5 text-nowcast-accent" />
            Live Atmospheric Sensor Observations
          </h1>
          <p className="text-xs text-nowcast-textMuted mt-1">
            Real-time telemetry from IMD DWR network, ISRO INSAT-3D/3DR, ILDN lightning sensors, and NWP models
          </p>
        </div>
        <div className="flex items-center gap-2 bg-nowcast-success/10 border border-nowcast-success/30 px-3 py-1.5 rounded-lg text-nowcast-success text-xs font-bold">
          <CheckCircle2 className="w-4 h-4" />
          4 Multi-Modal Feeds Online
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <RadarPanel onStationSelect={setSelectedStation} />
        <LightningPanel totalStrikes={187} cgCount={112} icCount={75} flashRatePerMin={22} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-1">
        <div className="bg-nowcast-sidebar border border-nowcast-card rounded-xl p-5 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Satellite className="w-4 h-4 text-nowcast-accent" />
              <h3 className="text-xs font-bold uppercase tracking-wider text-nowcast-text">
                ISRO INSAT-3D / 3DR Satellite
              </h3>
            </div>
            <span className="text-[10px] text-nowcast-success font-medium bg-nowcast-success/10 px-2 py-0.5 rounded border border-nowcast-success/20">
              Payload Operational
            </span>
          </div>

          <div className="grid grid-cols-3 gap-2 my-2">
            <div className="bg-nowcast-card p-2.5 rounded-lg border border-nowcast-border">
              <span className="text-[10px] text-nowcast-textMuted font-bold uppercase">TIR1 (10.8 µm)</span>
              <p className="text-lg font-bold font-mono text-nowcast-text mt-0.5">214.2 K</p>
              <span className="text-[9px] text-nowcast-danger">Overshooting Top</span>
            </div>
            <div className="bg-nowcast-card p-2.5 rounded-lg border border-nowcast-border">
              <span className="text-[10px] text-nowcast-textMuted font-bold uppercase">Water Vapour</span>
              <p className="text-lg font-bold font-mono text-nowcast-text mt-0.5">228.6 K</p>
              <span className="text-[9px] text-nowcast-info">Mid-Tropospheric</span>
            </div>
            <div className="bg-nowcast-card p-2.5 rounded-lg border border-nowcast-border">
              <span className="text-[10px] text-nowcast-textMuted font-bold uppercase">TIR1 - WV Diff</span>
              <p className="text-lg font-bold font-mono text-nowcast-accent mt-0.5">-14.4 K</p>
              <span className="text-[9px] text-nowcast-warning font-bold">Deep Convection</span>
            </div>
          </div>

          <div className="text-xs text-nowcast-textMuted flex justify-between pt-2 border-t border-nowcast-card">
            <span>Sampling Resolution: 4 km (resampled to 2 km)</span>
            <span className="font-mono text-nowcast-text">MOSDAC Real-Time Feed</span>
          </div>
        </div>

        <div className="bg-nowcast-sidebar border border-nowcast-card rounded-xl p-5 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Wind className="w-4 h-4 text-nowcast-accent" />
              <h3 className="text-xs font-bold uppercase tracking-wider text-nowcast-text">
                NWP Instability Indices (GFS / NCUM)
              </h3>
            </div>
            <span className="text-[10px] text-nowcast-warning font-medium bg-nowcast-warning/10 px-2 py-0.5 rounded border border-nowcast-warning/20">
              High Instability
            </span>
          </div>

          <div className="grid grid-cols-3 gap-2 my-2">
            <div className="bg-nowcast-card p-2.5 rounded-lg border border-nowcast-border">
              <span className="text-[10px] text-nowcast-textMuted font-bold uppercase">CAPE</span>
              <p className="text-lg font-bold font-mono text-nowcast-danger mt-0.5">3,420 J/kg</p>
              <span className="text-[9px] text-nowcast-danger font-bold">Extreme Energy</span>
            </div>
            <div className="bg-nowcast-card p-2.5 rounded-lg border border-nowcast-border">
              <span className="text-[10px] text-nowcast-textMuted font-bold uppercase">CIN</span>
              <p className="text-lg font-bold font-mono text-nowcast-text mt-0.5">25 J/kg</p>
              <span className="text-[9px] text-nowcast-success">Weak Cap Broken</span>
            </div>
            <div className="bg-nowcast-card p-2.5 rounded-lg border border-nowcast-border">
              <span className="text-[10px] text-nowcast-textMuted font-bold uppercase">0-6 km Shear</span>
              <p className="text-lg font-bold font-mono text-nowcast-accent mt-0.5">28 m/s</p>
              <span className="text-[9px] text-nowcast-warning font-bold">Organized Storms</span>
            </div>
          </div>

          <div className="text-xs text-nowcast-textMuted flex justify-between pt-2 border-t border-nowcast-card">
            <span>Forecast Cycle: 06:00 UTC Run</span>
            <span className="font-mono text-nowcast-text">GFS Global Model</span>
          </div>
        </div>
      </div>
    </div>
  );
};
