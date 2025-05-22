import React, { useState } from 'react';
import logoImage from "../images/petro-logo.png";

const AddProject = ({ onBackToProjects }) => {
  const [formData, setFormData] = useState({
    projectName: '',
    responsible: '',
    address: ''
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevState => ({
      ...prevState,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    if (e) e.preventDefault();
    console.log('Form submitted:', formData);
    // Here you would typically send the data to your backend
    alert('Project added successfully!');
    // Clear form after submission
    setFormData({
      projectName: '',
      responsible: '',
      address: ''
    });
    // Optionally, return to projects view after successful submission
    // onBackToProjects();
  };

  // Card background color
  const cardBlueColor = '#3E92CC';

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      {/* Header with Logo */}
      <div className="flex justify-end mb-8 max-w-6xl mx-auto">
        <div className="w-32">
          <img 
            src={logoImage}
            alt="PetroMonitore Logo" 
            className="w-full"
          />
        </div>
      </div>
      
      {/* Main Content */}
      <div className="max-w-6xl mx-auto">
        <div className="max-w-2xl mx-auto">
          {/* Page Title */}
          <h1 className="text-3xl font-bold text-gray-800 mb-8 text-center">Add New Project</h1>
          
          {/* Project Card with Form */}
          <div 
            className="rounded-lg shadow-lg p-8 mb-8"
            style={{ 
              backgroundColor: cardBlueColor,
              border: '2px solid #494A8D'
            }}
          >
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label htmlFor="projectName" className="block text-white text-lg mb-2">
                  Project Name
                </label>
                <input
                  type="text"
                  id="projectName"
                  name="projectName"
                  value={formData.projectName}
                  onChange={handleChange}
                  className="w-full px-4 py-3 rounded-md bg-white text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-300"
                  placeholder="Enter project name"
                  required
                />
              </div>
              
              <div>
                <label htmlFor="responsible" className="block text-white text-lg mb-2">
                  Responsible Person
                </label>
                <input
                  type="text"
                  id="responsible"
                  name="responsible"
                  value={formData.responsible}
                  onChange={handleChange}
                  className="w-full px-4 py-3 rounded-md bg-white text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-300"
                  placeholder="Enter responsible person's name"
                  required
                />
              </div>
              
              <div>
                <label htmlFor="address" className="block text-white text-lg mb-2">
                  Address
                </label>
                <textarea
                  id="address"
                  name="address"
                  value={formData.address}
                  onChange={handleChange}
                  rows="3"
                  className="w-full px-4 py-3 rounded-md bg-white text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-300"
                  placeholder="Enter project address"
                  required
                />
              </div>
            </form>
          </div>
          
          {/* Buttons positioned at left and right */}
          <div className="flex justify-between mt-6">
            <button
              onClick={onBackToProjects}
              className="bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium py-3 px-6 rounded-lg transition-colors"
            >
              Back to Projects
            </button>
            
            <button
              onClick={handleSubmit}
              className="bg-orange-500 hover:bg-orange-600 text-white font-bold py-3 px-8 rounded-lg transition-colors"
            >
              Add Project
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AddProject;