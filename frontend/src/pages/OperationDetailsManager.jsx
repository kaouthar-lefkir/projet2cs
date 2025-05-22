import { useState, useEffect } from "react";
import { ChevronRight, ArrowLeft, AlertTriangle } from "lucide-react";
import ProblemsManager from "./ProblemsManager";

export default function OperationDetailsManager({ operationData, onBackClick }) {
  // Single operation object - no scenarios
  const [operation, setOperation] = useState({
    id: 1,
    phase: 2,
    nom: "Forage XP-123",
    description: "Opération de forage sur le site alpha",
    type_operation: "Extraction",
    date_debut_prevue: "2025-04-01",
    date_fin_prevue: "2025-05-01",
    date_debut_reelle: "2025-04-05",
    date_fin_reelle: null, // Still ongoing
    cout_prevue: 1000000,
    cout_reel: 800000,
    statut: "En cours",
    progression: 70, // Static progression percentage
    responsable: 1,
    seuil_vert: 100, // >= 100% is green (prévision >= réelle)
    seuil_jaune: 80, // 80-100% is yellow
    seuil_rouge: 80   // < 80% is red (prévision much less than réelle)
  });

  // Add state to track if we're in problems view
  const [showProblemsView, setShowProblemsView] = useState(false);

  // Effect to update operation data if passed as prop
  useEffect(() => {
    if (operationData) {
      console.log("Received operation data:", operationData);
      // Update the operation with data from props
      setOperation(prev => ({
        ...prev,
        ...operationData,
        nom: operationData.nom || prev.nom,
        id: operationData.id || prev.id
      }));
    }
  }, [operationData]);

  // Sample team data - added more members for pagination
  const team = [
    { id: 1, name: "Livia Bator", role: "Responsable", avatar: "/api/placeholder/40/40" },
    { id: 2, name: "Randy Press", role: "Ingénieur", avatar: "/api/placeholder/40/40" },
    { id: 3, name: "Workman", role: "Ingénieur", avatar: "/api/placeholder/40/40" },
    { id: 4, name: "Sarah Johnson", role: "Technicien", avatar: "/api/placeholder/40/40" },
    { id: 5, name: "Marc Dupont", role: "Analyste", avatar: "/api/placeholder/40/40" },
    { id: 6, name: "Elena Rodriguez", role: "Ingénieur", avatar: "/api/placeholder/40/40" }
  ];
  
  // State for team pagination
  const [teamCurrentPage, setTeamCurrentPage] = useState(0);
  const MEMBERS_PER_PAGE = 3;

  // Calculate metrics
  const [metrics, setMetrics] = useState({
    // Time metrics
    daysPlanned: 30,
    daysElapsed: 10,
    daysRemaining: 20,
    expectedDaysAtCurrentProgress: 21,
    timeRatio: 0,
    timeStatus: "green",
    
    // Cost metrics
    costPlanned: 1000000,
    costUsed: 800000,
    expectedCostAtCurrentProgress: 700000,
    costRatio: 0,
    costStatus: "green",
    
    // Overall progression
    progression: 70,
    progressionStatus: "green"
  });

  useEffect(() => {
    const calculateMetrics = () => {
      const today = new Date();
      
      // Time calculations
      const startDatePlanned = new Date(operation.date_debut_prevue);
      const endDatePlanned = new Date(operation.date_fin_prevue);
      const startDateActual = new Date(operation.date_debut_reelle);
      
      const totalDaysPlanned = Math.ceil((endDatePlanned - startDatePlanned) / (1000 * 60 * 60 * 24));
      const daysElapsed = Math.ceil((today - startDateActual) / (1000 * 60 * 60 * 24));
      const daysRemaining = Math.max(0, Math.ceil((endDatePlanned - today) / (1000 * 60 * 60 * 24)));
      
      // Expected days we should have used based on current progress
      const expectedDaysAtCurrentProgress = (operation.progression / 100) * totalDaysPlanned;
      
      // Calculate time ratio: (prévision/réelle)*100
      let timeRatio;
      
      if (daysElapsed === 0) {
        timeRatio = 100;
      } else {
        timeRatio = (expectedDaysAtCurrentProgress / daysElapsed) * 100;
      }
      
      // Calculate cost ratio: (prévision/réelle)*100
      const expectedCostAtCurrentProgress = (operation.progression / 100) * operation.cout_prevue;
      const costRatio = (expectedCostAtCurrentProgress / operation.cout_reel) * 100;
      
      // Determine status colors based on thresholds
      const getStatus = (ratio) => {
        if (ratio >= operation.seuil_vert) return "green";
        if (ratio >= operation.seuil_jaune) return "yellow";
        return "red";
      };
      
      const timeStatus = getStatus(timeRatio);
      const costStatus = getStatus(costRatio);
      
      const progressionStatus = operation.progression >= 50 ? "green" : 
                               operation.progression >= 20 ? "yellow" : "red";
      
      setMetrics({
        daysPlanned: totalDaysPlanned,
        daysElapsed,
        daysRemaining,
        expectedDaysAtCurrentProgress: Math.round(expectedDaysAtCurrentProgress),
        timeRatio: Math.round(timeRatio),
        timeStatus,
        
        costPlanned: operation.cout_prevue,
        costUsed: operation.cout_reel,
        expectedCostAtCurrentProgress: Math.round(expectedCostAtCurrentProgress),
        costRatio: Math.round(costRatio),
        costStatus,
        
        progression: operation.progression,
        progressionStatus
      });
    };
    
    calculateMetrics();
  }, [operation]);

  // Format currency
  const formatCurrency = (amount) => {
    if (amount >= 1000000) {
      return `${(amount / 1000000).toFixed(1)}M $`;
    } else if (amount >= 1000) {
      return `${(amount / 1000).toFixed(1)}K $`;
    }
    return `${amount} $`;
  };

  // Render progress bar with color
  const ProgressBar = ({ percentage, status }) => {
    let bgColor;
    switch (status) {
      case "red":
        bgColor = "bg-red-500";
        break;
      case "yellow":
        bgColor = "bg-yellow-400";
        break;
      case "green":
      default:
        bgColor = "bg-green-500";
    }

    return (
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className={`h-2 rounded-full ${bgColor}`}
          style={{ width: `${Math.min(100, Math.max(0, percentage))}%` }}
        ></div>
      </div>
    );
  };

  // Handle click on check problems button
  const handleProblemsClick = () => {
    setShowProblemsView(true);
  };

  // Handle return from problems page
  const handleBackFromProblems = () => {
    setShowProblemsView(false);
  };

  // Render circular progress
  const CircularProgress = ({ percentage, status }) => {
    const createSegments = () => {
      const segments = [];
      const segmentCount = 8;
      const segmentAngle = 360 / segmentCount;
      const gapAngle = 4;
      
      for (let i = 0; i < segmentCount; i++) {
        const startAngle = i * segmentAngle;
        const endAngle = startAngle + segmentAngle - gapAngle;
        const isActive = (i + 1) * (100 / segmentCount) <= percentage;
        
        const startRadians = (startAngle - 90) * Math.PI / 180;
        const endRadians = (endAngle - 90) * Math.PI / 180;
        const radius = 50;
        
        const x1 = 60 + radius * Math.cos(startRadians);
        const y1 = 60 + radius * Math.sin(startRadians);
        const x2 = 60 + radius * Math.cos(endRadians);
        const y2 = 60 + radius * Math.sin(endRadians);
        
        const largeArcFlag = endAngle - startAngle <= 180 ? "0" : "1";
        
        let color;
        if (isActive) {
          switch (status) {
            case "red":
              color = "#EF4444";
              break;
            case "yellow":
              color = "#FBBF24";
              break;
            case "green":
            default:
              color = "#10B981";
          }
        } else {
          color = "#c6c6c6";
        }
        
        segments.push(
          <path
            key={i}
            d={`M 60,60 L ${x1},${y1} A ${radius},${radius} 0 ${largeArcFlag} 1 ${x2},${y2} Z`}
            fill={color}
            stroke="white"
            strokeWidth="1"
          />
        );
      }
      
      return segments;
    };

    return (
      <div className="relative flex items-center justify-center w-40 h-40">
        <svg className="w-full h-full" viewBox="0 0 120 120">
          <circle cx="60" cy="60" r="54" fill="white" />
          {createSegments()}
          <circle cx="60" cy="60" r="40" fill="white" />
          <text
            x="60"
            y="60"
            fill="black"
            textAnchor="middle"
            dominantBaseline="middle"
            fontSize="32"
            fontWeight="bold"
          >
            {percentage}%
          </text>
        </svg>
      </div>
    );
  };

  // If in problems view, show the ProblemsManager component
  if (showProblemsView) {
    return (
      <ProblemsManager onBackClick={handleBackFromProblems} />
    );
  }

  return (
    <div className="bg-gray-100 p-6 h-screen">
      {/* Back button */}
      <div className="mb-4">
        <button 
          onClick={onBackClick}
          className="flex items-center text-blue-600 hover:text-blue-800 font-medium"
        >
          <ArrowLeft size={18} className="mr-2" />
          Back to operations
        </button>
      </div>
    
      <div className="bg-white rounded-lg shadow p-6">
        <h1 className="text-3xl font-semibold text-blue-600 mb-6 text-center">
          {operation.nom} - {operation.id}
        </h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column */}
          <div>
            {/* Progress Circle */}
            <div className="bg-white rounded-lg p-4 mb-8">
              <h3 className="text-lg font-semibold text-gray-700 mb-4">Operation Progress</h3>
              <div className="flex justify-center">
                <CircularProgress percentage={operation.progression} status={metrics.progressionStatus} />
              </div>
              <div className="text-center mt-2 text-sm text-gray-600">
                Overall Progress: {operation.progression}%
              </div>
            </div>
            
            {/* Team */}
            <div className="bg-white rounded-lg p-4">
              <h3 className="text-lg font-semibold text-gray-700 mb-4">Operation Team</h3>
              <div className="flex items-center justify-center relative">
                {/* Left Arrow Button */}
                {teamCurrentPage > 0 && (
                  <button 
                    onClick={() => setTeamCurrentPage(prev => Math.max(0, prev - 1))}
                    className="absolute left-0 text-gray-400 hover:text-gray-600"
                    aria-label="Previous team members"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                    </svg>
                  </button>
                )}
                
                {/* Team Members */}
                <div className="flex space-x-8 items-center px-8">
                  {team
                    .slice(
                      teamCurrentPage * MEMBERS_PER_PAGE, 
                      teamCurrentPage * MEMBERS_PER_PAGE + MEMBERS_PER_PAGE
                    )
                    .map((member) => (
                      <div key={member.id} className="flex flex-col items-center">
                        <img src={member.avatar} alt={member.name} className="w-14 h-14 rounded-full mb-2" />
                        <p className="font-medium text-sm">{member.name}</p>
                        <p className="text-gray-500 text-xs">{member.role === "Responsable" ? "Résponsable" : member.role}</p>
                      </div>
                    ))}
                </div>
                
                {/* Right Arrow Button */}
                {(teamCurrentPage + 1) * MEMBERS_PER_PAGE < team.length && (
                  <button 
                    onClick={() => setTeamCurrentPage(prev => Math.min(Math.ceil(team.length / MEMBERS_PER_PAGE) - 1, prev + 1))}
                    className="absolute right-0 text-gray-400 hover:text-gray-600"
                    aria-label="Next team members"
                  >
                    <ChevronRight size={24} />
                  </button>
                )}
              </div>
              
              {/* Pagination dots */}
              {team.length > MEMBERS_PER_PAGE && (
                <div className="flex justify-center mt-4 space-x-2">
                  {Array.from({ length: Math.ceil(team.length / MEMBERS_PER_PAGE) }).map((_, index) => (
                    <button
                      key={index}
                      onClick={() => setTeamCurrentPage(index)}
                      className={`h-2 w-2 rounded-full ${
                        teamCurrentPage === index ? 'bg-blue-600' : 'bg-gray-300'
                      }`}
                      aria-label={`Go to page ${index + 1}`}
                    />
                  ))}
                </div>
              )}
            </div>
          </div>
          
          {/* Right Column */}
          <div>
            {/* Current Status */}
            <div className="bg-white rounded-lg p-6 mb-8">
              <h3 className="text-lg font-semibold text-gray-700 mb-6">Etat Actuel</h3>
              
              {/* Time Status */}
              <div className="mb-8">
                <div className="flex justify-between mb-2">
                  <span className="text-gray-700 font-medium">Délais</span>
                  <span className="font-medium flex items-center">
                    {metrics.daysElapsed} days used
                    {metrics.timeStatus === "red" && <AlertTriangle size={16} className="ml-1 text-red-500" />}
                    {metrics.timeStatus === "yellow" && <AlertTriangle size={16} className="ml-1 text-yellow-400" />}
                  </span>
                </div>
                <ProgressBar percentage={Math.min(100, (metrics.daysElapsed / metrics.daysPlanned) * 100)} status={metrics.timeStatus} />
                <div className="text-xs text-gray-500 mt-1">
                  Expected {metrics.expectedDaysAtCurrentProgress} days at {operation.progression}% progress / Actual {metrics.daysElapsed} days = {metrics.timeRatio}%
                </div>
              </div>
              
              {/* Cost Status */}
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-gray-700 font-medium">Cout</span>
                  <span className="font-medium flex items-center">
                    {formatCurrency(metrics.costUsed)}
                    {metrics.costStatus === "red" && <AlertTriangle size={16} className="ml-1 text-red-500" />}
                    {metrics.costStatus === "yellow" && <AlertTriangle size={16} className="ml-1 text-yellow-400" />}
                  </span>
                </div>
                <ProgressBar percentage={Math.min(100, (metrics.costUsed / metrics.costPlanned) * 100)} status={metrics.costStatus} />
                <div className="text-xs text-gray-500 mt-1">
                  Expected {formatCurrency(metrics.expectedCostAtCurrentProgress)} at {operation.progression}% progress / Actual {formatCurrency(metrics.costUsed)} = {metrics.costRatio}%
                </div>
              </div>
              
              {/* Check Problems Button */}
              <div className="mt-6 flex justify-end">
                <button 
                  className="flex items-center text-red-500 hover:text-red-600 font-medium"
                  onClick={handleProblemsClick}
                >
                  <span className="mr-1">Check problems</span>
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M12.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-2.293-2.293a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </button>
              </div>
            </div>
            
            {/* Planned Status */}
            <div className="bg-white rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-700 mb-6">Etat Previsionel</h3>
              
              {/* Planned Time */}
              <div className="flex justify-between items-center mb-6">
                <span className="text-gray-700 font-medium">Délais :</span>
                <span className="font-medium text-lg text-blue-600">{metrics.daysPlanned} Days</span>
              </div>
              
              {/* Planned Cost */}
              <div className="flex justify-between items-center mb-8">
                <span className="text-gray-700 font-medium">Cout :</span>
                <span className="font-medium text-lg text-blue-600">{formatCurrency(metrics.costPlanned)}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}