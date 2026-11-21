import React, { useState } from 'react';
import { RotateCcw, Calendar, Play, Pause, Database, MapPin, Zap, Radio, CloudRain } from 'lucide-react';
import { NowcastMap } from '../Dashboard/NowcastMap';
import { TimeSlider } from '../Dashboard/TimeSlider';

const HISTORICAL_EVENTS = [
  {
    id: 'DEL-2024',
    title: 'Delhi-NCR Pre-Monsoon Squall Line',
    date: 'May 18, 2024',
    location: 'North India (Haryana → Delhi → West UP)',
    center: [28.6139, 77.2090] as [number, number],
    peakDbz: 54.2,
    strikes: 342,
    leadTime: '120 min',
    synopticSummary: 'Intense westerly trough triggering severe multicellular convective squall with 75 kmph wind gusts and frequent cloud-to-ground lightning.',
  },
  {
    id: 'KOL-2023',
    title: 'Kolkata Nor\'wester (Kalbaishakhi)',
    date: 'April 22, 2023',
    location: 'East India (Gangetic West Bengal)',
    center: [22.5726, 88.3639] as [number, number],
    peakDbz: 58.0,
    strikes: 512,
    leadTime: '120 min',
    synopticSummary: 'Severe Kalbaishakhi supercell storm with large hailstones (up to 30mm) and severe downdrafts exceeding 85 kmph.',
  },
  {
    id: 'MUM-2023',
    title: 'Mumbai Coastal Convective Band',
    date: 'July 14, 2023',
    location: 'West Coast (Konkan Region)',
    center: [19.0760, 72.8777] as [number, number],
    peakDbz: 51.5,
    strikes: 210,
    leadTime: '120 min',
    synopticSummary: 'Offshore convective band propagating inland, causing rapid precipitation rate over 55 mm/hr in Mumbai suburban areas.',
  },
];

export const ReplayPage: React.FC = () => {
  const [selectedId, setSelectedId] = useState<string>('DEL-2024');
  const [replayMinute, setReplayMinute] = useState<number>(0);

  const currentEvent = HISTORICAL_EVENTS.find((e) => e.id === selectedId) || HISTORICAL_EVENTS[0];

  return (
    <div className="flex flex-col h-full gap-3.5 p-4 overflow-y-auto bg-nowcast-bg text-nowcast-text">
      <div className="flex items-center justify-between pb-3 border-b border-nowcast-border">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-nowcast-text flex items-center gap-2">
            <RotateCcw className="w-5 h-5 text-nowcast-accent" />
            Historical Extreme Convective Event Replay
          </h1>
          <p className="text-xs text-nowcast-textMuted mt-1">
            Deterministic evaluation against benchmarked IMD Doppler radar sweeps and ground-truth storm trajectories
          </p>
        </div>

        <div className="flex items-center gap-2 bg-nowcast-card border border-nowcast-border px-3 py-1.5 rounded-lg text-xs">
          <Database className="w-4 h-4 text-nowcast-accent" />
          <span className="font-mono text-nowcast-text">ground_truth/delhi_convective_squall_2024.npz</span>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3 shrink-0">
        {HISTORICAL_EVENTS.map((event) => (
          <button
            key={event.id}
            onClick={() => {
              setSelectedId(event.id);
              setReplayMinute(0);
            }}
            className={`p-3.5 rounded-xl border text-left transition-all flex flex-col justify-between ${
              selectedId === event.id
                ? 'bg-nowcast-sidebar border-nowcast-accent shadow-[0_0_12px_rgba(204,255,0,0.15)]'
                : 'bg-nowcast-sidebar/60 border-nowcast-card hover:border-nowcast-border'
            }`}
          >
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-[10px] font-mono text-nowcast-accent font-bold px-1.5 py-0.5 rounded bg-nowcast-accent/10">
                  {event.id}
                </span>
                <span className="text-[11px] text-nowcast-textMuted flex items-center gap-1">
                  <Calendar className="w-3 h-3" />
                  {event.date}
                </span>
              </div>
              <h3 className="text-xs font-bold text-nowcast-text line-clamp-1">{event.title}</h3>
              <p className="text-[11px] text-nowcast-textMuted mt-1 flex items-center gap-1">
                <MapPin className="w-3 h-3 text-nowcast-accent shrink-0" />
                <span className="truncate">{event.location}</span>
              </p>
            </div>

            <div className="flex items-center justify-between mt-3 pt-2 border-t border-nowcast-card text-[11px]">
              <span className="text-nowcast-danger font-bold">Peak {event.peakDbz} dBZ</span>
              <span className="text-nowcast-textMuted">{event.strikes} flashes</span>
            </div>
          </button>
        ))}
      </div>

      <div className="flex gap-4 flex-1 min-h-[440px]">
        <div className="flex-1 bg-nowcast-sidebar border border-nowcast-card rounded-xl overflow-hidden relative flex flex-col">
          <div className="flex items-center justify-between p-3 bg-nowcast-sidebar border-b border-nowcast-card shrink-0">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-nowcast-text">Replay Simulation:</span>
              <span className="text-xs font-mono text-nowcast-accent bg-nowcast-accent/10 px-2 py-0.5 rounded border border-nowcast-accent/20">
                {currentEvent.title} (T + {replayMinute}m)
              </span>
            </div>
            <span className="text-xs text-nowcast-textMuted font-mono">2 km Grid Resolution (512x512)</span>
          </div>

          <div className="flex-1 relative">
            <NowcastMap />
          </div>

          <div className="p-3 bg-nowcast-sidebar border-t border-nowcast-card shrink-0">
            <TimeSlider currentMinute={replayMinute} onChange={setReplayMinute} />
          </div>
        </div>

        <div className="w-72 bg-nowcast-sidebar border border-nowcast-card rounded-xl p-4 flex flex-col gap-3 shrink-0">
          <h3 className="text-xs font-bold uppercase tracking-wider text-nowcast-text pb-2 border-b border-nowcast-border">
            Event Case Study Data
          </h3>

          <div className="flex flex-col gap-1.5 text-xs">
            <span className="text-nowcast-textMuted font-bold text-[10px] uppercase">Synoptic Environment</span>
            <p className="text-xs text-nowcast-textMuted leading-relaxed bg-nowcast-card p-2.5 rounded-lg border border-nowcast-border">
              {currentEvent.synopticSummary}
            </p>
          </div>

          <div className="flex flex-col gap-2 pt-2">
            <div className="bg-nowcast-card p-2.5 rounded-lg border border-nowcast-border flex justify-between items-center text-xs">
              <span className="text-nowcast-textMuted flex items-center gap-1.5">
                <Radio className="w-3.5 h-3.5 text-nowcast-danger" />
                Max Reflectivity
              </span>
              <span className="font-mono font-bold text-nowcast-danger">{currentEvent.peakDbz} dBZ</span>
            </div>

            <div className="bg-nowcast-card p-2.5 rounded-lg border border-nowcast-border flex justify-between items-center text-xs">
              <span className="text-nowcast-textMuted flex items-center gap-1.5">
                <Zap className="w-3.5 h-3.5 text-nowcast-accent" />
                Lightning Activity
              </span>
              <span className="font-mono font-bold text-nowcast-accent">{currentEvent.strikes} strikes</span>
            </div>

            <div className="bg-nowcast-card p-2.5 rounded-lg border border-nowcast-border flex justify-between items-center text-xs">
              <span className="text-nowcast-textMuted flex items-center gap-1.5">
                <CloudRain className="w-3.5 h-3.5 text-nowcast-info" />
                Forecast Horizon
              </span>
              <span className="font-mono font-bold text-nowcast-text">{currentEvent.leadTime}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
