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
    
    // Prototype Hardcoded Data
    const mockAlerts: WeatherAlert[] = [
      { id: 'alert-1', title: 'Severe Thunderstorm Warning', description: 'Intense thunderstorm activity detected.', riskLevel: 'severe', latitude: 28.6139, longitude: 77.2090, radius_km: 60, issuedAt: new Date().toISOString(), validUntil: new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString(), eventType: 'THUNDERSTORM', probability: 0.85 },
      { id: 'alert-2', title: 'Extreme Lightning Risk', description: 'Frequent cloud-to-ground lightning.', riskLevel: 'extreme', latitude: 22.5726, longitude: 88.3639, radius_km: 45, issuedAt: new Date().toISOString(), validUntil: new Date(Date.now() + 1 * 60 * 60 * 1000).toISOString(), eventType: 'EXTREME_LIGHTNING', probability: 0.95 },
      { id: 'alert-3', title: 'Moderate Squall Alert', description: 'Squally winds reaching 40-50 kmph.', riskLevel: 'moderate', latitude: 19.0760, longitude: 72.8777, radius_km: 80, issuedAt: new Date().toISOString(), validUntil: new Date(Date.now() + 3 * 60 * 60 * 1000).toISOString(), eventType: 'SQUALL', probability: 0.45 },
      { id: 'alert-4', title: 'High Hailstorm Risk', description: 'Hailstones up to 2cm expected.', riskLevel: 'high', latitude: 13.0827, longitude: 80.2707, radius_km: 50, issuedAt: new Date().toISOString(), validUntil: new Date(Date.now() + 1.5 * 60 * 60 * 1000).toISOString(), eventType: 'HAILSTORM', probability: 0.65 },
      { id: 'alert-5', title: 'Severe Cloudburst Warning', description: 'Heavy precipitation over short duration.', riskLevel: 'severe', latitude: 31.1048, longitude: 77.1734, radius_km: 30, issuedAt: new Date().toISOString(), validUntil: new Date(Date.now() + 4 * 60 * 60 * 1000).toISOString(), eventType: 'THUNDERSTORM', probability: 0.88 },
      { id: 'alert-6', title: 'Low Wind Alert', description: 'Gusty winds in isolated pockets.', riskLevel: 'low', latitude: 23.0225, longitude: 72.5714, radius_km: 100, issuedAt: new Date().toISOString(), validUntil: new Date(Date.now() + 5 * 60 * 60 * 1000).toISOString(), eventType: 'SQUALL', probability: 0.25 },
      { id: 'alert-7', title: 'Extreme Rainfall', description: 'Continuous extreme rainfall.', riskLevel: 'extreme', latitude: 9.9312, longitude: 76.2673, radius_km: 70, issuedAt: new Date().toISOString(), validUntil: new Date(Date.now() + 12 * 60 * 60 * 1000).toISOString(), eventType: 'THUNDERSTORM', probability: 0.99 },
      { id: 'alert-8', title: 'Moderate Heatwave', description: 'Temperatures 4-5 degrees above normal.', riskLevel: 'moderate', latitude: 26.9124, longitude: 75.7873, radius_km: 120, issuedAt: new Date().toISOString(), validUntil: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(), eventType: 'THUNDERSTORM', probability: 0.70 },
      { id: 'alert-9', title: 'Severe Dust Storm', description: 'Visibility reduced to less than 500m.', riskLevel: 'severe', latitude: 28.0229, longitude: 73.3119, radius_km: 150, issuedAt: new Date().toISOString(), validUntil: new Date(Date.now() + 3 * 60 * 60 * 1000).toISOString(), eventType: 'SQUALL', probability: 0.80 },
      { id: 'alert-10', title: 'High Cyclone Watch', description: 'Deep depression intensifying.', riskLevel: 'high', latitude: 17.6868, longitude: 83.2185, radius_km: 200, issuedAt: new Date().toISOString(), validUntil: new Date(Date.now() + 48 * 60 * 60 * 1000).toISOString(), eventType: 'THUNDERSTORM', probability: 0.60 },
      { id: 'alert-11', title: 'Severe Lightning', description: 'Continuous lightning activity.', riskLevel: 'severe', latitude: 12.9716, longitude: 77.5946, radius_km: 40, issuedAt: new Date().toISOString(), validUntil: new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString(), eventType: 'EXTREME_LIGHTNING', probability: 0.90 },
      { id: 'alert-12', title: 'Extreme Cloudburst', description: 'Imminent extreme precipitation.', riskLevel: 'extreme', latitude: 30.3165, longitude: 78.0322, radius_km: 30, issuedAt: new Date().toISOString(), validUntil: new Date(Date.now() + 3 * 60 * 60 * 1000).toISOString(), eventType: 'THUNDERSTORM', probability: 0.98 }
    ];

    set({ alerts: mockAlerts, isLoading: false });
  },

  fetchLatestNowcast: async () => {
    // Generate ~42 cells randomly over India (Lat: 8 to 33, Lon: 68 to 90)
    const mockCells = Array.from({ length: 42 }).map((_, i) => ({
      id: `cell-${i}`,
      lat: 8 + Math.random() * 25,
      lon: 68 + Math.random() * 22,
      intensity: 30 + Math.random() * 60
    }));
    set({ cells: mockCells, timestamp: new Date().toISOString() });
  },

  fetchRadarAndLightning: async () => {
    const mockRadarScans = [
      { timestamp: new Date().toISOString(), url: '/mock-radar-1.png' }
    ];
    
    // Generate ~187 lightning strokes randomly over India
    const mockLightningStrokes = Array.from({ length: 187 }).map((_, i) => ({
      id: `ls-${i}`,
      lat: 8 + Math.random() * 25,
      lon: 68 + Math.random() * 22,
      time: new Date().toISOString(),
      type: Math.random() > 0.5 ? 'CG' : 'IC'
    }));
    
    set({ 
      radarScans: mockRadarScans, 
      lightningStrokes: mockLightningStrokes 
    });
  }
}));
