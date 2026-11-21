import React, { useState, useEffect } from 'react';
import { Play, Pause, SkipBack, SkipForward, Clock } from 'lucide-react';

interface TimeSliderProps {
  currentMinute?: number;
  onChange?: (minute: number) => void;
  maxMinutes?: number;
  stepMinutes?: number;
}

export const TimeSlider: React.FC<TimeSliderProps> = ({
  currentMinute = 0,
  onChange,
  maxMinutes = 120,
  stepMinutes = 15,
}) => {
  const [minute, setMinute] = useState<number>(currentMinute);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [speed, setSpeed] = useState<number>(1);

  const steps = [];
  for (let m = 0; m <= maxMinutes; m += stepMinutes) {
    steps.push(m);
  }

  const handleStepChange = (newMin: number) => {
    const clamped = Math.max(0, Math.min(maxMinutes, newMin));
    setMinute(clamped);
    if (onChange) {
      onChange(clamped);
    }
  };

  useEffect(() => {
    let timer: any = null;
    if (isPlaying) {
      const intervalMs = Math.max(500, 1500 / speed);
      timer = setInterval(() => {
        setMinute((prev) => {
          const next = prev + stepMinutes;
          if (next > maxMinutes) {
            return 0;
          }
          if (onChange) {
            onChange(next);
          }
          return next;
        });
      }, intervalMs);
    }
    return () => {
      if (timer) clearInterval(timer);
    };
  }, [isPlaying, speed, maxMinutes, stepMinutes, onChange]);

  const progressPercent = (minute / maxMinutes) * 100;

  return (
    <div className="w-full bg-nowcast-sidebar border border-nowcast-card rounded-xl p-3 flex flex-col gap-2.5">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Clock className="w-4 h-4 text-nowcast-accent" />
          <span className="text-xs font-bold uppercase tracking-wider text-nowcast-text">
            Forecast Horizon
          </span>
          <span className="text-xs font-bold text-nowcast-accent bg-nowcast-accent/10 px-2 py-0.5 rounded border border-nowcast-accent/20">
            {minute === 0 ? 'T = 0 (Live Scan)' : `T + ${minute} min`}
          </span>
        </div>

        <div className="flex items-center gap-1.5">
          <button
            onClick={() => setSpeed((s) => (s === 1 ? 2 : 1))}
            className="text-[11px] font-bold px-2 py-0.5 rounded bg-nowcast-card border border-nowcast-border text-nowcast-textMuted hover:text-nowcast-text transition-colors"
          >
            {speed}x
          </button>
          <button
            onClick={() => handleStepChange(minute - stepMinutes)}
            className="p-1.5 rounded-lg bg-nowcast-card border border-nowcast-border text-nowcast-text hover:text-nowcast-accent transition-colors"
          >
            <SkipBack className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className="p-1.5 rounded-lg bg-nowcast-accent text-nowcast-bg font-bold hover:bg-nowcast-accentHover transition-colors shadow-[0_0_10px_rgba(204,255,0,0.3)]"
          >
            {isPlaying ? <Pause className="w-3.5 h-3.5 fill-current" /> : <Play className="w-3.5 h-3.5 fill-current" />}
          </button>
          <button
            onClick={() => handleStepChange(minute + stepMinutes)}
            className="p-1.5 rounded-lg bg-nowcast-card border border-nowcast-border text-nowcast-text hover:text-nowcast-accent transition-colors"
          >
            <SkipForward className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      <div className="relative w-full flex flex-col gap-1.5">
        <div className="relative w-full h-2 bg-nowcast-card rounded-full overflow-hidden border border-nowcast-border cursor-pointer">
          <div
            className="absolute top-0 bottom-0 left-0 bg-nowcast-accent transition-all duration-300 shadow-[0_0_8px_rgba(204,255,0,0.8)]"
            style={{ width: `${progressPercent}%` }}
          />
        </div>

        <div className="flex justify-between items-center text-[10px] text-nowcast-textMuted font-mono">
          {steps.map((s) => (
            <button
              key={s}
              onClick={() => handleStepChange(s)}
              className={`hover:text-nowcast-accent transition-colors ${
                minute === s ? 'text-nowcast-accent font-bold' : ''
              }`}
            >
              +{s}m
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
