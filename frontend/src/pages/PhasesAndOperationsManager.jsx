import { useState } from 'react';
import { ChevronDown, ChevronRight, AlertCircle } from 'lucide-react';
import Topbar from "../components/Topbar";
import OperationDetailsManager from './OperationDetailsManager'; // Updated import
import PhaseDetails from './PhaseDetails';

export default function OperationsContent() {
  // State to track which phases are expanded
  const [expandedPhases, setExpandedPhases] = useState({
    'Phase1': true,
    'Phase2': true
  });
  
  // State for confirmation popup
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [itemToDelete, setItemToDelete] = useState(null);
  
  // State to track selected operation for details view
  const [selectedOperation, setSelectedOperation] = useState(null);
  
  // State to track selected phase for details view
  const [selectedPhase, setSelectedPhase] = useState(null);

  // Sample data for operations
  const [operations, setOperations] = useState([
    {
      id: 'Phase1',
      type: 'phase',
      operationId: '#12548796',
      date: '28 Jan, 12.30 AM',
      expanded: true
    },
    {
      id: 'Operation 1',
      type: 'operation',
      phaseParent: 'Phase1',
      operationId: '#12548796',
      date: '25 Jan, 10.40 PM'
    },
    {
      id: 'Operation 2',
      type: 'operation',
      phaseParent: 'Phase1',
      operationId: '#12548796',
      date: '20 Jan, 10.40 PM'
    },
    {
      id: 'Operation 3',
      type: 'operation',
      phaseParent: 'Phase1',
      operationId: '#12548796',
      date: '15 Jan, 03.29 PM'
    },
    {
      id: 'Phase2',
      type: 'phase',
      operationId: '#12548796',
      date: '14 Jan, 10.40 PM',
      expanded: true
    }
  ]);

  // Toggle phase expansion
  const togglePhase = (phaseId) => {
    setExpandedPhases(prev => ({
      ...prev,
      [phaseId]: !prev[phaseId]
    }));
  };

  // Initiate the removal process with confirmation
  const initiateRemove = (id) => {
    setItemToDelete(id);
    setShowConfirmation(true);
  };

  // Cancel delete operation
  const cancelDelete = () => {
    setShowConfirmation(false);
    setItemToDelete(null);
  };

  // Confirm and handle removal
  const confirmRemove = () => {
    const id = itemToDelete;
    const itemToRemove = operations.find(op => op.id === id);
    
    if (itemToRemove.type === 'phase') {
      // If removing a phase, also remove all operations belonging to that phase
      setOperations(operations.filter(op => 
        op.id !== id && op.phaseParent !== id
      ));
    } else {
      // If removing just an operation
      setOperations(operations.filter(op => op.id !== id));
    }
    
    // Reset confirmation state
    setShowConfirmation(false);
    setItemToDelete(null);
  };

  // Handle details click for an operation
  const handleDetailsClick = (operation) => {
    setSelectedOperation(operation);
  };

  // Handle details click for a phase
  const handlePhaseDetailsClick = (phase) => {
    setSelectedPhase(phase);
  };

  // Handle back to list
  const handleBackToList = () => {
    setSelectedOperation(null);
    setSelectedPhase(null);
  };

  // If an operation is selected, show its details page
  if (selectedOperation) {
    return <OperationDetailsManager operationData={selectedOperation} onBackClick={handleBackToList} />;
  }

  // If a phase is selected, show its details page
  if (selectedPhase) {
    return <PhaseDetails phaseData={selectedPhase} onBackClick={handleBackToList} />;
  }

  return (
    <div className="flex flex-col h-screen">     
      <Topbar pageTitle={"Phases"}/>

      <div className="bg-gray-50 p-6 min-h-screen">
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="grid grid-cols-12 text-sm text-gray-500 font-medium mb-4 px-2">
            <div className="col-span-4">Description</div>
            <div className="col-span-3">Operation ID</div>
            <div className="col-span-3">Date</div>
            <div className="col-span-2">Progress</div>
          </div>

          {operations.map((operation) => (
            <div key={operation.id} className="mb-2">
              {operation.type === 'phase' ? (
                <div className="grid grid-cols-12 items-center py-3 px-2 rounded-md">
                  <div className="col-span-4 flex items-center">
                    <button 
                      onClick={() => togglePhase(operation.id)}
                      className="mr-2 text-blue-600 focus:outline-none"
                    >
                      {expandedPhases[operation.id] ? 
                        <ChevronDown size={20} /> : 
                        <ChevronRight size={20} />
                      }
                    </button>
                    <span className="font-medium text-gray-800">{operation.id}</span>
                  </div>
                  <div className="col-span-3 text-gray-600">{operation.operationId}</div>
                  <div className="col-span-3 text-gray-600">{operation.date}</div>
                  <div className="col-span-2 flex justify-between items-center">
                    <button 
                      className="px-4 py-1 text-blue-600 border border-blue-600 rounded-md text-sm"
                      onClick={() => handlePhaseDetailsClick(operation)}
                    >
                      Details
                    </button>
                    <button 
                      className="text-red-500 hover:text-red-700"
                      onClick={() => initiateRemove(operation.id)}
                    >
                      Remove
                    </button>
                  </div>
                </div>
              ) : (
                expandedPhases[operation.phaseParent] && (
                  <div className="grid grid-cols-12 items-center py-3 px-2 ml-8 rounded-md">
                    <div className="col-span-4 text-gray-800">{operation.id}</div>
                    <div className="col-span-3 text-gray-600">{operation.operationId}</div>
                    <div className="col-span-3 text-gray-600">{operation.date}</div>
                    <div className="col-span-2 flex justify-between items-center">
                      <button 
                        className="px-4 py-1 text-blue-600 border border-blue-600 rounded-md text-sm"
                        onClick={() => handleDetailsClick(operation)}
                      >
                        Details
                      </button>
                      <button 
                        className="text-red-500 hover:text-red-700"
                        onClick={() => initiateRemove(operation.id)}
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                )
              )}
            </div>
          ))}
        </div>

        {/* Confirmation Dialog */}
        {showConfirmation && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white p-6 rounded-lg shadow-lg w-96">
              <div className="flex items-center mb-4 text-amber-600">
                <AlertCircle className="mr-2" />
                <h3 className="text-lg font-medium">Confirm Removal</h3>
              </div>
              <p className="mb-6">
                Are you sure you want to remove this item? 
                {operations.find(op => op.id === itemToDelete)?.type === 'phase' && 
                  " This will also remove all operations within this phase."}
              </p>
              <div className="flex justify-end space-x-3">
                <button 
                  onClick={cancelDelete}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button 
                  onClick={confirmRemove}
                  className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
                >
                  Remove
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}