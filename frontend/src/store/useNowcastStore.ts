import { create } from 'zustand';
import { type WeatherAlert } from '../types/nowcast';
import { getAlerts, getNowcast, getLightningRecent } from '../lib/api';

export type MapLayer = 'thunderstorm' | 'lightning' | 'composite' | 'observations';
export type OperationalMode = 'LIVE' | 'HISTORICAL_REPLAY' | 'OFFLINE_DEMO';

interface NowcastState {
  cells: any[];
  alerts: WeatherAlert[];
  radarScans: any[];
  lightningStrokes: any[];
  timestamp: string | null;
  selectedLayer: MapLayer;
  operationalMode: OperationalMode;
  replayEventId: string | null;
  replayBounds: [[number, number], [number, number]] | null;
  mapCenter: [number, number] | null;
  mapZoom: number | null;
  forecastMinute: number;
  isLoading: boolean;
  error: string | null;

  setNowcastData: (data: any) => void;
  setAlerts: (alerts: WeatherAlert[]) => void;
  setSelectedLayer: (layer: MapLayer) => void;
  setOperationalMode: (mode: OperationalMode) => void;
  loadHistoricalEvent: (eventData: any) => void;
  setMapCenter: (center: [number, number] | null, zoom?: number) => void;
  setForecastMinute: (minute: number) => void;

  fetchActiveAlerts: () => Promise<void>;
  fetchLatestNowcast: () => Promise<void>;
  fetchRadarAndLightning: () => Promise<void>;
}

export const useNowcastStore = create<NowcastState>((set, get) => ({
  cells: [],
  alerts: [],
  radarScans: [],
  lightningStrokes: [],
  timestamp: null,
  selectedLayer: 'thunderstorm',
  operationalMode: 'OFFLINE_DEMO',
  replayEventId: null,
  replayBounds: null,
  mapCenter: null,
  mapZoom: null,
  forecastMinute: 0,
  isLoading: false,
  error: null,

  setNowcastData: (data) => set({ cells: data.cells || [], timestamp: data.issued_at }),
  setAlerts: (alerts) => set({ alerts }),
  setSelectedLayer: (layer) => set({ selectedLayer: layer }),
  setOperationalMode: (mode) => set((state) => ({
    operationalMode: mode,
    ...(mode !== 'HISTORICAL_REPLAY' ? { replayEventId: null, replayBounds: null } : {}),
  })),
  loadHistoricalEvent: (eventData) => {
    const cells = eventData.cells || [];
    const syntheticAlerts = cells.map((c: any) => ({
      id: `alert-${c.cell_id}`,
      title: `${c.severity?.toUpperCase() || 'SEVERE'} Thunderstorm Warning`,
      description: `Historical benchmark storm cell ${c.cell_id} with peak reflectivity of ${c.max_dbz} dBZ.`,
      riskLevel: (c.severity || 'severe').toLowerCase(),
      latitude: c.center?.lat || 28.61,
      longitude: c.center?.lon || 77.23,
      radius_km: c.radius_km || 35,
      issuedAt: eventData.date || new Date().toISOString(),
      validUntil: new Date(Date.now() + 2 * 3600000).toISOString(),
      eventType: 'THUNDERSTORM',
      probability: c.probability || 0.9,
      polygon: c.polygon,
      imd_color: c.severity === 'extreme' ? 'RED' : 'ORANGE',
    }));
    const bounds: [[number, number], [number, number]] | null = eventData.bounds
      ? [
          [eventData.bounds.lat_min, eventData.bounds.lon_min],
          [eventData.bounds.lat_max, eventData.bounds.lon_max],
        ]
      : null;
    set({
      cells,
      alerts: syntheticAlerts,
      lightningStrokes: eventData.lightning_strokes || [],
      timestamp: eventData.date,
      operationalMode: 'HISTORICAL_REPLAY',
      replayEventId: eventData.event_id || null,
      replayBounds: bounds,
      forecastMinute: 0,
      mapCenter: eventData.center ? [eventData.center.lat, eventData.center.lon] : null,
      mapZoom: 8,
    });
  },
  setMapCenter: (center, zoom) => set((state) => ({
    mapCenter: center,
    mapZoom: zoom ?? state.mapZoom,
  })),
  setForecastMinute: (minute) => set({ forecastMinute: minute }),

  fetchActiveAlerts: async () => {
    set({ isLoading: true, error: null });
    try {
      const data = await getAlerts();
      if (data && Array.isArray(data.alerts)) {
        const formatted = data.alerts.map((a: any) => ({
          id: a.id || `alert-${Math.random().toString(36).substring(7)}`,
          title: a.title || 'Severe Weather Warning',
          description: a.description || a.message || 'Thunderstorm activity detected.',
          riskLevel: (a.riskLevel || a.severity || 'moderate').toLowerCase(),
          latitude: a.latitude ?? a.centroid_lat ?? 28.61,
          longitude: a.longitude ?? a.centroid_lon ?? 77.23,
          radius_km: a.radius_km || 40,
          issuedAt: a.issuedAt || a.issue_time || new Date().toISOString(),
          validUntil: a.validUntil || a.valid_until || new Date(Date.now() + 2 * 3600000).toISOString(),
          eventType: a.eventType || a.alert_type || 'THUNDERSTORM',
          probability: a.probability ?? 0.75,
          polygon: Array.isArray(a.polygon) ? a.polygon : undefined,
          imd_color: a.imd_color,
          impacts: Array.isArray(a.impacts) ? a.impacts : [],
        }));
        set({ alerts: formatted, isLoading: false, error: null });
      } else {
        set({ alerts: [], isLoading: false, error: null });
      }
    } catch (err: any) {
      set({ alerts: [], isLoading: false, error: 'Alert service unreachable' });
    }
  },

  fetchLatestNowcast: async () => {
    try {
      const data = await getNowcast();
      const isReal = data?.model?.checkpoint_loaded === true;
      const opMode: OperationalMode = isReal ? 'LIVE' : 'OFFLINE_DEMO';
      if (data && Array.isArray(data.cells)) {
        set((state) => ({
          cells: data.cells,
          timestamp: data.issued_at || new Date().toISOString(),
          operationalMode: state.operationalMode === 'HISTORICAL_REPLAY' ? 'HISTORICAL_REPLAY' : opMode,
          error: null,
        }));
      } else {
        set((state) => ({
          cells: [],
          timestamp: new Date().toISOString(),
          operationalMode: state.operationalMode === 'HISTORICAL_REPLAY' ? 'HISTORICAL_REPLAY' : opMode,
          error: null,
        }));
      }
    } catch (err: any) {
      set({ cells: [], error: 'Nowcast service unreachable' });
    }
  },

  fetchRadarAndLightning: async () => {
    try {
      const data = await getLightningRecent();
      if (data && Array.isArray(data.strokes)) {
        set({
          lightningStrokes: data.strokes,
          radarScans: [{ timestamp: new Date().toISOString(), url: '/mock-radar-1.png' }],
        });
      } else {
        set({
          lightningStrokes: [],
          radarScans: [{ timestamp: new Date().toISOString(), url: '/mock-radar-1.png' }],
        });
      }
    } catch {
      set({
        lightningStrokes: [],
        radarScans: [{ timestamp: new Date().toISOString(), url: '/mock-radar-1.png' }],
      });
    }
  },
}));
