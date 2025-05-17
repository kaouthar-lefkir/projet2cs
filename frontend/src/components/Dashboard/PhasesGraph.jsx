import { useState } from 'react';

export default function PhasesGraph() {
  // Static data with pre-defined bar heights
  const [phasesData] = useState([
    {
      id: 1,
      nom: "P1",
      previsionHeight: 60,
      reelHeight: 40,
      status: "done" // green
    },
    {
      id: 2,
      nom: "P2",
      previsionHeight: 130,
      reelHeight: 40,
      status: "inProgress" // yellow
    },
    {
      id: 3,
      nom: "P3",
      previsionHeight: 180,
      reelHeight: 110,
      status: "inProgress" // yellow
    },
    {
      id: 4,
      nom: "P4",
      previsionHeight: 220,
      reelHeight: 0, // Not started yet
      status: "late" // would be red, but using yellow to match image
    }
  ]);

  // Get color for status
  const getStatusColor = (status) => {
    switch (status) {
      case 'late': return '#FACC15'; // yellow-400 (using yellow to match your image)
      case 'inProgress': return '#FACC15'; // yellow-400
      case 'done': return '#10B981'; // green-500
      default: return '#FACC15'; // default yellow
    }
  };

  // Constants for positioning
  const barWidth = 40;
  const barSpacing = 10;
  const topY = 50;
  const leftGroupX = 10; // Moved to far left
  const rightGroupX = 300; // Moved to far right

  return (
    <div className="bg-white rounded-lg shadow p-6 w-full">
      {/* Header */}
      <div className="flex justify-between mb-4 text-lg font-bold text-blue-800">
        <div className="ml-4">Prévision</div>
        <div className="mr-4">Réel</div>
      </div>
      
      {/* Graph container */}
      <div className="w-full h-96">
        <svg viewBox="0 0 500 400" className="w-full h-full">
          {/* Left Column - Prévision (P4,P3,P2,P1 order) at far left */}
          <g className="prevision-column">
            {phasesData.slice().reverse().map((phase, index) => {
              const xPosition = leftGroupX + index * (barWidth + barSpacing);
              return (
                <rect
                  key={`prev-${phase.id}`}
                  x={xPosition}
                  y={topY}
                  width={barWidth}
                  height={phase.previsionHeight}
                  rx={barWidth/2}
                  ry={barWidth/2}
                  fill={getStatusColor(phase.status)}
                />
              );
            })}
          </g>
          
          {/* Right Column - Réel (P1,P2,P3,P4 order) at far right */}
          <g className="reel-column">
            {phasesData.map((phase, index) => {
              const xPosition = rightGroupX + index * (barWidth + barSpacing);
              return (
                <rect
                  key={`reel-${phase.id}`}
                  x={xPosition}
                  y={topY}
                  width={barWidth}
                  height={phase.reelHeight > 0 ? phase.reelHeight : 0} // Safety check
                  rx={barWidth/2}
                  ry={barWidth/2}
                  fill={getStatusColor(phase.status)}
                />
              );
            })}
          </g>
          
          {/* Phase labels */}
          {/* Left labels (P4,P3,P2,P1) */}
          {phasesData.slice().reverse().map((phase, index) => {
            const leftX = leftGroupX + index * (barWidth + barSpacing) + barWidth/2;
            return (
              <text
                key={`left-label-${phase.id}`}
                x={leftX}
                y={topY - 10}
                textAnchor="middle"
                fontSize="12"
                fill="#4B5563"
              >
                {phase.nom}
              </text>
            );
          })}
          
          {/* Right labels (P1,P2,P3,P4) */}
          {phasesData.map((phase, index) => {
            const rightX = rightGroupX + index * (barWidth + barSpacing) + barWidth/2;
            return (
              <text
                key={`right-label-${phase.id}`}
                x={rightX}
                y={topY - 10}
                textAnchor="middle"
                fontSize="12"
                fill="#4B5563"
              >
                {phase.nom}
              </text>
            );
          })}
          
          {/* Add dividing line in center for visual clarity (optional) */}
          <line 
            x1="250" 
            y1="30" 
            x2="250" 
            y2="300" 
            stroke="#E5E7EB" 
            strokeWidth="1" 
            strokeDasharray="5,5" 
          />
        </svg>
      </div>
      
      {/* Legend */}
      <div className="flex justify-center mt-4 space-x-8">
        <div className="flex items-center">
          <div className="mr-2 w-3 h-3 rounded-full bg-red-500"></div>
          <span className="text-sm text-gray-600">Late</span>
        </div>
        <div className="flex items-center">
          <div className="mr-2 w-3 h-3 rounded-full bg-yellow-400"></div>
          <span className="text-sm text-gray-600">In Progress</span>
        </div>
        <div className="flex items-center">
          <div className="mr-2 w-3 h-3 rounded-full bg-green-500"></div>
          <span className="text-sm text-gray-600">Done</span>
        </div>
      </div>
    </div>
  );
}