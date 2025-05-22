import { useState } from "react";
import { ArrowLeft } from "lucide-react";
import SolutionManager from "./SolutionManager";

export default function ProblemsManager({ onBackClick }) {
  // Sample data for recent problems
  const [allProblems] = useState([
    {
      id: "#12548796",
      description: "Probleme 1",
      tacheId: "#12548796",
      responsableId: "#12548796",
      date: "28 Jan, 12:30 AM",
      solution: { object: "Oil Pressure Drop", description: "Solution for handling pressure drops in the main pipeline." }
    },
    {
      id: "#12548797",
      description: "Probleme 2",
      tacheId: "#12548796",
      responsableId: "#12548796",
      date: "25 Jan, 10:40 PM",
      solution: null // No solution yet
    },
    {
      id: "#12548798",
      description: "Probleme 3",
      tacheId: "#12548796",
      responsableId: "#12548796",
      date: "20 Jan, 10:40 PM",
      solution: { object: "Sensor Calibration", description: "Steps to recalibrate pressure sensors after maintenance." }
    },
    {
      id: "#12548799",
      description: "Probleme 4",
      tacheId: "#12548796",
      responsableId: "#12548796",
      date: "15 Jan, 03:29 PM",
      solution: null // No solution yet
    },
    {
      id: "#12548800",
      description: "Probleme 5",
      tacheId: "#12548796",
      responsableId: "#12548796",
      date: "14 Jan, 10:40 PM",
      solution: { object: "Valve Malfunction", description: "Procedure to fix valve malfunctions in section A." }
    },
    {
      id: "#12548801",
      description: "Probleme 6",
      tacheId: "#12548796",
      responsableId: "#12548796",
      date: "10 Jan, 08:15 AM",
      solution: null // No solution yet
    },
    {
      id: "#12548802",
      description: "Probleme 7",
      tacheId: "#12548796",
      responsableId: "#12548796",
      date: "05 Jan, 02:45 PM",
      solution: null // No solution yet
    },
    {
      id: "#12548803",
      description: "Probleme 8",
      tacheId: "#12548796",
      responsableId: "#12548796",
      date: "02 Jan, 11:30 AM",
      solution: null // No solution yet
    }
  ]);

  const [currentPage, setCurrentPage] = useState(1);
  const [selectedProblem, setSelectedProblem] = useState(null);
  const itemsPerPage = 5;
  
  // Calculate pagination
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentProblems = allProblems.slice(indexOfFirstItem, indexOfLastItem);
  const totalPages = Math.ceil(allProblems.length / itemsPerPage);

  // Page change handler
  const handlePageChange = (pageNumber) => {
    if (pageNumber > 0 && pageNumber <= totalPages) {
      setCurrentPage(pageNumber);
    }
  };

  // Handle solution button click - only navigate if solution exists
  const handleSolutionClick = (problem) => {
    if (problem.solution) {
      setSelectedProblem(problem);
    }
  };

  // Handle back to problems list
  const handleBackToProblems = () => {
    setSelectedProblem(null);
  };

  // If a problem with solution is selected, show the solution page
  if (selectedProblem && selectedProblem.solution) {
    return (
      <SolutionManager 
        problem={selectedProblem} 
        onBackClick={handleBackToProblems}
      />
    );
  }

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
          Recent Problems
        </h1>

        {/* Problems Table */}
        <table className="min-w-full">
          <thead>
            <tr className="text-left text-gray-500">
              <th className="pb-4 pl-4">Description</th>
              <th className="pb-4 px-3">Tache ID</th>
              <th className="pb-4 px-3">Responsable Id</th>
              <th className="pb-4 px-3">Date</th>
              <th className="pb-4 px-3 text-right">Expert Recommandation</th>
            </tr>
          </thead>
          <tbody>
            {currentProblems.map((problem, index) => (
              <tr key={index} className="border-t border-gray-200">
                <td className="py-4 pl-4 text-red-500">{problem.description}</td>
                <td className="py-4 px-3">{problem.tacheId}</td>
                <td className="py-4 px-3">{problem.responsableId}</td>
                <td className="py-4 px-3">{problem.date}</td>
                <td className="py-4 px-3 text-right">
                  <button 
                    className={`px-4 py-1 border rounded-full hover:bg-green-50 transition-colors duration-200 ${
                      problem.solution 
                        ? "border-blue-500 text-blue-500 cursor-pointer"
                        : "border-gray-300 text-gray-400 cursor-default"
                    }`}
                    onClick={() => handleSolutionClick(problem)}
                  >
                    {problem.solution ? "View Solution" : "No Solution"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {/* Pagination */}
        <div className="flex items-center justify-end mt-6 gap-2">
          <button 
            className={`flex items-center ${currentPage === 1 ? 'text-gray-400 cursor-not-allowed' : 'text-blue-600 hover:text-blue-800'}`}
            onClick={() => handlePageChange(currentPage - 1)}
            disabled={currentPage === 1}
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
            Previous
          </button>
          
          {Array.from({ length: totalPages }, (_, i) => i + 1).map((pageNumber) => (
            <button 
              key={pageNumber}
              onClick={() => handlePageChange(pageNumber)}
              className={`w-8 h-8 flex items-center justify-center rounded-full transition-colors duration-200 
                ${pageNumber === currentPage ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-blue-100'}`}
            >
              {pageNumber}
            </button>
          ))}
          
          <button 
            className={`flex items-center ${currentPage === totalPages ? 'text-gray-400 cursor-not-allowed' : 'text-blue-600 hover:text-blue-800'}`}
            onClick={() => handlePageChange(currentPage + 1)}
            disabled={currentPage === totalPages}
          >
            Next
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 ml-1" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}