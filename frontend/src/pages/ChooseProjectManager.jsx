import React, { useState, useRef, useEffect } from 'react';
import { Search, Filter, ChevronDown } from 'lucide-react';
import ProjectCard from '../components/ProjectCard';
import AddProject from './AddProject';
import logoImage from "../images/petro-logo.png";

// Main Dashboard Component
const ChooseProjectManager = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterOption, setFilterOption] = useState('all');
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [showAddProject, setShowAddProject] = useState(false); // State for controlling view
  const dropdownRef = useRef(null);
  
  // Sample project data
  const projects = [
    {
      id: 1,
      nom: "Petroleum Exploration",
      responsable: "NOM DE RESPONSABLE",
      localisation: "Adresse du projet ."
    },
    {
      id: 2,
      nom: "Petroleum Etion",
      responsable: "NOM DE RESPONSABLE",
      localisation: "Adresse du projet ."
    },
    {
      id: 3,
      nom: "Petroleum ",
      responsable: "NOM DE RESPONSABLE",
      localisation: "Adresse du projet ."
    },
    {
      id: 4,
      nom: "Petroleum Exploration",
      responsable: "NOM DE RESPONSABLE",
      localisation: "Adress projet ."
    },
    {
      id: 5,
      nom: " Exploration",
      responsable: "NOM DE RESPONSABLE",
      localisation: "Adresse du projet ."
    },
    {
      id: 6,
      nom: "Petroleum Exploration",
      responsable: "RESPONSABLE",
      localisation: "Adresse du projet ."
    },
  ];

  // Filter projects based on search term and filter option
  const filteredProjects = projects.filter(project => {
    const searchLower = searchTerm.toLowerCase();
    
    // Apply search based on selected filter
    switch(filterOption) {
      case 'name':
        return project.nom.toLowerCase().includes(searchLower);
      case 'responsible':
        return project.responsable.toLowerCase().includes(searchLower);
      case 'address':
        return project.localisation.toLowerCase().includes(searchLower);
      case 'all':
      default:
        return (
          project.nom.toLowerCase().includes(searchLower) ||
          project.responsable.toLowerCase().includes(searchLower) ||
          project.localisation.toLowerCase().includes(searchLower)
        );
    }
  });

  // Handle search input change
  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
  };

  // Handle filter option change
  const handleFilterChange = (option) => {
    setFilterOption(option);
    setDropdownOpen(false);
  };
  
  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setDropdownOpen(false);
      }
    }
    
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [dropdownRef]);

  // Handle add new project button click
  const handleAddProject = () => {
    setShowAddProject(true);
  };

  // Handle back to projects from add project form
  const handleBackToProjects = () => {
    setShowAddProject(false);
  };

  // If add project view is active, show the AddProject component
  if (showAddProject) {
    return <AddProject onBackToProjects={handleBackToProjects} />;
  }

  // Otherwise show the project list view
  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Logo and Header */}
      <div className="flex justify-end mb-8">
        <div className="w-32">
          <img 
            src={logoImage}
            alt="PetroMonitore Logo" 
            className="w-full"
          />
        </div>
      </div>
      
      {/* Search Bar with Filter Dropdown */}
      <div className="w-full max-w-2xl mx-auto mb-12">
        <div className="flex items-center border border-gray-300 rounded-lg bg-white px-4 py-2">
          <Search className="text-gray-400 mr-2" size={20} />
          <input
            type="text"
            placeholder="Search projects"
            className="w-full focus:outline-none"
            value={searchTerm}
            onChange={handleSearchChange}
          />
          
          {/* Filter Dropdown */}
          <div className="relative flex items-center ml-2 pl-2 border-l border-gray-200" ref={dropdownRef}>
            <button 
              className="flex items-center text-gray-600 hover:text-gray-800 focus:outline-none"
              onClick={() => setDropdownOpen(!dropdownOpen)}
            >
              <Filter size={16} />
              <span className="mx-1 text-sm font-medium">
                {filterOption === 'all' ? 'All' : 
                 filterOption === 'name' ? 'Name' : 
                 filterOption === 'responsible' ? 'Responsible' : 'Address'}
              </span>
              <ChevronDown size={14} className={`transition-transform duration-200 ${dropdownOpen ? 'transform rotate-180' : ''}`} />
            </button>
            
            {dropdownOpen && (
              <div className="absolute right-0 top-full mt-1 w-48 bg-white rounded-md shadow-lg py-1 z-10 border border-gray-200">
                <button 
                  className={`block px-4 py-2 text-sm text-left w-full hover:bg-gray-100 ${filterOption === 'all' ? 'bg-gray-100 text-blue-600 font-medium' : ''}`}
                  onClick={() => handleFilterChange('all')}
                >
                  All
                </button>
                <button 
                  className={`block px-4 py-2 text-sm text-left w-full hover:bg-gray-100 ${filterOption === 'name' ? 'bg-gray-100 text-blue-600 font-medium' : ''}`}
                  onClick={() => handleFilterChange('name')}
                >
                  Project Name
                </button>
                <button 
                  className={`block px-4 py-2 text-sm text-left w-full hover:bg-gray-100 ${filterOption === 'responsible' ? 'bg-gray-100 text-blue-600 font-medium' : ''}`}
                  onClick={() => handleFilterChange('responsible')}
                >
                  Responsible
                </button>
                <button 
                  className={`block px-4 py-2 text-sm text-left w-full hover:bg-gray-100 ${filterOption === 'address' ? 'bg-gray-100 text-blue-600 font-medium' : ''}`}
                  onClick={() => handleFilterChange('address')}
                >
                  Address
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Project Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-10">
        {filteredProjects.map((project) => (
          <ProjectCard key={project.id} project={project} />
        ))}
      </div>
      
      {/* Add New Project Button */}
      <div className="flex justify-end">
        <button
          onClick={handleAddProject}
          className="bg-orange-500 hover:bg-orange-600 text-white font-bold py-3 px-6 rounded-lg transition-colors"
        >
          Add New Project
        </button>
      </div>
    </div>
  );
};

export default ChooseProjectManager;