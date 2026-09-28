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
      {
        id: 'alert-1',
        title: 'Severe Thunderstorm Warning',
        description: 'Intense thunderstorm activity detected. Heavy rainfall and strong winds expected.',
        riskLevel: 'severe',
        latitude: 28.6139,
        longitude: 77.2090, // Delhi
        radius_km: 60,
        issuedAt: new Date().toISOString(),
        validUntil: new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString(),
        eventType: 'THUNDERSTORM',
        probability: 0.85,
      },
      {
        id: 'alert-2',
        title: 'Extreme Lightning Risk',
        description: 'Frequent cloud-to-ground lightning strikes observed.',
        riskLevel: 'extreme',
        latitude: 22.5726,
        longitude: 88.3639, // Kolkata
        radius_km: 45,
        issuedAt: new Date().toISOString(),
        validUntil: new Date(Date.now() + 1 * 60 * 60 * 1000).toISOString(),
        eventType: 'EXTREME_LIGHTNING',
        probability: 0.95,
      },
      {
        id: 'alert-3',
        title: 'Moderate Squall Alert',
        description: 'Squally winds reaching 40-50 kmph likely.',
        riskLevel: 'moderate',
        latitude: 19.0760,
        longitude: 72.8777, // Mumbai
        radius_km: 80,
        issuedAt: new Date().toISOString(),
        validUntil: new Date(Date.now() + 3 * 60 * 60 * 1000).toISOString(),
        eventType: 'SQUALL',
        probability: 0.45,
      }
    ];

    set({ alerts: mockAlerts, isLoading: false });
  },

  fetchLatestNowcast: async () => {
    // Prototype Hardcoded Data
    const mockCells = [
      { id: 'cell-1', lat: 28.61, lon: 77.20, intensity: 55 },
      { id: 'cell-2', lat: 22.57, lon: 88.36, intensity: 65 },
      { id: 'cell-3', lat: 19.07, lon: 72.87, intensity: 45 },
      { id: 'cell-4', lat: 13.08, lon: 80.27, intensity: 50 },
      { id: 'cell-5', lat: 26.84, lon: 80.94, intensity: 60 }
    ];
    set({ cells: mockCells, timestamp: new Date().toISOString() });
  },

  fetchRadarAndLightning: async () => {
    // Prototype Hardcoded Data
    const mockRadarScans = [
      { timestamp: new Date().toISOString(), url: '/mock-radar-1.png' }
    ];
    const mockLightningStrokes = [
      { id: 'ls-1', lat: 28.62, lon: 77.21, time: new Date().toISOString(), type: 'CG' },
      { id: 'ls-2', lat: 28.60, lon: 77.19, time: new Date().toISOString(), type: 'CG' },
      { id: 'ls-3', lat: 22.58, lon: 88.37, time: new Date().toISOString(), type: 'IC' },
      { id: 'ls-4', lat: 22.56, lon: 88.35, time: new Date().toISOString(), type: 'CG' },
      { id: 'ls-5', lat: 13.09, lon: 80.28, time: new Date().toISOString(), type: 'CG' },
      { id: 'ls-6', lat: 19.08, lon: 72.88, time: new Date().toISOString(), type: 'IC' },
      { id: 'ls-7', lat: 26.85, lon: 80.95, time: new Date().toISOString(), type: 'CG' },
    ];
    
    set({ 
      radarScans: mockRadarScans, 
      lightningStrokes: mockLightningStrokes 
    });
  }
}));
