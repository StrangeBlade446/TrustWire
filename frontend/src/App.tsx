import React, { useState, useEffect } from 'react';
import {
  Shield,  Activity,

  Clock,
  Cpu,
  Lock,
  Info,
  Layers,
  AlertTriangle,
  Bell,
  CheckCircle2,
  HardDrive
} from 'lucide-react';
import { Dashboard } from './views/Dashboard';
import { LiveMonitoring } from './views/LiveMonitoring';
import { AnalyzeMedia } from './views/AnalyzeMedia';
import { AlertHistory } from './views/AlertHistory';
import { ModelsPerformance } from './views/ModelsPerformance';
import { PrivacySettings } from './views/PrivacySettings';
import { About } from './views/About';
import { LiveMonitoringOverlay } from './components/LiveMonitoringOverlay';
import { DisparityAlertPopup } from './components/DisparityAlertPopup';
import { api } from './services/api';
import { MonitoringStatus, AlertItem } from './types';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [monitoringStatus, setMonitoringStatus] = useState<MonitoringStatus | null>(null);
  const [incomingAlert, setIncomingAlert] = useState<AlertItem | null>(null);

  // Poll basic monitoring state
  useEffect(() => {
    // Initial health check to fetch token
    api.getHealth().catch(() => {});

    const fetchStatus = () => {
      api.getMonitoringStatus()
        .then(setMonitoringStatus)
        .catch(() => {});
    };
    fetchStatus();
    const interval = setInterval(fetchStatus, 3000);
    return () => clearInterval(interval);
  }, []);

  // Real-time WebSocket connection
  useEffect(() => {
    let ws: WebSocket | null = null;
    let reconnectTimeout: any = null;

    const connectWs = () => {
      try {
        const socket = new WebSocket('ws://127.0.0.1:8765/api/ws');
        ws = socket;
        socket.onopen = () => {
          // Send ping every 2 seconds
          const pingInterval = setInterval(() => {
            if (socket.readyState === WebSocket.OPEN) {
              socket.send('ping');
            }
          }, 2000);
          socket.addEventListener('close', () => clearInterval(pingInterval));
        };
        ws.onmessage = (event) => {
          try {
            const msg = JSON.parse(event.data);
            if (msg.type === 'NEW_ALERT' && msg.alert) {
              // Only show the popup for live monitoring alerts — not media analysis uploads.
              // Media analysis results are shown inline in the AnalyzeMedia view.
              if (msg.alert.source === 'Live Monitoring') {
                setIncomingAlert(msg.alert);
                const desktop = (window as any).trustwireDesktop;
                if (desktop?.sendAlert) {
                  desktop.sendAlert(msg.alert);
                }
              }
            } else if (msg.type === 'PONG' && msg.monitoring) {
              setMonitoringStatus(msg.monitoring);
            }
          } catch (e) {}
        };
        ws.onclose = () => {
          reconnectTimeout = setTimeout(connectWs, 3000);
        };
      } catch (err) {
        reconnectTimeout = setTimeout(connectWs, 3000);
      }
    };

    connectWs();
    return () => {
      if (ws) ws.close();
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
    };
  }, []);

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Shield },
    { id: 'monitoring', label: 'Live Monitoring', icon: Activity, badge: monitoringStatus?.is_monitoring ? 'LIVE' : null },
    { id: 'analyze', label: 'Analyse Media', icon: Layers },
    { id: 'alerts', label: 'Alert History', icon: Bell },
    { id: 'models', label: 'Models & Speed', icon: Cpu },
    { id: 'privacy', label: 'Privacy & 15m Policy', icon: Lock },
    { id: 'about', label: 'About & Licenses', icon: Info },
  ];

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-background text-gray-200 relative">
      {/* Floating Top Screen Overlay Bar */}
      <LiveMonitoringOverlay
        monitoringStatus={monitoringStatus}
        onStatusChange={setMonitoringStatus}
        onNavigateToMonitoring={() => setActiveTab('monitoring')}
      />

      {/* Sleek Dark Sidebar */}
      <aside className="w-64 border-r border-border bg-surface flex flex-col justify-between flex-shrink-0">
        <div>
          {/* Logo & Product Name */}
          <div className="p-6 border-b border-border/60 flex items-center gap-3">
            <div className="p-2 rounded-xl bg-teal-500/10 border border-teal-500/20 text-teal-400">
              <Shield className="w-5 h-5" />
            </div>
            <div>
              <div className="font-bold text-base text-white tracking-tight flex items-center gap-1.5">
                Trustwire
                <span className="text-[10px] px-1.5 py-0.2 rounded font-mono bg-teal-500/20 text-teal-300 font-semibold">v1.0</span>
              </div>
              <div className="text-[10px] text-gray-400 font-mono">Deception Defense</div>
            </div>
          </div>

          {/* Nav Items */}
          <nav className="p-3 space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-medium transition-all ${
                    isActive
                      ? 'bg-teal-500/10 text-teal-300 font-semibold border border-teal-500/20'
                      : 'text-gray-400 hover:text-white hover:bg-panel'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon className={`w-4 h-4 ${isActive ? 'text-teal-400' : 'text-gray-400'}`} />
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-rose-500 text-white animate-pulse">
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Bottom Hardware Status Strip */}
        <div className="p-4 border-t border-border/60 bg-panel text-[11px] text-gray-400 space-y-2">
          <div className="flex items-center justify-between">
            <span className="flex items-center gap-1.5 text-gray-300 font-medium">
              <Cpu className="w-3.5 h-3.5 text-teal-400" />
              Windows Core
            </span>
            <span className="text-[10px] font-mono text-teal-400">Localhost Only</span>
          </div>
          <div className="text-[10px] text-gray-500 leading-tight">
            15m Max Storage • Zero Remote Cloud Transmission
          </div>
        </div>
      </aside>

      {/* Main Content Viewport */}
      <main className="flex-1 overflow-y-auto relative flex flex-col">
        {/* Real-time Disparity Alert Pop-up Modal */}
        <DisparityAlertPopup
          alert={incomingAlert}
          onDismiss={() => {
            setIncomingAlert(null);
            const desktop = (window as any).trustwireDesktop;
            if (desktop?.dismissAlert) {
              desktop.dismissAlert();
            }
          }}
          onPauseMonitoring={async () => {
            try {
              await api.stopMonitoring();
              const updated = await api.getMonitoringStatus();
              setMonitoringStatus(updated);
            } catch (e) {}
          }}
          onViewAlertHistory={() => setActiveTab('alerts')}
        />

        {/* View Switcher */}
        {activeTab === 'dashboard' && <Dashboard onNavigate={setActiveTab} />}
        {activeTab === 'monitoring' && (
          <LiveMonitoring
            currentStatus={monitoringStatus}
            onStatusChange={setMonitoringStatus}
          />
        )}
        {activeTab === 'analyze' && <AnalyzeMedia />}
        {activeTab === 'alerts' && <AlertHistory />}
        {activeTab === 'models' && <ModelsPerformance />}
        {activeTab === 'privacy' && <PrivacySettings />}
        {activeTab === 'about' && <About />}
      </main>
    </div>
  );
};
