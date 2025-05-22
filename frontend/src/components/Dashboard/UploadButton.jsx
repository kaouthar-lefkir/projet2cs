import React from 'react';

const UploadButton = ({ onClick }) => {
  return (
    <div className="flex justify-end my-6 mr-4">
      <button 
        onClick={onClick}
        className="flex items-center bg-orange-500 hover:bg-orange-600 text-white font-medium py-2 px-4 rounded-lg shadow-lg transition-colors"
      >
        Upload repport
      </button>
    </div>
  );
};

export default UploadButton;