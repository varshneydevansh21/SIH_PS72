import React, { useEffect, useState, useMemo } from 'react';
import { MapContainer, TileLayer, Circle, Popup, useMap, CircleMarker } from 'react-leaflet';
import { useNowcastStore } from '../../store/useNowcastStore';
import {
  type WeatherAlert,
  type RiskLevel,
  RISK_LEVEL_CONFIG,
} from '../../types/nowcast';
import { AlertTriangle, Shield, Zap, CloudLightning, X, Plus, Minus } from 'lucide-react';

// India center
const MAP_CENTER = [20.5937, 78.9629] as [number, number];
const ZOOM = 5;

/** Resolve the icon component by event type. */
function getEventIcon(eventType: string) {
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

/** Format a relative time string from an ISO timestamp. */
function formatRelativeTime(iso: string): string {
  const diff = new Date(iso).getTime() - Date.now();
  if (diff <= 0) return 'Expired';
  const minutes = Math.floor(diff / 60_000);
  if (minutes < 60) return `${minutes}m remaining`;
  const hours = Math.floor(minutes / 60);
  return `${hours}h ${minutes % 60}m remaining`;
}

/** Fit the map to show all alert and cell markers. */
function MapUpdater({ cells, alerts }: { cells: any[]; alerts: WeatherAlert[] }) {
  const map = useMap();
  const { mapCenter, mapZoom, setMapCenter } = useNowcastStore();

  useEffect(() => {
    if (mapCenter) {
      map.flyTo(mapCenter, mapZoom || 8, { duration: 1.5 });
      setTimeout(() => setMapCenter(null), 1500);
    }
  }, [mapCenter, mapZoom, map, setMapCenter]);
  return null;
}

function CustomZoomControl() {
  const map = useMap();
  return (
    <div className="absolute top-4 left-4 z-[400] flex flex-col bg-nowcast-sidebar/90 backdrop-blur-md border border-nowcast-card rounded-md shadow-lg overflow-hidden">
      <button onClick={(e) => { e.preventDefault(); map.zoomIn(); }} className="p-2 hover:bg-nowcast-card transition-colors border-b border-nowcast-card">
        <Plus className="w-4 h-4 text-nowcast-text" />
      </button>
      <button onClick={(e) => { e.preventDefault(); map.zoomOut(); }} className="p-2 hover:bg-nowcast-card transition-colors">
        <Minus className="w-4 h-4 text-nowcast-text" />
      </button>
    </div>
  );
}


// ────────────────────────────────────────────────────────────────
//  NowcastMap – primary export
// ────────────────────────────────────────────────────────────────
export function NowcastMap() {
  const { cells, alerts, lightningStrokes } = useNowcastStore();
  const [loading, setLoading] = useState(true);
  const [dismissedAlerts, setDismissedAlerts] = useState<Set<string>>(new Set());

  useEffect(() => {
    // Short delay to show the loading animation, then reveal the map
    const timer = setTimeout(() => setLoading(false), 1200);
    return () => clearTimeout(timer);
  }, []);

  const visibleAlerts = useMemo(
    () => alerts.filter((a) => !dismissedAlerts.has(a.id)),
    [alerts, dismissedAlerts],
  );

  return (
    <div className="h-full w-full bg-nowcast-bg relative">
      <MapContainer
        center={MAP_CENTER}
        zoom={ZOOM}
        className="h-full w-full z-0"
        zoomControl={false}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          className="map-tiles"
        />

        {/* ── Warning Alert Zones ── */}
        {visibleAlerts.map((alert) => {
          const cfg = RISK_LEVEL_CONFIG[alert.riskLevel];
          return (
            <React.Fragment key={alert.id}>
              {/* Outer glow ring for severe/extreme */}
              {(alert.riskLevel === 'extreme' || alert.riskLevel === 'severe') && (
                <Circle
                  center={[alert.latitude, alert.longitude]}
                  radius={alert.radius_km * 1000 * 1.3}
                  pathOptions={{
                    color: cfg.color,
                    fillColor: cfg.fillColor,
                    fillOpacity: 0.05,
                    weight: 1,
                    dashArray: '8 4',
                  }}
                />
              )}
              {/* Primary alert zone */}
              <Circle
                center={[alert.latitude, alert.longitude]}
                radius={alert.radius_km * 1000}
                pathOptions={{
                  color: cfg.color,
                  fillColor: cfg.fillColor,
                  fillOpacity: cfg.fillOpacity,
                  weight: 2,
                }}
              >
                <Popup>
                  <div className="font-sans min-w-[200px]">
                    <div className="flex items-center gap-2 mb-2">
                      <span
                        className="flex items-center justify-center w-6 h-6 rounded text-white text-sm"
                        style={{ backgroundColor: cfg.color }}
                      >
                        {cfg.icon}
                      </span>
                      <div>
                        <span
                          className="text-xs font-bold uppercase tracking-wider"
                          style={{ color: cfg.color }}
                        >
                          {cfg.label} Risk
                        </span>
                        <h3 className="font-bold text-slate-800 text-sm leading-tight">
                          {alert.title}
                        </h3>
                      </div>
                    </div>
                    <p className="text-xs text-slate-600 mb-2">{alert.description}</p>
                    <div className="flex justify-between text-xs text-slate-500 border-t pt-2">
                      <span>Prob: <b>{(alert.probability * 100).toFixed(0)}%</b></span>
                      <span>{formatRelativeTime(alert.validUntil)}</span>
                    </div>
                  </div>
                </Popup>
              </Circle>
              {/* Center marker dot */}
              <Circle
                center={[alert.latitude, alert.longitude]}
                radius={5000}
                pathOptions={{
                  color: cfg.color,
                  fillColor: cfg.color,
                  fillOpacity: 0.9,
                  weight: 0,
                }}
              />
            </React.Fragment>
          );
        })}

        {/* ── Active Thunderstorm Cells ── */}
        {cells.map((cell: any) => (
          <CircleMarker
            key={cell.id}
            center={[cell.lat, cell.lon]}
            radius={6}
            pathOptions={{
              color: '#f97316',
              fillColor: '#fdba74',
              fillOpacity: 0.7,
              weight: 1,
            }}
          >
            <Popup>
              <div className="text-xs font-semibold">Thunderstorm Cell</div>
              <div className="text-[10px] text-gray-500">Intensity: {cell.intensity.toFixed(1)}</div>
            </Popup>
          </CircleMarker>
        ))}

        {/* ── Lightning Strokes ── */}
        {lightningStrokes.map((stroke: any) => (
          <CircleMarker
            key={stroke.id}
            center={[stroke.lat, stroke.lon]}
            radius={3}
            pathOptions={{
              color: stroke.type === 'CG' ? '#eab308' : '#3b82f6',
              fillColor: stroke.type === 'CG' ? '#fde047' : '#93c5fd',
              fillOpacity: 0.9,
              weight: 0,
            }}
          >
            <Popup>
              <div className="text-xs font-semibold">Lightning Stroke ({stroke.type})</div>
              <div className="text-[10px] text-gray-500">Time: {new Date(stroke.time).toLocaleTimeString()}</div>
            </Popup>
          </CircleMarker>
        ))}

        <MapUpdater cells={cells} alerts={visibleAlerts} />
        <CustomZoomControl />
      </MapContainer>

      {/* ── Risk Legend ── */}
      <div className="absolute bottom-4 right-4 z-[500] bg-nowcast-sidebar/90 backdrop-blur-md border border-nowcast-border rounded-lg p-3 shadow-lg">
        <div className="text-[10px] font-semibold text-nowcast-textMuted uppercase tracking-wider mb-2">
          Risk Levels
        </div>
        <div className="flex flex-col gap-1.5">
          {(['extreme', 'severe', 'high', 'moderate', 'low', 'minimal'] as RiskLevel[]).map((level) => {
            const cfg = RISK_LEVEL_CONFIG[level];
            const count = visibleAlerts.filter((a) => a.riskLevel === level).length;
            return (
              <div key={level} className="flex items-center gap-2 text-xs">
                <div
                  className="w-3 h-3 rounded-full border"
                  style={{ backgroundColor: cfg.fillColor, borderColor: cfg.color, opacity: 1 }}
                />
                <span className="text-nowcast-text font-medium">
                  {cfg.label}
                </span>
                {count > 0 && (
                  <span className={`ml-auto font-bold ${cfg.textClass}`}>{count}</span>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* ── Loading Overlay ── */}
      {loading && (
        <div className="absolute inset-0 z-[600] flex items-center justify-center bg-nowcast-bg/60 backdrop-blur-sm">
          <div className="rounded-lg bg-nowcast-sidebar p-4 shadow-xl border border-nowcast-border text-nowcast-text flex items-center gap-3">
            <div className="w-5 h-5 border-2 border-nowcast-accent border-t-transparent rounded-full animate-spin" />
            Connecting to Nowcast stream...
          </div>
        </div>
      )}
    </div>
  );
}

// ────────────────────────────────────────────────────────────────
//  Helpers
// ────────────────────────────────────────────────────────────────

/** Maps backend severity strings to the 4-tier risk enum. */
function mapSeverityToRisk(severity?: string): RiskLevel {
  switch (severity?.toUpperCase()) {
    case 'EXTREME':
      return 'extreme';
    case 'WARNING':
    case 'SEVERE':
      return 'severe';
    case 'WATCH':
      return 'high';
    case 'ADVISORY':
    case 'MODERATE':
      return 'moderate';
    case 'LOW':
      return 'low';
    default:
      return 'minimal';
  }
}
