export interface RadarStation {
  id: string;
  name: string;
  lat: number;
  lon: number;
  band: 'S' | 'C' | 'X';
  rangeKm: number;
  status: 'operational' | 'maintenance' | 'offline';
}

export interface RadarScanMetadata {
  id: string;
  stationId: string;
  timestamp: string;
  maxReflectivityDbz: number;
  elevationAngleDeg: number;
  tileUrl?: string;
}

export interface RadarColorScaleStep {
  dbz: number;
  color: string;
  label: string;
}

export const RADAR_COLOR_SCALE: RadarColorScaleStep[] = [
  { dbz: 0, color: '#000000', label: '< 10 dBZ (Light/None)' },
  { dbz: 15, color: '#04E9E7', label: '15 dBZ (Very Light Rain)' },
  { dbz: 25, color: '#019FF4', label: '25 dBZ (Light Rain)' },
  { dbz: 35, color: '#0300F4', label: '35 dBZ (Moderate Rain)' },
  { dbz: 40, color: '#02FD02', label: '40 dBZ (Heavy Rain)' },
  { dbz: 45, color: '#01C501', label: '45 dBZ (Thunderstorm)' },
  { dbz: 50, color: '#008E00', label: '50 dBZ (Severe Storm)' },
  { dbz: 55, color: '#FDF802', label: '55 dBZ (Hail Risk)' },
  { dbz: 60, color: '#E5BC00', label: '60 dBZ (Large Hail)' },
  { dbz: 65, color: '#FD0000', label: '65 dBZ (Extreme Storm)' },
  { dbz: 70, color: '#D40000', label: '70+ dBZ (Violent Tornado/Hail)' },
];
