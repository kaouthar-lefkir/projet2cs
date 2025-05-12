import { useState, useEffect } from "react";
import { ArrowLeft } from "lucide-react";

export default function OperationModification({ operationData, onSave, onBackClick }) {
  const [operation, setOperation] = useState({
    id: 1,
    cout_prevue: 1000000,
    date_debut_prevue: "2025-04-01",
    date_fin_prevue: "2025-05-01",
    seuil_vert: 100,
    seuil_jaune: 80,
    seuil_rouge: 80,
    progression: 70
  });

  // State to track time between start and end dates
  const [daysPlanned, setDaysPlanned] = useState(30);

  // Effect to update operation data if passed as prop
  useEffect(() => {
    if (operationData) {
      console.log("Received operation data in ModifyOperation:", operationData);
      setOperation(prev => ({
        ...prev,
        ...operationData,
        id: operationData.id || prev.id
      }));
    }
  }, [operationData]);

  // Calculate days between dates whenever dates change
  useEffect(() => {
    const startDate = new Date(operation.date_debut_prevue);
    const endDate = new Date(operation.date_fin_prevue);
    
    // Calculate the difference in days
    const diffTime = Math.abs(endDate - startDate);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    setDaysPlanned(diffDays);
  }, [operation.date_debut_prevue, operation.date_fin_prevue]);

  // Handle input changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    
    // Handle numeric conversions
    if (["cout_prevue", "seuil_vert", "seuil_jaune", "seuil_rouge", "progression"].includes(name)) {
      setOperation({ ...operation, [name]: Number(value) });
    } else {
      setOperation({ ...operation, [name]: value });
    }
  };

  // Format currency for display
  const formatCurrency = (amount) => {
    if (amount >= 1000000) {
      return `${(amount / 1000000).toFixed(1)}M $`;
    } else if (amount >= 1000) {
      return `${(amount / 1000).toFixed(1)}K $`;
    }
    return `${amount} $`;
  };

  // Handle form submission
  const handleSubmit = (e) => {
    if (e) e.preventDefault();
    
    // Log what's being saved
    console.log("Saving operation data:", operation);
    
    // Pass the updated operation data back to the parent component
    onSave(operation);
  };

  return (
    <div className="bg-gray-100 p-6 min-h-screen">
      {/* Back button */}
      <div className="mb-4">
        <button 
          onClick={onBackClick}
          className="flex items-center text-blue-600 hover:text-blue-800 font-medium"
        >
          <ArrowLeft size={18} className="mr-2" />
          Back to operation details
        </button>
      </div>
    
      <div className="bg-white rounded-lg shadow p-6">
        <h1 className="text-3xl font-semibold text-blue-600 mb-6 text-center">
          Modify Operations Details
        </h1>
        
        <form onSubmit={handleSubmit} className="form-container">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Left Column */}
            <div>
              <div className="bg-white rounded-lg p-6 mb-6 shadow-sm border border-gray-100">
                <h3 className="text-lg font-semibold text-gray-700 mb-6">Etat Previsionel</h3>
                
                {/* Planned Dates */}
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <label htmlFor="date_debut_prevue" className="block text-sm font-medium text-gray-700 mb-1">
                      Date Début Prévue:
                    </label>
                    <input
                      type="date"
                      id="date_debut_prevue"
                      name="date_debut_prevue"
                      value={operation.date_debut_prevue}
                      onChange={handleChange}
                      className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label htmlFor="date_fin_prevue" className="block text-sm font-medium text-gray-700 mb-1">
                      Date Fin Prévue:
                    </label>
                    <input
                      type="date"
                      id="date_fin_prevue"
                      name="date_fin_prevue"
                      value={operation.date_fin_prevue}
                      onChange={handleChange}
                      className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
                
                {/* Délais row with calculated value */}
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Délais:</label>
                  <div className="p-2 bg-gray-100 rounded-md text-gray-700">
                    {daysPlanned} Days
                  </div>
                </div>
                
                {/* Planned Cost */}
                <div className="mb-4">
                  <label htmlFor="cout_prevue" className="block text-sm font-medium text-gray-700 mb-1">
                    Cout Prévue:
                  </label>
                  <input
                    type="number"
                    id="cout_prevue"
                    name="cout_prevue"
                    value={operation.cout_prevue}
                    onChange={handleChange}
                    className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <div className="text-xs text-gray-500 mt-1">
                    Current value: {formatCurrency(operation.cout_prevue)}
                  </div>
                </div>
              </div>
            </div>
            
            {/* Right Column */}
            <div>
              <div className="bg-white rounded-lg p-6 mb-6 shadow-sm border border-gray-100">
                <h3 className="text-lg font-semibold text-gray-700 mb-6">Seuils</h3>
                
                {/* Thresholds */}
                <div className="grid grid-cols-1 gap-4 mb-6">
                  <div>
                    <label htmlFor="seuil_vert" className="flex items-center text-sm font-medium text-gray-700 mb-1">
                      <div className="w-4 h-4 bg-green-500 rounded-full mr-2"></div>
                      Seuil Vert (%):
                    </label>
                    <input
                      type="number"
                      id="seuil_vert"
                      name="seuil_vert"
                      value={operation.seuil_vert}
                      onChange={handleChange}
                      min="0"
                      max="200"
                      className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <div className="text-xs text-gray-500 mt-1">
                      Greater than or equal to this value (prévision/réelle*100)
                    </div>
                  </div>
                  
                  <div>
                    <label htmlFor="seuil_jaune" className="flex items-center text-sm font-medium text-gray-700 mb-1">
                      <div className="w-4 h-4 bg-yellow-400 rounded-full mr-2"></div>
                      Seuil Jaune (%):
                    </label>
                    <input
                      type="number"
                      id="seuil_jaune"
                      name="seuil_jaune"
                      value={operation.seuil_jaune}
                      onChange={handleChange}
                      min="0"
                      max="200"
                      className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <div className="text-xs text-gray-500 mt-1">
                      Between this value and green threshold
                    </div>
                  </div>
                  
                  <div>
                    <label htmlFor="seuil_rouge" className="flex items-center text-sm font-medium text-gray-700 mb-1">
                      <div className="w-4 h-4 bg-red-500 rounded-full mr-2"></div>
                      Seuil Rouge (%):
                    </label>
                    <input
                      type="number"
                      id="seuil_rouge"
                      name="seuil_rouge"
                      value={operation.seuil_rouge}
                      onChange={handleChange}
                      min="0"
                      max="200"
                      className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <div className="text-xs text-gray-500 mt-1">
                      Less than this value
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-100">
                <h3 className="text-lg font-semibold text-gray-700 mb-6">Progress</h3>
                
                {/* Progress */}
                <div className="mb-6">
                  <label htmlFor="progression" className="block text-sm font-medium text-gray-700 mb-1">
                    Current Progress (%):
                  </label>
                  <input
                    type="number"
                    id="progression"
                    name="progression"
                    value={operation.progression}
                    onChange={handleChange}
                    min="0"
                    max="100"
                    className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                    <div
                      className="h-2 rounded-full bg-blue-500"
                      style={{ width: `${Math.min(100, Math.max(0, operation.progression))}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          {/* Action Buttons */}
          <div className="flex justify-center mt-8 space-x-4">
            <button
              type="button"
              onClick={onBackClick}
              className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-medium py-2 px-8 rounded transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-8 rounded transition-colors"
            >
              Save Changes
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}