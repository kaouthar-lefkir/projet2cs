import React, { useState } from 'react';
import Topbar from '../components/Topbar';
import { ProgressBar } from 'react-bootstrap';
import PhasesGraph from '../components/Dashboard/PhasesGraph';
import PhasesPieChart from '../components/Dashboard/PhasesPieChart';
import PhasesLineChart from '../components/Dashboard/PhasesLineChart';
import UploadButton from '../components/Dashboard/UploadButton';
import ProgressBars from '../components/Dashboard/ProgressBars';

function Dashboard() {
  const [projectData, setProjectData] = useState({
    daysPlanned: 100,
    daysElapsed: 50,
    costPlanned: 10,
    costUsed: 7,
    progression: 50,
    seuil_vert: 100,
    seuil_jaune: 80,
    seuil_rouge: 80,
  });

  const [phasesData, setPhasesData] = useState([
    {
      id: 1,
      nom: 'Forage XP-123',
      date_debut_prevue: '2025-04-01',
      date_fin_prevue: '2025-05-01',
      date_debut_reelle: '2025-04-05',
      date_fin_reelle: null,
      cout_prevue: 1000000,
      cout_reel: 800000,
      progression: 70,
      seuil_vert: 100,
      seuil_jaune: 80,
      seuil_rouge: 80,
    },
    {
      id: 2,
      nom: 'Installation Pipeline E-456',
      date_debut_prevue: '2025-03-15',
      date_fin_prevue: '2025-04-15',
      date_debut_reelle: '2025-03-20',
      date_fin_reelle: null,
      cout_prevue: 1500000,
      cout_reel: 1600000,
      progression: 60,
      seuil_vert: 100,
      seuil_jaune: 80,
      seuil_rouge: 80,
    },
    {
      id: 3,
      nom: 'Maintenance Platform B',
      date_debut_prevue: '2025-02-01',
      date_fin_prevue: '2025-03-01',
      date_debut_reelle: '2025-02-05',
      date_fin_reelle: '2025-03-10',
      cout_prevue: 800000,
      cout_reel: 750000,
      progression: 100,
      seuil_vert: 100,
      seuil_jaune: 80,
      seuil_rouge: 80,
    },
  ]);

  const lineChartData = [
    { name: 'Jul', value: 200 },
    { name: 'Aug', value: 400 },
    { name: 'Sep', value: 700 },
    { name: 'Oct', value: 200 },
    { name: 'Nov', value: 450 },
    { name: 'Dec', value: 200 },
    { name: 'Jan', value: 450 },
  ];

  const pieChartData = [
    { name: 'Operation1', percentage: 30, color: '#1e3a8a' },
    { name: 'Operation2', percentage: 15, color: '#f97316' },
    { name: 'Operation3', percentage: 35, color: '#2563eb' },
    { name: 'Operation4', percentage: 20, color: '#ec4899' },
  ];

  const handleUploadClick = () => {
    // Handle the upload logic here
    console.log('Upload report button clicked');
    // You can open a file picker or a modal here
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Topbar */}
        <Topbar pageTitle="Dashboard" />

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto p-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Phases Graph */}
            <div className="bg-white rounded-lg shadow p-4">
              <PhasesGraph phases={phasesData} />
            </div>

            {/* Project Progress Bars */}
            <div className="bg-white rounded-lg shadow p-4">
              <ProgressBars projectData={projectData} />
            </div>

            {/* Pie Chart */}
            <div className="bg-white rounded-lg shadow p-4">
              <div className="h-[300px]">
                <PhasesPieChart data={pieChartData} />
              </div>
            </div>

            {/* Performance Line Chart */}
            <div className="bg-white rounded-lg shadow p-4">
              <div className="h-[300px]">
                <PhasesLineChart data={lineChartData} />
              </div>
            </div>
            
            {/* Additional content to make the dashboard more scrollable */}
            
            {/* Upload Report Button - Now part of the scrollable content */}
            <div className="col-span-1 md:col-span-2">
              <UploadButton onClick={handleUploadClick} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;