import { create } from 'zustand';
import { type WeatherAlert } from '../types/nowcast';

export type MapLayer = 'thunderstorm' | 'lightning' | 'composite' | 'observations';

const API_URL = 'http://localhost:8001';

interface NowcastState {
  cells: any[];
  alerts: WeatherAlert[];
  radarScans: any[];
  lightningStrokes: any[];
  timestamp: string | null;
  selectedLayer: MapLayer;
  mapCenter: [number, number] | null;
  mapZoom: number | null;
  isLoading: boolean;
  error: string | null;
  
  setNowcastData: (data: any) => void;
  setAlerts: (alerts: WeatherAlert[]) => void;
  setSelectedLayer: (layer: MapLayer) => void;
  setMapCenter: (center: [number, number] | null, zoom?: number) => void;

  // Async API Actions
  fetchActiveAlerts: () => Promise<void>;
  fetchLatestNowcast: () => Promise<void>;
  fetchRadarAndLightning: () => Promise<void>;
}

export const useNowcastStore = create<NowcastState>((set) => ({
  cells: [],
  alerts: [],
  radarScans: [],
  lightningStrokes: [],
  timestamp: null,
  selectedLayer: 'thunderstorm',
  mapCenter: null,
  mapZoom: null,
  isLoading: false,
  error: null,
  
  setNowcastData: (data) => set({ cells: data.cells, timestamp: data.issued_at }),
  setAlerts: (alerts) => set({ alerts }),
  setSelectedLayer: (layer) => set({ selectedLayer: layer }),
  setMapCenter: (center, zoom) => set((state) => ({ 
    mapCenter: center, 
    mapZoom: zoom ?? state.mapZoom 
  })),

  fetchActiveAlerts: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await fetch(`${API_URL}/alerts`);
      if (!response.ok) throw new Error('Failed to fetch alerts');
      const data = await response.json();
      
      // Map backend Alert model to frontend WeatherAlert type
      const mappedAlerts: WeatherAlert[] = data.alerts.map((a: any) => ({
        id: a.id,
        title: `${a.alert_type} Warning`,
        description: a.message,
        riskLevel: a.severity.toLowerCase(),
        latitude: a.centroid_lat ?? 20.0,
        longitude: a.centroid_lon ?? 80.0,
        radius_km: 50,
        issuedAt: a.issue_time,
        validUntil: a.valid_until,
        eventType: a.alert_type,
        probability: 0.8, // default or extract from nowcast relation
      }));

      set({ alerts: mappedAlerts, isLoading: false });
    } catch (error: any) {
      console.error(error);
      set({ error: error.message, isLoading: false });
    }
  },

  fetchLatestNowcast: async () => {
    try {
      const response = await fetch(`${API_URL}/nowcast`);
      if (!response.ok) throw new Error('Failed to fetch nowcasts');
      const data = await response.json();
      set({ cells: data.nowcasts, timestamp: new Date().toISOString() });
    } catch (error) {
      console.error(error);
    }
  },

  fetchRadarAndLightning: async () => {
    try {
      const [radarRes, lightRes] = await Promise.all([
        fetch(`${API_URL}/radar/latest`),
        fetch(`${API_URL}/lightning/recent?minutes=30`)
      ]);
      
      const radarData = await radarRes.json();
      const lightData = await lightRes.json();
      
      set({ 
        radarScans: radarData.scans || [], 
        lightningStrokes: lightData.strokes || [] 
      });
    } catch (error) {
      console.error(error);
    }
  }
}));
