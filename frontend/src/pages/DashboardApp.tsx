import React, { useState } from 'react';
import { Sidebar } from '../components/Sidebar';
import { Topbar } from '../components/Topbar';
import { DashboardView } from '../components/Dashboard/DashboardView';
import { ForecastTimelineView } from '../components/Dashboard/ForecastTimelineView';
import { AnalyticsPage } from '../components/Pages/AnalyticsPage';
import { ObservationsPage } from '../components/Pages/ObservationsPage';
import { AlertsPage } from '../components/Pages/AlertsPage';
import { ReplayPage } from '../components/Pages/ReplayPage';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  return (
    <div className="flex h-screen w-full bg-nowcast-bg overflow-hidden text-nowcast-text font-sans">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      <div className="flex flex-col flex-1 h-full min-w-0">
        <Topbar />
        <main className="flex-1 overflow-hidden relative">
          {(activeTab === 'dashboard' || activeTab === 'nowcast') && <DashboardView />}
          {activeTab === 'observations' && <ObservationsPage />}
          {activeTab === 'timeline' && <ForecastTimelineView />}
          {activeTab === 'alerts' && <AlertsPage />}
          {activeTab === 'analytics' && <AnalyticsPage />}
          {activeTab === 'replay' && <ReplayPage />}
          {activeTab === 'settings' && (
            <div className="p-8 flex flex-col gap-4 text-nowcast-text">
              <h2 className="text-lg font-bold">System Configuration</h2>
              <div className="bg-nowcast-sidebar p-4 rounded-xl border border-nowcast-card max-w-lg flex flex-col gap-3 text-xs">
                <div className="flex justify-between">
                  <span className="text-nowcast-textMuted">Backend API URL:</span>
                  <span className="font-mono text-nowcast-accent">http://localhost:8001</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-nowcast-textMuted">Model Architecture:</span>
                  <span className="font-mono text-nowcast-text">PyTorch UNet-ConvLSTM</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-nowcast-textMuted">Spatial Grid:</span>
                  <span className="font-mono text-nowcast-text">2 km (512x512)</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-nowcast-textMuted">Lead Time Horizon:</span>
                  <span className="font-mono text-nowcast-text">120 Minutes (8 Steps)</span>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
