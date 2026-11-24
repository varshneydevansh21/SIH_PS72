/** Risk levels for weather alerts, ordered by severity. */
export type RiskLevel = 'minimal' | 'low' | 'moderate' | 'high' | 'severe' | 'extreme';

/** A single weather warning alert with geolocation and risk classification. */
export interface WeatherAlert {
  id: string;
  title: string;
  description: string;
  riskLevel: RiskLevel;
  latitude: number;
  longitude: number;
  radius_km: number;
  issuedAt: string;
  validUntil: string;
  eventType: 'THUNDERSTORM' | 'EXTREME_LIGHTNING' | 'HAILSTORM' | 'SQUALL';
  probability: number;
  polygon?: [number, number][];
  imd_color?: string;
  impacts?: Array<{
    location_name: string;
    district: string;
    distance_km: number;
    eta_minutes: number;
    warning_text: string;
  }>;
}

/** Visual configuration for each risk level. */
export interface RiskLevelConfig {
  label: string;
  color: string;
  fillColor: string;
  fillOpacity: number;
  icon: string;
  bgClass: string;
  textClass: string;
  borderClass: string;
}

/** Map from risk level to its visual config. */
export const RISK_LEVEL_CONFIG: Record<RiskLevel, RiskLevelConfig> = {
  minimal: {
    label: 'Minimal (0-15%)',
    color: '#00E676',
    fillColor: '#00E676',
    fillOpacity: 0.1,
    icon: '✓',
    bgClass: 'bg-[#00E676]/10',
    textClass: 'text-[#00E676]',
    borderClass: 'border-[#00E676]/30',
  },
  low: {
    label: 'Low (15-30%)',
    color: '#81C784',
    fillColor: '#81C784',
    fillOpacity: 0.15,
    icon: '⚠',
    bgClass: 'bg-[#81C784]/10',
    textClass: 'text-[#81C784]',
    borderClass: 'border-[#81C784]/30',
  },
  moderate: {
    label: 'Moderate (30-50%)',
    color: '#FFAA00',
    fillColor: '#FFAA00',
    fillOpacity: 0.2,
    icon: '⚠',
    bgClass: 'bg-[#FFAA00]/10',
    textClass: 'text-[#FFAA00]',
    borderClass: 'border-[#FFAA00]/30',
  },
  high: {
    label: 'High (50-70%)',
    color: '#FF6D00',
    fillColor: '#FF6D00',
    fillOpacity: 0.3,
    icon: '⚡',
    bgClass: 'bg-[#FF6D00]/10',
    textClass: 'text-[#FF6D00]',
    borderClass: 'border-[#FF6D00]/30',
  },
  severe: {
    label: 'Severe (70-90%)',
    color: '#FF1744',
    fillColor: '#FF1744',
    fillOpacity: 0.4,
    icon: '🔴',
    bgClass: 'bg-[#FF1744]/10',
    textClass: 'text-[#FF1744]',
    borderClass: 'border-[#FF1744]/30',
  },
  extreme: {
    label: 'Extreme (>90%)',
    color: '#D50000',
    fillColor: '#D50000',
    fillOpacity: 0.5,
    icon: '💀',
    bgClass: 'bg-[#D50000]/10',
    textClass: 'text-[#D50000]',
    borderClass: 'border-[#D50000]/30',
  },
};
