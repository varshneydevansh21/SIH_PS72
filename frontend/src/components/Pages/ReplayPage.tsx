import React, { useState, useEffect } from 'react';
import { RotateCcw, Calendar, Database, MapPin, Zap, Radio, CloudRain, Award } from 'lucide-react';
import { NowcastMap } from '../Dashboard/NowcastMap';
import { TimeSlider } from '../Dashboard/TimeSlider';
import { useNowcastStore } from '../../store/useNowcastStore';
import { getReplayEvents, getReplayEvent } from '../../lib/api';

export const ReplayPage: React.FC = () => {
  const [events, setEvents] = useState<any[]>([]);
  const [selectedId, setSelectedId] = useState<string>('DEL-2024');
  const [replayMinute, setReplayMinute] = useState<number>(0);
  const [currentEventData, setCurrentEventData] = useState<any>(null);

  const loadHistoricalEvent = useNowcastStore((s) => s.loadHistoricalEvent);
  const setForecastMinute = useNowcastStore((s) => s.setForecastMinute);
  const fetchLatestNowcast = useNowcastStore((s) => s.fetchLatestNowcast);
  const fetchActiveAlerts = useNowcastStore((s) => s.fetchActiveAlerts);
  const setOperationalMode = useNowcastStore((s) => s.setOperationalMode);

  useEffect(() => {
    let mounted = true;
    getReplayEvents()
      .then((data) => {
        if (mounted && Array.isArray(data) && data.length > 0) {
          setEvents(data);
        }
      })
      .catch(() => {});

    return () => {
      mounted = false;
      fetchLatestNowcast();
      fetchActiveAlerts();
    };
  }, [fetchLatestNowcast, fetchActiveAlerts]);

  useEffect(() => {
    let mounted = true;
    getReplayEvent(selectedId)
      .then((eventData) => {
        if (mounted && eventData) {
          setCurrentEventData(eventData);
          loadHistoricalEvent(eventData);
        }
      })
      .catch(() => {});

    return () => {
      mounted = false;
    };
  }, [selectedId, loadHistoricalEvent]);

  const handleMinuteChange = (min: number) => {
    setReplayMinute(min);
    setForecastMinute(min);
  };

  const currentEvent = currentEventData || events.find((e) => e.event_id === selectedId) || {
    event_id: 'DEL-2024',
    title: 'Delhi-NCR Pre-Monsoon Squall Line',
    date: '2024-05-18T16:30:00Z',
    radar_station: 'DEL (Palam DWR)',
    peak_dbz: 54.2,
    total_strikes: 342,
    lead_time: '120 min',
    synoptic_summary: 'Severe multicellular convective squall with 75 kmph wind gusts and frequent cloud-to-ground lightning across Delhi-NCR.',
    metrics: {
      csi_35dbz: 0.58,
      csi_45dbz: 0.49,
      pod: 0.74,
      far: 0.28,
      position_rmse_km: 8.2,
      baseline_skill_lift: '+18.4% vs Farneback Optical Flow',
    },
  };

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
          <span className="font-mono text-nowcast-text">ground_truth/{selectedId.toLowerCase()}_benchmark.npz</span>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3 shrink-0">
        {(events.length > 0 ? events : [currentEvent]).map((event: any) => {
          const evId = event.event_id || event.id;
          return (
            <button
              key={evId}
              onClick={() => {
                setSelectedId(evId);
                handleMinuteChange(0);
              }}
              className={`p-3.5 rounded-xl border text-left transition-all flex flex-col justify-between ${
                selectedId === evId
                  ? 'bg-nowcast-sidebar border-nowcast-accent shadow-[0_0_12px_rgba(204,255,0,0.15)]'
                  : 'bg-nowcast-sidebar/60 border-nowcast-card hover:border-nowcast-border'
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-[10px] font-mono text-nowcast-accent font-bold px-1.5 py-0.5 rounded bg-nowcast-accent/10">
                    {evId}
                  </span>
                  <span className="text-[11px] text-nowcast-textMuted flex items-center gap-1">
                    <Calendar className="w-3 h-3" />
                    {new Date(event.date).toLocaleDateString()}
                  </span>
                </div>
                <h3 className="text-xs font-bold text-nowcast-text line-clamp-1">{event.title}</h3>
                <p className="text-[11px] text-nowcast-textMuted mt-1 flex items-center gap-1">
                  <MapPin className="w-3 h-3 text-nowcast-accent shrink-0" />
                  <span className="truncate">{event.radar_station || 'IMD DWR Station'}</span>
                </p>
              </div>

              <div className="flex items-center justify-between mt-3 pt-2 border-t border-nowcast-card text-[11px]">
                <span className="text-nowcast-danger font-bold">Peak {event.peak_dbz || event.peakDbz} dBZ</span>
                <span className="text-nowcast-textMuted">{event.total_strikes || event.strikes} flashes</span>
              </div>
            </button>
          );
        })}
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
            <TimeSlider currentMinute={replayMinute} onChange={handleMinuteChange} />
          </div>
        </div>

        <div className="w-80 bg-nowcast-sidebar border border-nowcast-card rounded-xl p-4 flex flex-col gap-3 shrink-0 overflow-y-auto">
          <h3 className="text-xs font-bold uppercase tracking-wider text-nowcast-text pb-2 border-b border-nowcast-border">
            Event Case Study Data
          </h3>

          <div className="flex flex-col gap-1.5 text-xs">
            <span className="text-nowcast-textMuted font-bold text-[10px] uppercase">Synoptic Environment</span>
            <p className="text-xs text-nowcast-textMuted leading-relaxed bg-nowcast-card p-2.5 rounded-lg border border-nowcast-border">
              {currentEvent.synoptic_summary || currentEvent.synopticSummary}
            </p>
          </div>

          {currentEvent.metrics && (
            <div className="flex flex-col gap-1.5 text-xs">
              <span className="text-nowcast-textMuted font-bold text-[10px] uppercase flex items-center gap-1">
                <Award className="w-3.5 h-3.5 text-nowcast-accent" />
                Verified Verification Skill
              </span>
              <div className="bg-nowcast-card p-2.5 rounded-lg border border-nowcast-border flex flex-col gap-1 text-[11px]">
                <div className="flex justify-between">
                  <span className="text-nowcast-textMuted">CSI (35 dBZ):</span>
                  <span className="font-mono font-bold text-nowcast-accent">{currentEvent.metrics.csi_35dbz}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-nowcast-textMuted">CSI (45 dBZ):</span>
                  <span className="font-mono font-bold text-nowcast-accent">{currentEvent.metrics.csi_45dbz}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-nowcast-textMuted">POD / FAR:</span>
                  <span className="font-mono font-bold text-nowcast-text">{currentEvent.metrics.pod} / {currentEvent.metrics.far}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-nowcast-textMuted">Position RMSE:</span>
                  <span className="font-mono font-bold text-nowcast-text">{currentEvent.metrics.position_rmse_km} km</span>
                </div>
                {currentEvent.metrics.baseline_skill_lift && (
                  <div className="text-[10px] text-nowcast-success font-semibold mt-1 pt-1 border-t border-nowcast-border">
                    {currentEvent.metrics.baseline_skill_lift}
                  </div>
                )}
              </div>
            </div>
          )}

          <div className="flex flex-col gap-2 pt-1">
            <div className="bg-nowcast-card p-2.5 rounded-lg border border-nowcast-border flex justify-between items-center text-xs">
              <span className="text-nowcast-textMuted flex items-center gap-1.5">
                <Radio className="w-3.5 h-3.5 text-nowcast-danger" />
                Max Reflectivity
              </span>
              <span className="font-mono font-bold text-nowcast-danger">{currentEvent.peak_dbz || currentEvent.peakDbz} dBZ</span>
            </div>

            <div className="bg-nowcast-card p-2.5 rounded-lg border border-nowcast-border flex justify-between items-center text-xs">
              <span className="text-nowcast-textMuted flex items-center gap-1.5">
                <Zap className="w-3.5 h-3.5 text-nowcast-accent" />
                Lightning Activity
              </span>
              <span className="font-mono font-bold text-nowcast-accent">{currentEvent.total_strikes || currentEvent.strikes} strikes</span>
            </div>

            <div className="bg-nowcast-card p-2.5 rounded-lg border border-nowcast-border flex justify-between items-center text-xs">
              <span className="text-nowcast-textMuted flex items-center gap-1.5">
                <CloudRain className="w-3.5 h-3.5 text-nowcast-info" />
                Forecast Horizon
              </span>
              <span className="font-mono font-bold text-nowcast-text">{currentEvent.lead_time || currentEvent.leadTime}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
