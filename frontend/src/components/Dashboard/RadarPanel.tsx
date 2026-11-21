import React, { useState } from 'react';
import { Radio, RefreshCw, Layers, Compass } from 'lucide-react';
import { RADAR_COLOR_SCALE } from '../../types/radar';

interface RadarPanelProps {
  onStationSelect?: (stationId: string) => void;
}

const STATIONS = [
  { id: 'DEL', name: 'New Delhi (Palam)', lat: 28.58, lon: 77.21, band: 'S', range: '250 km' },
  { id: 'KOL', name: 'Kolkata', lat: 22.57, lon: 88.36, band: 'S', range: '250 km' },
  { id: 'MUM', name: 'Mumbai', lat: 19.08, lon: 72.88, band: 'S', range: '250 km' },
  { id: 'CHE', name: 'Chennai', lat: 13.08, lon: 80.27, band: 'S', range: '250 km' },
  { id: 'PAT', name: 'Patna', lat: 25.61, lon: 85.14, band: 'C', range: '250 km' },
  { id: 'HYD', name: 'Hyderabad', lat: 17.38, lon: 78.49, band: 'S', range: '250 km' },
];

export const RadarPanel: React.FC<RadarPanelProps> = ({ onStationSelect }) => {
  const [selectedStation, setSelectedStation] = useState<string>('DEL');
  const [product, setProduct] = useState<'Z' | 'ZDR' | 'VEL'>('Z');

  const current = STATIONS.find((s) => s.id === selectedStation) || STATIONS[0];

  const handleSelect = (id: string) => {
    setSelectedStation(id);
    if (onStationSelect) {
      onStationSelect(id);
    }
  };

  return (
    <div className="flex flex-col gap-3.5 bg-nowcast-sidebar border border-nowcast-card rounded-xl p-4 text-nowcast-text">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Radio className="w-4 h-4 text-nowcast-accent" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-nowcast-text">
            Doppler Weather Radar (DWR)
          </h3>
        </div>
        <span className="flex items-center gap-1.5 text-[10px] text-nowcast-success font-medium">
          <span className="w-2 h-2 rounded-full bg-nowcast-success animate-pulse" />
          Live Ingestion
        </span>
      </div>

      <div className="flex flex-col gap-1.5">
        <label className="text-[11px] font-bold text-nowcast-textMuted uppercase">
          Select DWR Radar Station
        </label>
        <select
          value={selectedStation}
          onChange={(e) => handleSelect(e.target.value)}
          className="w-full bg-nowcast-card border border-nowcast-border text-nowcast-text text-xs rounded-lg px-3 py-2 outline-none focus:border-nowcast-accent"
        >
          {STATIONS.map((s) => (
            <option key={s.id} value={s.id}>
              {s.name} ({s.id}) — {s.band}-Band
            </option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-3 gap-2">
        <button
          onClick={() => setProduct('Z')}
          className={`py-1.5 px-2 rounded-lg text-xs font-bold transition-all border ${
            product === 'Z'
              ? 'bg-nowcast-accent/20 text-nowcast-accent border-nowcast-accent/50 shadow-[0_0_10px_rgba(204,255,0,0.15)]'
              : 'bg-nowcast-card text-nowcast-textMuted border-nowcast-border hover:text-nowcast-text'
          }`}
        >
          Reflectivity (Z)
        </button>
        <button
          onClick={() => setProduct('ZDR')}
          className={`py-1.5 px-2 rounded-lg text-xs font-bold transition-all border ${
            product === 'ZDR'
              ? 'bg-nowcast-accent/20 text-nowcast-accent border-nowcast-accent/50 shadow-[0_0_10px_rgba(204,255,0,0.15)]'
              : 'bg-nowcast-card text-nowcast-textMuted border-nowcast-border hover:text-nowcast-text'
          }`}
        >
          Diff. Refl (Z_DR)
        </button>
        <button
          onClick={() => setProduct('VEL')}
          className={`py-1.5 px-2 rounded-lg text-xs font-bold transition-all border ${
            product === 'VEL'
              ? 'bg-nowcast-accent/20 text-nowcast-accent border-nowcast-accent/50 shadow-[0_0_10px_rgba(204,255,0,0.15)]'
              : 'bg-nowcast-card text-nowcast-textMuted border-nowcast-border hover:text-nowcast-text'
          }`}
        >
          Velocity (V)
        </button>
      </div>

      <div className="flex flex-col gap-1 bg-nowcast-card p-2.5 rounded-lg border border-nowcast-border text-xs">
        <div className="flex justify-between text-nowcast-textMuted">
          <span>Coordinates:</span>
          <span className="font-mono text-nowcast-text">{current.lat.toFixed(2)}°N, {current.lon.toFixed(2)}°E</span>
        </div>
        <div className="flex justify-between text-nowcast-textMuted">
          <span>Scan Radius:</span>
          <span className="font-mono text-nowcast-text">{current.range}</span>
        </div>
        <div className="flex justify-between text-nowcast-textMuted">
          <span>Max Reflectivity:</span>
          <span className="font-mono font-bold text-nowcast-danger">54.2 dBZ</span>
        </div>
      </div>

      <div className="flex flex-col gap-1.5">
        <div className="flex justify-between items-center text-[11px] font-bold text-nowcast-textMuted">
          <span>Reflectivity Scale (dBZ)</span>
          <span className="text-[10px] text-nowcast-accent">≥ 35 dBZ = Convective Storm</span>
        </div>
        <div className="flex h-3 w-full rounded overflow-hidden border border-nowcast-border">
          {RADAR_COLOR_SCALE.map((step) => (
            <div
              key={step.dbz}
              className="flex-1 h-full"
              style={{ backgroundColor: step.color }}
              title={step.label}
            />
          ))}
        </div>
        <div className="flex justify-between text-[9px] text-nowcast-textMuted font-mono">
          <span>0</span>
          <span>15</span>
          <span>35</span>
          <span>50</span>
          <span>65</span>
          <span>70+</span>
        </div>
      </div>
    </div>
  );
};
