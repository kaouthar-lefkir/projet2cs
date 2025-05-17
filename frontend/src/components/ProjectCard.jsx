import React from 'react';

const ProjectCard = ({ project, onClick }) => {
  return (
    <button 
      className="w-64 h-48 rounded-lg p-6 flex flex-col items-center justify-center text-white border border-gray-300 cursor-pointer hover:opacity-90 transition-opacity"
      style={{ 
        backgroundColor: '#3E92CC',
        borderColor: '#494A8D',
        borderWidth: '1px'
      }}
      onClick={onClick}
    >
      <h2 className="text-2xl font-bold mb-2">{project.nom}</h2>
      <p className="text-lg mb-2 opacity-80">{project.responsable}</p>
      <p className="text-base opacity-80">{project.localisation}</p>
    </button>
  );
};

export default ProjectCard;