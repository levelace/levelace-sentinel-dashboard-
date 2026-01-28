import React from 'react';
import TopBar from './components/TopBar';
import ScopeTable from './components/ScopeTable';
import TargetControl from './components/TargetControl';
import PhaseTimeline from './components/PhaseTimeline';
import AuditLog from './components/AuditLog';

const App: React.FC = () => {
  return (
    <div>
      <TopBar />
      <main>
        <ScopeTable />
        <TargetControl />
        <PhaseTimeline />
        <AuditLog />
      </main>
    </div>
  );
};

export default App;
