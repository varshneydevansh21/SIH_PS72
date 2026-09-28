import React, { useState } from 'react';
import { Search, ChevronDown, Bell, User } from 'lucide-react';
import { LOCATIONS_DB, INDIA_REGIONS, LocationRecord } from '../lib/locations';
import { useNowcastStore } from '../store/useNowcastStore';

export function Topbar() {
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearchFocused, setIsSearchFocused] = useState(false);
  const [selectedRegion, setSelectedRegion] = useState('all');
  const setMapCenter = useNowcastStore(state => state.setMapCenter);
  const alerts = useNowcastStore(state => state.alerts);
  
  const hasHighRiskAlerts = alerts.some(alert => ['high', 'severe', 'extreme'].includes(alert.riskLevel));
  
  const handleLocationSelect = async (loc: LocationRecord) => {
    setSearchQuery(loc.name);
    setIsSearchFocused(false);
    
    try {
      // Query accurate coordinates for the selected location
      const res = await fetch(`https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(loc.name)}&count=1`);
      const data = await res.json();
      if (data.results && data.results.length > 0) {
        setMapCenter([data.results[0].latitude, data.results[0].longitude], 10);
      } else {
        // Fallback to local DB if no results
        setMapCenter([loc.lat, loc.lng], 10);
      }
    } catch (e) {
      console.error("Geocoding failed, falling back to local DB");
      setMapCenter([loc.lat, loc.lng], 10);
    }
  };
  
  const filteredLocations = searchQuery.length >= 2 
    ? LOCATIONS_DB.filter(loc => 
        loc.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        loc.state.toLowerCase().includes(searchQuery.toLowerCase())
      ).slice(0, 8)
    : [];

  return (
    <header className="h-16 border-b border-nowcast-card bg-nowcast-bg flex items-center justify-between px-6 shrink-0">
      <div className="flex items-center gap-4 flex-1">
        <div className="relative w-72">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-nowcast-textMuted" />
          <input 
            type="text" 
            placeholder="Search location (city, district, state)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onFocus={() => setIsSearchFocused(true)}
            onBlur={() => setTimeout(() => setIsSearchFocused(false), 200)}
            className="w-full bg-nowcast-card border border-nowcast-card rounded-md py-1.5 pl-9 pr-4 text-sm text-nowcast-text placeholder:text-nowcast-textMuted focus:outline-none focus:border-nowcast-accent/50 transition-colors"
          />
          {isSearchFocused && filteredLocations.length > 0 && (
            <div className="absolute top-full left-0 right-0 mt-1 bg-nowcast-bg border border-nowcast-card rounded-md shadow-xl z-50 max-h-64 overflow-y-auto">
              {filteredLocations.map(loc => (
                <div key={loc.id} onMouseDown={() => handleLocationSelect(loc)} className="px-4 py-2 hover:bg-nowcast-card cursor-pointer flex flex-col border-b border-nowcast-card/30 last:border-0">
                  <span className="text-sm font-medium text-nowcast-text">{loc.name}</span>
                  <span className="text-xs text-nowcast-textMuted">{loc.state} • {loc.type}</span>
                </div>
              ))}
            </div>
          )}
          {isSearchFocused && searchQuery.length >= 2 && filteredLocations.length === 0 && (
            <div className="absolute top-full left-0 right-0 mt-1 bg-nowcast-bg border border-nowcast-card rounded-md shadow-xl z-50 px-4 py-3 text-sm text-nowcast-textMuted text-center">
              No registered location found
            </div>
          )}
        </div>
        
        <div className="relative">
          <select 
            value={selectedRegion}
            onChange={(e) => setSelectedRegion(e.target.value)}
            className="appearance-none bg-nowcast-card border border-nowcast-card rounded-md pl-3 pr-8 py-1.5 text-sm text-nowcast-text focus:outline-none focus:border-nowcast-accent/50 transition-colors cursor-pointer"
          >
            {INDIA_REGIONS.map(region => (
              <option key={region.id} value={region.id}>{region.name}</option>
            ))}
          </select>
          <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 text-nowcast-textMuted pointer-events-none" />
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="text-sm text-nowcast-textMuted">
          {new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })}, {new Date().toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', timeZoneName: 'short' })}
        </div>
        
        <div className="flex items-center gap-2 px-3 py-1 bg-nowcast-success/10 border border-nowcast-success/20 rounded-full">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-nowcast-success opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-nowcast-success"></span>
          </span>
          <span className="text-xs font-medium text-nowcast-success">Live</span>
        </div>
        
        <button className="relative p-2 rounded-full hover:bg-nowcast-card transition-colors">
          <Bell className="w-5 h-5 text-nowcast-textMuted" />
          <span className={`absolute top-1.5 right-1.5 w-2 h-2 rounded-full border border-nowcast-bg ${hasHighRiskAlerts ? 'bg-nowcast-danger animate-pulse' : 'bg-nowcast-success'}`}></span>
        </button>
        
        <div className="w-8 h-8 rounded-full bg-nowcast-accent/20 flex items-center justify-center border border-nowcast-accent/30 text-nowcast-accent font-medium text-sm">
          ST
        </div>
      </div>
    </header>
  );
}
