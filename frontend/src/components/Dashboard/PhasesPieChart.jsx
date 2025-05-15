import { useState } from 'react';

export default function PhasesPieChart({ data }) {
  // Use data from props or fallback to default data if props not provided
  const phasesData = data || [
    { name: 'Operation1', percentage: 30, color: '#2d3a6d' },
    { name: 'Operation2', percentage: 15, color: '#f97316' },
    { name: 'Opration3', percentage: 35, color: '#2563eb' },
    { name: 'Operation4', percentage: 20, color: '#ec4899' },
  ];

  // Function to create a standard pie chart
  const createPieChart = () => {
    const segments = [];
    let cumulativeAngle = 0;
    const centerX = 120;
    const centerY = 120;
    const radius = 110; // Much smaller radius
    
    phasesData.forEach(phase => {
      // Fix color format if it has backticks (from your dashboard code)
      const color = phase.color.replace(/`/g, '') || '#000000';
      
      // Calculate the start and end angles for this segment
      const startAngle = cumulativeAngle;
      const sliceAngle = (phase.percentage / 100) * 2 * Math.PI;
      const endAngle = startAngle + sliceAngle;
      
      // Calculate the SVG arc path
      const startX = centerX + radius * Math.cos(startAngle);
      const startY = centerY + radius * Math.sin(startAngle);
      const endX = centerX + radius * Math.cos(endAngle);
      const endY = centerY + radius * Math.sin(endAngle);
      
      const largeArcFlag = sliceAngle > Math.PI ? 1 : 0;
      
      const pathData = [
        `M ${centerX} ${centerY}`,
        `L ${startX} ${startY}`,
        `A ${radius} ${radius} 0 ${largeArcFlag} 1 ${endX} ${endY}`,
        'Z'
      ].join(' ');
      
      // Calculate position for the text
      const midAngle = startAngle + sliceAngle / 2;
      const textRadius = radius * 0.6; // Position text at 60% of the radius
      const textX = centerX + textRadius * Math.cos(midAngle);
      const textY = centerY + textRadius * Math.sin(midAngle);
      
      segments.push({
        path: pathData,
        color: color,
        name: phase.name, 
        percentage: phase.percentage,
        textX,
        textY
      });
      
      // Update the cumulative angle for the next segment
      cumulativeAngle = endAngle;
    });
    
    return segments;
  };

  const segments = createPieChart();

  return (
    <div className="h-full flex flex-col">
      <h2 className="text-base font-medium text-gray-700 mb-1">Phases Statistics</h2>
      <div className="flex-1 flex items-center justify-center">
        <svg height="240px" width="240px" viewBox="0 0 240 240" preserveAspectRatio="xMidYMid meet">
          {segments.map((segment, index) => (
            <g key={index}>
              <path d={segment.path} fill={segment.color} />
              <text 
                x={segment.textX} 
                y={segment.textY - 4} 
                fill="white" 
                fontSize="10"
                fontWeight="bold" 
                textAnchor="middle" 
                dominantBaseline="middle"
              >
                {segment.percentage}%
              </text>
              <text 
                x={segment.textX} 
                y={segment.textY + 6} 
                fill="white" 
                fontSize="8"
                fontWeight="medium" 
                textAnchor="middle" 
                dominantBaseline="middle"
              >
                {segment.name}
              </text>
            </g>
          ))}
        </svg>
      </div>
    </div>
  );
}