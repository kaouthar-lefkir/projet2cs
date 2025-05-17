import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, Area, Tooltip } from 'recharts';

export default function PhasesLineChart({ chartData, threshold }) {
  // Données reçues en props:
  chartData = [
    { name: 'Jul', value: 200 },
    { name: 'Aug', value: 400 },
    { name: 'Sep', value: 700 },
    { name: 'Oct', value: 200 },
    { name: 'Nov', value: 450 },
    { name: 'Dec', value: 200 },
    { name: 'Jan', value: 450 },
  ];
  threshold = { warning: 400, critical: 600 };

  // Fonction pour déterminer la couleur de la ligne en fonction de la valeur
  const getLineColor = (value) => {
    if (value >= threshold.critical) return "#ef4444"; // Rouge pour valeurs critiques
    if (value >= threshold.warning) return "#f59e0b"; // Orange pour avertissement
    return "#4338ca"; // Bleu pour normal
  };

  // Création d'un tableau de segments de couleur pour la ligne
  const colorSegments = chartData.map((entry, index) => {
    // Si c'est le dernier point, pas de segment après lui
    if (index === chartData.length - 1) return null;
    
    const nextEntry = chartData[index + 1];
    const avgValue = (entry.value + nextEntry.value) / 2;
    const color = getLineColor(avgValue);
    
    return (
      <Line 
        key={index}
        type="monotone"
        data={[entry, nextEntry]}
        dataKey="value"
        stroke={color}
        strokeWidth={2}
        dot={false}
        activeDot={false}
        isAnimationActive={false}
      />
    );
  }).filter(segment => segment !== null);

  // Trouver la valeur max pour l'axe Y avec un peu de marge
  const maxValue = Math.max(...chartData.map(item => item.value)) * 1.2;

  return (
    <div className="bg-white p-4 rounded-lg shadow-sm">
      <h2 className="text-lg font-medium mb-4">Phases graph</h2>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
          <XAxis dataKey="name" stroke="#cbd5e1" />
          <YAxis stroke="#cbd5e1" domain={[0, maxValue]} />
          <Tooltip 
            formatter={(value) => [`${value}`, 'Value']}
            labelFormatter={(name) => `Month: ${name}`}
            contentStyle={{ backgroundColor: '#f8fafc', borderRadius: '4px' }}
          />
          
          {/* Segments colorés de la ligne */}
          {colorSegments}
          
          {/* Points sur la ligne */}
          <Line 
            type="monotone" 
            dataKey="value" 
            stroke="none"
            strokeWidth={0}
            dot={(props) => {
              const color = getLineColor(props.payload.value);
              return (
                <circle 
                  cx={props.cx} 
                  cy={props.cy} 
                  r={4} 
                  fill={color} 
                  stroke="white" 
                  strokeWidth={1}
                />
              );
            }}
          />
          
          {/* Zone sous la courbe */}
          <Area 
            type="monotone" 
            dataKey="value" 
            fill="#c7d2fe" 
            fillOpacity={0.3} 
            stroke="none"
          />
        </LineChart>
      </ResponsiveContainer>
      
      {/* Légende des seuils */}
      <div className="flex justify-end mt-2 text-xs text-gray-500">
        <div className="flex items-center mr-3">
          <div className="w-2 h-2 bg-indigo-700 mr-1"></div>
          <span>Normal (&lt;{threshold.warning})</span>
        </div>
        <div className="flex items-center mr-3">
          <div className="w-2 h-2 bg-amber-500 mr-1"></div>
          <span>Warning ({threshold.warning}-{threshold.critical})</span>
        </div>
        <div className="flex items-center">
          <div className="w-2 h-2 bg-red-500 mr-1"></div>
          <span>Critical (&gt;{threshold.critical})</span>
        </div>
      </div>
    </div>
  );
}