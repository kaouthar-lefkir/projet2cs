import { useState, useEffect } from 'react';
import { Search, Paperclip, ArrowLeft, Trash2, Edit2, Check, X } from 'lucide-react';

export default function SolutionPage({ problem = null, onBackClick, onSolutionUpdate, onSolutionDelete }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSolution, setSelectedSolution] = useState(problem?.solution || null);
  const [searchResults, setSearchResults] = useState([]);
  const [showResults, setShowResults] = useState(false);
  const [newSolution, setNewSolution] = useState({ 
    object: problem?.description ? `Solution for ${problem.description}` : '', 
    description: '' 
  });
  const [isCreatingNew, setIsCreatingNew] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editedSolution, setEditedSolution] = useState(null);
  
  // If we have a problem with no solution, show the search interface by default
  const [searchMode, setSearchMode] = useState(!problem?.solution);

  // Update local state when props change
  useEffect(() => {
    setSelectedSolution(problem?.solution || null);
    setSearchMode(!problem?.solution);
    setNewSolution({ 
      object: problem?.description ? `Solution for ${problem.description}` : '', 
      description: '' 
    });
  }, [problem]);

  // Mock solutions for demonstration
  const mockSolutions = [
    { id: 1, object: 'Oil Pressure Drop', description: 'Solution for handling pressure drops in the main pipeline.' },
    { id: 2, object: 'Valve Malfunction', description: 'Procedure to fix valve malfunctions in section A.' },
    { id: 3, object: 'Sensor Calibration', description: 'Steps to recalibrate pressure sensors after maintenance.' }
  ];

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
    setIsCreatingNew(false);
    setIsEditing(false);
    
    // Update the parent component's state
    if (onSolutionUpdate) {
      onSolutionUpdate(solution);
    }
  };

  const handleNewSolutionChange = (e) => {
    const { name, value } = e.target;
    setNewSolution(prev => ({ ...prev, [name]: value }));
  };

  const handleEditedSolutionChange = (e) => {
    const { name, value } = e.target;
    setEditedSolution(prev => ({ ...prev, [name]: value }));
  };

  const createNewSolution = () => {
    if (!newSolution.object.trim()) return;
    
    const createdSolution = {
      id: Date.now(),
      ...newSolution
    };
    
    setSelectedSolution(createdSolution);
    setNewSolution({ object: '', description: '' });
    setIsCreatingNew(false);
    
    // Update the parent component's state
    if (onSolutionUpdate) {
      onSolutionUpdate(createdSolution);
    }
  };

  const startNewSolution = () => {
    setIsCreatingNew(true);
    setSelectedSolution(null);
    setShowResults(false);
    setSearchMode(false);
    setIsEditing(false);
  };
  
  const switchToSearchMode = () => {
    setIsCreatingNew(false);
    setSelectedSolution(null);
    setSearchMode(true);
    setShowResults(false);
    setIsEditing(false);
  };

  const startEditing = () => {
    setIsEditing(true);
    setEditedSolution({...selectedSolution});
  };

  const cancelEditing = () => {
    setIsEditing(false);
    setEditedSolution(null);
  };

  const saveEdits = () => {
    if (!editedSolution.object.trim()) return;
    
    setSelectedSolution(editedSolution);
    setIsEditing(false);
    
    // Update the parent component's state
    if (onSolutionUpdate) {
      onSolutionUpdate(editedSolution);
    }
  };

  const deleteSolution = () => {
    if (confirm('Are you sure you want to delete this solution?')) {
      setSelectedSolution(null);
      setSearchMode(true);
      
      // Update the parent component's state
      if (onSolutionDelete) {
        onSolutionDelete();
      }
    }
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
        
        {!selectedSolution && !isCreatingNew && searchMode && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="font-medium text-gray-700">Find an existing solution</h3>
              <button 
                className="px-4 py-2 text-blue-600 hover:underline"
                onClick={startNewSolution}
              >
                Create new solution instead
              </button>
            </div>
            
            <div className="relative">
              <div className="flex items-center border border-gray-300 rounded-lg overflow-hidden">
                <span className="pl-4">
                  <Search size={20} className="text-gray-400" />
                </span>
                <input
                  type="text"
                  placeholder="Chercher une ancienne solution"
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
                    <button 
                      className="mt-2 text-blue-600 hover:underline"
                      onClick={startNewSolution}
                    >
                      Create a new solution?
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
        
        {selectedSolution && !isEditing && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium">Selected Solution</h3>
              <div className="flex space-x-2">
                <button 
                  onClick={startEditing}
                  className="p-2 text-blue-600 hover:bg-blue-50 rounded-full"
                  title="Edit solution"
                >
                  <Edit2 size={20} />
                </button>
                <button 
                  onClick={deleteSolution}
                  className="p-2 text-red-500 hover:bg-red-50 rounded-full"
                  title="Delete solution"
                >
                  <Trash2 size={20} />
                </button>
              </div>
            </div>
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

        {selectedSolution && isEditing && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium">Edit Solution</h3>
              <div className="flex space-x-2">
                <button 
                  onClick={saveEdits}
                  className="p-2 text-green-600 hover:bg-green-50 rounded-full"
                  title="Save changes"
                >
                  <Check size={20} />
                </button>
                <button 
                  onClick={cancelEditing}
                  className="p-2 text-gray-500 hover:bg-gray-50 rounded-full"
                  title="Cancel editing"
                >
                  <X size={20} />
                </button>
              </div>
            </div>
            <div className="mb-4">
              <label className="block text-gray-700 font-medium mb-2">Object:</label>
              <input
                type="text"
                name="object"
                className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={editedSolution.object}
                onChange={handleEditedSolutionChange}
              />
            </div>
            <div className="mb-4">
              <label className="block text-gray-700 font-medium mb-2">Description:</label>
              <textarea
                name="description"
                rows="6"
                className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={editedSolution.description}
                onChange={handleEditedSolutionChange}
              ></textarea>
            </div>
          </div>
        )}
        
        {isCreatingNew && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium">New Solution</h3>
              <button 
                className="px-4 py-2 text-blue-600 hover:underline"
                onClick={switchToSearchMode}
              >
                Find existing solution instead
              </button>
            </div>
            
            <div className="mb-4">
              <label className="block text-gray-700 font-medium mb-2">Object:</label>
              <input
                type="text"
                name="object"
                className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={newSolution.object}
                onChange={handleNewSolutionChange}
              />
            </div>
            <div className="mb-4">
              <label className="block text-gray-700 font-medium mb-2">Description:</label>
              <textarea
                name="description"
                rows="6"
                className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={newSolution.description}
                onChange={handleNewSolutionChange}
              ></textarea>
            </div>
            <div className="flex justify-end">
              <button
                type="button"
                className="flex items-center gap-2 px-4 py-2"
              >
                <Paperclip size={20} className="text-gray-600" />
              </button>
            </div>
            <div className="flex justify-end mt-4">
              <button
                type="button"
                className="px-6 py-2 bg-orange-500 text-white rounded-md hover:bg-orange-600 font-medium"
                onClick={createNewSolution}
              >
                Add
              </button>
            </div>
          </div>
        )}
        
        {!selectedSolution && !isCreatingNew && !searchMode && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <div className="flex space-x-4 justify-center">
              <button 
                className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                onClick={switchToSearchMode}
              >
                Search for existing solution
              </button>
              <button 
                className="px-6 py-3 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
                onClick={startNewSolution}
              >
                Create a new solution
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}