import { create } from 'zustand';
import { type WeatherAlert } from '../types/nowcast';
import { getAlerts, getNowcast, getLightningRecent } from '../lib/api';

export type MapLayer = 'thunderstorm' | 'lightning' | 'composite' | 'observations';

interface NowcastState {
  cells: any[];
  alerts: WeatherAlert[];
  radarScans: any[];
  lightningStrokes: any[];
  timestamp: string | null;
  selectedLayer: MapLayer;
  mapCenter: [number, number] | null;
  mapZoom: number | null;
  forecastMinute: number;
  isLoading: boolean;
  error: string | null;

  setNowcastData: (data: any) => void;
  setAlerts: (alerts: WeatherAlert[]) => void;
  setSelectedLayer: (layer: MapLayer) => void;
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
  mapCenter: null,
  mapZoom: null,
  forecastMinute: 0,
  isLoading: false,
  error: null,

  setNowcastData: (data) => set({ cells: data.cells || [], timestamp: data.issued_at }),
  setAlerts: (alerts) => set({ alerts }),
  setSelectedLayer: (layer) => set({ selectedLayer: layer }),
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
      if (data && Array.isArray(data.cells)) {
        set({
          cells: data.cells,
          timestamp: data.issued_at || new Date().toISOString(),
          error: null,
        });
      } else {
        set({ cells: [], timestamp: new Date().toISOString(), error: null });
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
