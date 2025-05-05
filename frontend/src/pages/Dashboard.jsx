import React from 'react';
import Topbar from '../components/Topbar';

function Dashboard() {
  return (
    <div className="flex h-screen bg-gray-50">
     
      
      <div className="flex-1 flex flex-col overflow-hidden">
       
        <Topbar pageTitle="Dashboard" />
        
      
        <div className="flex-1 overflow-auto p-6">
          <h3> Dashboard content </h3>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;