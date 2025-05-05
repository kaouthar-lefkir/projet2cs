import React, { useState, useEffect } from 'react';
import { FiSettings, FiBell } from 'react-icons/fi';

function Topbar({ pageTitle }) {
  const [userName, setUserName] = useState('');
  const [userImage, setUserImage] = useState('');

  useEffect(() => {
    // Récupérer les informations de l'utilisateur depuis le localStorage
    const userData = JSON.parse(localStorage.getItem('user'));
    if (userData) {
      setUserName(userData.name);
      setUserImage(userData.picture);
    }
  }, []);

  return (
    <div className="flex items-center justify-between bg-white py-4 px-6 border-b border-gray-200">
      {/* Page Title */}
      <div className="flex-grow">
        <h1 className="text-2xl font-bold text-gray-800">{pageTitle || 'Project Details'}</h1>
      </div>
      
      {/* Icons and User Profile */}
      <div className="flex items-center space-x-4">
        {/* Settings Icon */}
        <button className="text-gray-500 hover:text-gray-700 p-2 rounded-full hover:bg-gray-100">
          <FiSettings size={20} />
        </button>
        
        {/* Notification Icon */}
        <button className="text-gray-500 hover:text-gray-700 p-2 rounded-full hover:bg-gray-100 relative">
          <FiBell size={20} />
          <span className="absolute top-1 right-1 h-2 w-2 bg-red-500 rounded-full"></span>
        </button>
        
        {/* User Profile Image */}
        <div className="flex items-center">
          <img 
            src={userImage || '/api/placeholder/40/40'} 
            alt="User Profile" 
            className="w-10 h-10 rounded-full object-cover border border-gray-200" 
          />
        </div>
      </div>
    </div>
  );
}

export default Topbar;