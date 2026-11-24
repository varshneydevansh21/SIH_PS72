import React, { useEffect, useState, useMemo } from 'react';
import {
  MapContainer,
  TileLayer,
  Circle,
  Polygon,
  Popup,
  useMap,
  CircleMarker,
  Polyline,
  ImageOverlay,
} from 'react-leaflet';
import { useNowcastStore } from '../../store/useNowcastStore';
import {
  type WeatherAlert,
  type RiskLevel,
  RISK_LEVEL_CONFIG,
} from '../../types/nowcast';
import { AlertTriangle, Zap, CloudLightning, Plus, Minus } from 'lucide-react';

const MAP_CENTER = [28.6139, 77.2090] as [number, number];
const ZOOM = 7;

const DELHI_NCR_BOUNDS: [[number, number], [number, number]] = [
  [24.0, 72.0],
  [33.2, 82.5],
];

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

function formatRelativeTime(iso: string): string {
  const diff = new Date(iso).getTime() - Date.now();
  if (diff <= 0) return 'Expired';
  const minutes = Math.floor(diff / 60_000);
  if (minutes < 60) return `${minutes}m remaining`;
  const hours = Math.floor(minutes / 60);
  return `${hours}h ${minutes % 60}m remaining`;
}

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
      <button
        onClick={(e) => {
          e.preventDefault();
          map.zoomIn();
        }}
        className="p-2 hover:bg-nowcast-card transition-colors border-b border-nowcast-card"
      >
        <Plus className="w-4 h-4 text-nowcast-text" />
      </button>
      <button
        onClick={(e) => {
          e.preventDefault();
          map.zoomOut();
        }}
        className="p-2 hover:bg-nowcast-card transition-colors"
      >
        <Minus className="w-4 h-4 text-nowcast-text" />
      </button>
    </div>
  );
}

export function NowcastMap() {
  const { cells, alerts, lightningStrokes, forecastMinute, selectedLayer, timestamp } = useNowcastStore();
  const [loading, setLoading] = useState(true);
  const [dismissedAlerts] = useState<Set<string>>(new Set());

  useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 800);
    return () => clearTimeout(timer);
  }, []);

  const visibleAlerts = useMemo(
    () => alerts.filter((a) => !dismissedAlerts.has(a.id)),
    [alerts, dismissedAlerts],
  );

  const rasterUrl = useMemo(() => {
    const base = (import.meta as any).env?.VITE_API_BASE_URL || '/api/v1';
    return `${base}/nowcast/raster?minute=${forecastMinute}&layer=${selectedLayer}&ts=${encodeURIComponent(timestamp || '')}`;
  }, [forecastMinute, selectedLayer, timestamp]);

  const showLightning = selectedLayer === 'lightning' || selectedLayer === 'composite' || selectedLayer === 'observations';
  const showCells = selectedLayer === 'thunderstorm' || selectedLayer === 'composite' || selectedLayer === 'observations';

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

        {selectedLayer !== 'observations' && (
          <ImageOverlay
            url={rasterUrl}
            bounds={DELHI_NCR_BOUNDS}
            opacity={0.62}
            zIndex={200}
          />
        )}

        {visibleAlerts.map((alert) => {
          const cfg = RISK_LEVEL_CONFIG[alert.riskLevel] || RISK_LEVEL_CONFIG.moderate;
          const hasPolygon = Array.isArray(alert.polygon) && alert.polygon.length >= 3;
          const polygonPositions: [number, number][] = hasPolygon
            ? alert.polygon!.map(([lon, lat]) => [lat, lon])
            : [];

          return (
            <React.Fragment key={alert.id}>
              {hasPolygon ? (
                <Polygon
                  positions={polygonPositions}
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
                            {alert.imd_color ? `${alert.imd_color} ALERT` : `${cfg.label} Risk`}
                          </span>
                          <h3 className="font-bold text-slate-800 text-sm leading-tight">
                            {alert.title}
                          </h3>
                        </div>
                      </div>
                      <p className="text-xs text-slate-600 mb-2">{alert.description}</p>
                      {alert.impacts && alert.impacts.length > 0 && (
                        <div className="mb-2 p-1.5 bg-slate-50 rounded border border-slate-200">
                          <div className="text-[10px] font-bold text-slate-700 uppercase">Impact ETAs:</div>
                          {alert.impacts.slice(0, 2).map((imp: any, i: number) => (
                            <div key={i} className="text-[11px] text-slate-600 flex justify-between">
                              <span>{imp.location_name}:</span>
                              <b>{imp.eta_minutes} min ({imp.distance_km} km)</b>
                            </div>
                          ))}
                        </div>
                      )}
                      <div className="flex justify-between text-xs text-slate-500 border-t pt-2">
                        <span>Prob: <b>{(alert.probability * 100).toFixed(0)}%</b></span>
                        <span>{formatRelativeTime(alert.validUntil)}</span>
                      </div>
                    </div>
                  </Popup>
                </Polygon>
              ) : (
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
                            {alert.imd_color ? `${alert.imd_color} ALERT` : `${cfg.label} Risk`}
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
              )}
            </React.Fragment>
          );
        })}

        {showCells &&
          cells.map((cell: any) => {
            let cLat = cell.center?.lat ?? cell.lat ?? 28.61;
            let cLon = cell.center?.lon ?? cell.lon ?? 77.23;
            let currentProb = cell.probability ?? 0.8;
            const initialLat = cell.center?.lat ?? cell.lat ?? 28.61;
            const initialLon = cell.center?.lon ?? cell.lon ?? 77.23;
            const cellKey = cell.cell_id ?? cell.id ?? String(cLat + cLon);
            const intensity = cell.intensity ?? cell.max_reflectivity_dbz ?? cell.max_dbz ?? 42.0;

            if (forecastMinute > 0 && Array.isArray(cell.forecast_positions)) {
              const match = cell.forecast_positions.find((fp: any) => fp.minutes_ahead === forecastMinute);
              if (match) {
                cLat = match.lat;
                cLon = match.lon;
                if (typeof match.probability === 'number') {
                  currentProb = match.probability;
                }
              }
            }

            const dLat = cLat - initialLat;
            const dLon = cLon - initialLon;
            const hasCellPolygon = Array.isArray(cell.polygon) && cell.polygon.length >= 3;
            const shiftedPolygon: [number, number][] = hasCellPolygon
              ? cell.polygon.map(([lon, lat]: [number, number]) => [lat + dLat, lon + dLon] as [number, number])
              : [];

            return (
              <React.Fragment key={cellKey}>
                {hasCellPolygon && (
                  <Polygon
                    positions={shiftedPolygon}
                    pathOptions={{
                      color: '#ea580c',
                      fillColor: '#f97316',
                      fillOpacity: Math.max(0.12, 0.30 * (currentProb / 0.8)),
                      weight: 2,
                    }}
                  />
                )}
                {Array.isArray(cell.forecast_positions) && cell.forecast_positions.length > 0 && (
                  <Polyline
                    positions={[
                      [initialLat, initialLon],
                      ...cell.forecast_positions.map((p: any) => [p.lat, p.lon]),
                    ]}
                    pathOptions={{
                      color: '#f97316',
                      weight: 2,
                      dashArray: '5 5',
                      opacity: 0.7,
                    }}
                  />
                )}
                <CircleMarker
                  center={[cLat, cLon]}
                  radius={7}
                  pathOptions={{
                    color: '#ea580c',
                    fillColor: '#f97316',
                    fillOpacity: 0.9,
                    weight: 2,
                  }}
                >
                  <Popup>
                    <div className="font-sans min-w-[160px]">
                      <div className="text-xs font-bold text-slate-800">
                        Thunderstorm Cell ({cell.cell_id ?? cell.id ?? 'Active'})
                      </div>
                      <div className="text-[10px] text-gray-600 mt-1">
                        Position at: <b>{forecastMinute === 0 ? 'T = 0 (Live)' : `T + ${forecastMinute} min`}</b>
                      </div>
                      <div className="text-[10px] text-gray-600">
                        Coordinates: {cLat.toFixed(2)}°N, {cLon.toFixed(2)}°E
                      </div>
                      <div className="text-[10px] text-gray-600">
                        Reflectivity: {typeof intensity === 'number' ? intensity.toFixed(1) : intensity} dBZ
                      </div>
                      <div className="text-[10px] text-gray-600">
                        Probability: <b>{(currentProb * 100).toFixed(0)}%</b>
                      </div>
                      {cell.severity && (
                        <div className="text-[10px] font-bold text-orange-600 uppercase mt-1">
                          Severity: {cell.severity}
                        </div>
                      )}
                    </div>
                  </Popup>
                </CircleMarker>
              </React.Fragment>
            );
          })}

        {showLightning &&
          lightningStrokes.map((stroke: any) => (
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
                <div className="text-[10px] text-gray-500">
                  Time: {new Date(stroke.time || stroke.timestamp).toLocaleTimeString()}
                </div>
              </Popup>
            </CircleMarker>
          ))}

        <MapUpdater cells={cells} alerts={visibleAlerts} />
        <CustomZoomControl />
      </MapContainer>

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
                <span className="text-nowcast-text font-medium">{cfg.label}</span>
                {count > 0 && <span className={`ml-auto font-bold ${cfg.textClass}`}>{count}</span>}
              </div>
            );
          })}
        </div>
      </div>

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
