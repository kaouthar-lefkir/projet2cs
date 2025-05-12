import React, { useState } from 'react';
import Topbar from '../components/Topbar';
import ProfilePage from './DetailsProfile'; 

const ProjectTeam = () => {
  // Sample data - could be loaded from API
  const allTeamMembers = [
    {
      id: "#12548796",
      username: "Livia Bator",
      field: "Eng terrain",
      date: "28 Jan, 12:30 AM",
      avatar: "/api/placeholder/48/48"
    },
    {
      id: "#12548797", 
      username: "Alex Martin",
      field: "Architect",
      date: "18 Jan, 09:15 AM",
      avatar: "/api/placeholder/48/48"
    },
    {
      id: "#12548798", 
      username: "Sarah Chen",
      field: "Project Manager",
      date: "15 Jan, 02:40 PM",
      avatar: "/api/placeholder/48/48"
    },
    {
      id: "#12548799", 
      username: "Workman",
      field: "Engénieur",
      date: "25 Jan, 10:40 PM",
      avatar: "/api/placeholder/48/48"
    },
    {
      id: "#12548800", 
      username: "Jean Dupont",
      field: "Engénieur",
      date: "25 Jan, 10:40 PM",
      avatar: "/api/placeholder/48/48"
    },
    {
      id: "#12548801", 
      username: "Marie Laurent",
      field: "Engénieur",
      date: "25 Jan, 10:40 PM",
      avatar: "/api/placeholder/48/48"
    }
  ];

  const [currentPage, setCurrentPage] = useState(1);
  const [selectedUserId, setSelectedUserId] = useState(null); // État pour l'utilisateur sélectionné
  const itemsPerPage = 3;
  
  // Calculate pagination
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentTeamMembers = allTeamMembers.slice(indexOfFirstItem, indexOfLastItem);
  const totalPages = Math.ceil(allTeamMembers.length / itemsPerPage);

  // Page change handler
  const handlePageChange = (pageNumber) => {
    if (pageNumber > 0 && pageNumber <= totalPages) {
      setCurrentPage(pageNumber);
    }
  };

  // Gestionnaire de clic sur le bouton "Details"
  const handleDetailsClick = (userId) => {
    setSelectedUserId(userId);
  };

  // Gestionnaire de retour à la liste
  const handleBackToList = () => {
    setSelectedUserId(null);
  };

  // Si un utilisateur est sélectionné, afficher la page de profil
  if (selectedUserId) {
    return <ProfilePage userId={selectedUserId} onBackClick={handleBackToList} />;
  }

  // Sinon, afficher la liste des membres de l'équipe
  return (
    
    <div className="flex flex-col h-screen">
      <Topbar pageTitle="Project Team" />
      
      <div className="flex-1 p-8 bg-gray-50">
        <div className="bg-white rounded-lg shadow p-6 w-full">
          {/* Navigation Tabs */}
          <div className="border-b border-gray-200 mb-6">
            <div className="flex">
              <button className="px-4 py-2 text-blue-600 border-b-2 border-blue-600 font-medium">
                Profiles
              </button>
            </div>
          </div>

          {/* Team Members Table */}
          <table className="min-w-full">
            <thead>
              <tr className="text-left text-gray-500">
                <th className="pb-4 pl-4 w-1/5">Username</th>
                <th className="pb-4 px-3 w-1/5">User ID</th>
                <th className="pb-4 px-3 w-1/5">Field</th>
                <th className="pb-4 px-3 w-1/5">Date</th>
                <th className="pb-4 px-3 w-1/5 text-right">Profile</th>
              </tr>
            </thead>
            <tbody>
              {currentTeamMembers.map((member, index) => (
                <tr key={index} className="border-t border-gray-200">
                  <td className="py-4 pl-4">
                    {member.avatar && (
                      <div className="flex items-center">
                        <img 
                          src={member.avatar} 
                          alt={member.username} 
                          className="h-12 w-12 rounded-full mr-4" 
                        />
                        <span>{member.username}</span>
                      </div>
                    )}
                    {!member.avatar && <span className="pl-16">{member.username}</span>}
                  </td>
                  <td className="py-4 px-3">{member.id}</td>
                  <td className="py-4 px-3">{member.field}</td>
                  <td className="py-4 px-3">{member.date}</td>
                  <td className="py-4 px-3 text-right">
                    <button 
                      className="px-4 py-1 border border-blue-500 text-blue-500 rounded-full hover:bg-blue-50 transition-colors duration-200"
                      onClick={() => handleDetailsClick(member.id)}
                    >
                      Details
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
    </div>
  );
};

export default ProjectTeam;