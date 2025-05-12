import { useState, useEffect } from 'react';
import { Search, ArrowLeft } from 'lucide-react';

export default function SolutionManager({ problem = null, onBackClick }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSolution, setSelectedSolution] = useState(problem?.solution || null);
  const [searchResults, setSearchResults] = useState([]);
  const [showResults, setShowResults] = useState(false);
  
  // Mock solutions for demonstration
  const mockSolutions = [
    { id: 1, object: 'Oil Pressure Drop', description: 'Solution for handling pressure drops in the main pipeline.' },
    { id: 2, object: 'Valve Malfunction', description: 'Procedure to fix valve malfunctions in section A.' },
    { id: 3, object: 'Sensor Calibration', description: 'Steps to recalibrate pressure sensors after maintenance.' }
  ];

  // Update local state when props change
  useEffect(() => {
    setSelectedSolution(problem?.solution || null);
  }, [problem]);

  const handleSearch = () => {
    if (!searchQuery.trim()) return;
    
    // Filter mock solutions based on search query
    const results = mockSolutions.filter(
      solution => 
        solution.object.toLowerCase().includes(searchQuery.toLowerCase()) ||
        solution.description.toLowerCase().includes(searchQuery.toLowerCase())
    );
    
    setSearchResults(results);
    setShowResults(true);
  };

  const selectSolution = (solution) => {
    setSelectedSolution(solution);
    setShowResults(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Back button */}
        <div className="mb-4">
          <button 
            onClick={onBackClick}
            className="flex items-center text-blue-600 hover:text-blue-800 font-medium"
          >
            <ArrowLeft size={18} className="mr-2" />
            Back to problems list
          </button>
        </div>

        <div className="mb-6">
          <h2 className="text-2xl font-bold text-gray-700">Solution</h2>
          <div className="h-1 w-16 bg-green-500 mt-1"></div>
        </div>

        {problem && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h3 className="text-lg font-semibold mb-4">Problem Details</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-gray-600">ID: <span className="text-gray-800">{problem.id}</span></p>
                <p className="text-gray-600">Description: <span className="text-red-500 font-medium">{problem.description}</span></p>
              </div>
              <div>
                <p className="text-gray-600">Tache ID: <span className="text-gray-800">{problem.tacheId}</span></p>
                <p className="text-gray-600">Date: <span className="text-gray-800">{problem.date}</span></p>
              </div>
            </div>
          </div>
        )}
        
        {!selectedSolution && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h3 className="font-medium text-gray-700 mb-4">Find an existing solution</h3>
            
            <div className="relative">
              <div className="flex items-center border border-gray-300 rounded-lg overflow-hidden">
                <span className="pl-4">
                  <Search size={20} className="text-gray-400" />
                </span>
                <input
                  type="text"
                  placeholder="Search for existing solutions"
                  className="w-full py-3 px-4 focus:outline-none"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                />
              </div>
              <button 
                className="absolute right-2 top-1/2 transform -translate-y-1/2 p-2 text-gray-400"
                onClick={handleSearch}
                type="button"
              >
                <Search size={16} />
              </button>
            </div>
            
            {showResults && (
              <div className="mt-4">
                {searchResults.length > 0 ? (
                  <div className="space-y-3">
                    <h3 className="font-medium text-gray-700">Results:</h3>
                    {searchResults.map(solution => (
                      <div 
                        key={solution.id}
                        className="p-3 border border-gray-200 rounded-md hover:bg-gray-50 cursor-pointer"
                        onClick={() => selectSolution(solution)}
                      >
                        <div className="font-medium">{solution.object}</div>
                        <div className="text-sm text-gray-600">{solution.description}</div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-4">
                    <p className="text-gray-600">No solutions found.</p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
        
        {selectedSolution && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-medium mb-4">Solution Details</h3>
            <div className="mb-4">
              <label className="block text-gray-700 font-medium mb-2">Object:</label>
              <div className="p-3 bg-gray-50 rounded-md">{selectedSolution.object}</div>
            </div>
            <div className="mb-4">
              <label className="block text-gray-700 font-medium mb-2">Description:</label>
              <div className="p-3 bg-gray-50 rounded-md min-h-32">{selectedSolution.description}</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}