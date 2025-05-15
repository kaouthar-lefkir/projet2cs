import React, { useState, useRef, useEffect } from 'react';
import { Search, Filter, ChevronDown } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
// import axios from 'axios'; // Uncomment this when implementing API calls
import ProjectCard from '../components/ProjectCard';
import logoImage from "../images/petro-logo.png";

// Main Dashboard Component
const ChooseProject = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterOption, setFilterOption] = useState('all');
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const dropdownRef = useRef(null);
  const navigate = useNavigate();
  
  // Load projects on component mount - static for now, Axios commented for later
  useEffect(() => {
    // Simulating data loading
    setLoading(true);
    
    // Static project data for testing
    const staticProjects = [
      {
        id: 1,
        nom: "Petroleum Exploration Phase 1",
        description: "Initial exploration of petroleum deposits in northern region",
        localisation: "Northern Regional District, Zone B",
        budget_initial: 750000.00,
        cout_actuel: 325000.00,
        date_debut: "2025-01-15",
        date_fin_prevue: "2025-07-30",
        date_fin_reelle: null,
        statut: "En cours",
        responsable: 5, // Responsible user ID
        seuil_alerte_cout: 800000.00,
        seuil_alerte_delai: 30,
        date_creation: "2024-12-10T14:30:00",
        // Added Dashboard-specific data
        daysPlanned: 196, // Days between start and planned end date
        daysElapsed: 120, // Example calculation
        costPlanned: 750000.00,
        costUsed: 325000.00,
        progression: 43, // Example percentage
        seuil_vert: 100,
        seuil_jaune: 80,
        seuil_rouge: 60,
        // Sample phases data for this project
        phases: [
          {
            id: 101,
            nom: 'Site Preparation',
            date_debut_prevue: '2025-01-15',
            date_fin_prevue: '2025-02-28',
            date_debut_reelle: '2025-01-20',
            date_fin_reelle: '2025-03-05',
            cout_prevue: 150000,
            cout_reel: 175000,
            progression: 100,
            seuil_vert: 100,
            seuil_jaune: 80,
            seuil_rouge: 60,
          },
          {
            id: 102,
            nom: 'Exploratory Drilling',
            date_debut_prevue: '2025-03-01',
            date_fin_prevue: '2025-05-15',
            date_debut_reelle: '2025-03-10',
            date_fin_reelle: null,
            cout_prevue: 400000,
            cout_reel: 150000,
            progression: 60,
            seuil_vert: 100,
            seuil_jaune: 80,
            seuil_rouge: 60,
          }
        ]
      },
      {
        id: 2,
        nom: "Refinery Upgrade Project",
        description: "Modernization of refinery equipment and safety systems",
        localisation: "Central Processing Facility",
        budget_initial: 1200000.00,
        cout_actuel: 450000.00,
        date_debut: "2024-11-01",
        date_fin_prevue: "2025-09-15",
        date_fin_reelle: null,
        statut: "En cours",
        responsable: 3, // Responsible user ID
        seuil_alerte_cout: 1300000.00,
        seuil_alerte_delai: 45,
        date_creation: "2024-10-05T09:15:00",
        // Added Dashboard-specific data
        daysPlanned: 318, // Days between start and planned end date
        daysElapsed: 195, // Example calculation
        costPlanned: 1200000.00,
        costUsed: 450000.00,
        progression: 38, // Example percentage
        seuil_vert: 100,
        seuil_jaune: 80,
        seuil_rouge: 60,
        // Sample phases data for this project
        phases: [
          {
            id: 201,
            nom: 'Equipment Assessment',
            date_debut_prevue: '2024-11-01',
            date_fin_prevue: '2024-12-15',
            date_debut_reelle: '2024-11-05',
            date_fin_reelle: '2024-12-20',
            cout_prevue: 100000,
            cout_reel: 110000,
            progression: 100,
            seuil_vert: 100,
            seuil_jaune: 80,
            seuil_rouge: 60,
          },
          {
            id: 202,
            nom: 'System Replacement',
            date_debut_prevue: '2025-01-01',
            date_fin_prevue: '2025-04-30',
            date_debut_reelle: '2025-01-10',
            date_fin_reelle: null,
            cout_prevue: 700000,
            cout_reel: 340000,
            progression: 65,
            seuil_vert: 100,
            seuil_jaune: 80,
            seuil_rouge: 60,
          }
        ]
      },
      {
        id: 3,
        nom: "Environmental Impact Assessment",
        description: "Comprehensive environmental study of proposed drilling sites",
        localisation: "Southern Coastal Region",
        budget_initial: 450000.00,
        cout_actuel: 420000.00,
        date_debut: "2024-09-20",
        date_fin_prevue: "2025-03-20",
        date_fin_reelle: "2025-04-05",
        statut: "Terminé",
        responsable: 8, // Responsible user ID
        seuil_alerte_cout: 500000.00,
        seuil_alerte_delai: 15,
        date_creation: "2024-08-30T11:45:00",
        // Added Dashboard-specific data
        daysPlanned: 181, // Days between start and planned end date
        daysElapsed: 198, // Exceeded planned days
        costPlanned: 450000.00,
        costUsed: 420000.00,
        progression: 100, // Completed
        seuil_vert: 100,
        seuil_jaune: 85,
        seuil_rouge: 70,
        // Sample phases data for this project
        phases: [
          {
            id: 301,
            nom: 'Data Collection',
            date_debut_prevue: '2024-09-20',
            date_fin_prevue: '2024-11-30',
            date_debut_reelle: '2024-09-25',
            date_fin_reelle: '2024-12-10',
            cout_prevue: 200000,
            cout_reel: 210000,
            progression: 100,
            seuil_vert: 100,
            seuil_jaune: 85,
            seuil_rouge: 70,
          },
          {
            id: 302,
            nom: 'Analysis & Reporting',
            date_debut_prevue: '2024-12-01',
            date_fin_prevue: '2025-03-20',
            date_debut_reelle: '2024-12-15',
            date_fin_reelle: '2025-04-05',
            cout_prevue: 250000,
            cout_reel: 210000,
            progression: 100,
            seuil_vert: 100,
            seuil_jaune: 85,
            seuil_rouge: 70,
          }
        ]
      },
      {
        id: 4,
        nom: "Pipeline Maintenance",
        description: "Scheduled maintenance and inspection of main transport pipelines",
        localisation: "Eastern Transport Corridor",
        budget_initial: 350000.00,
        cout_actuel: 175000.00,
        date_debut: "2025-02-01",
        date_fin_prevue: "2025-05-15",
        date_fin_reelle: null,
        statut: "En cours",
        responsable: 5, // Responsible user ID
        seuil_alerte_cout: 375000.00,
        seuil_alerte_delai: 10,
        date_creation: "2025-01-15T08:30:00",
        // Added Dashboard-specific data
        daysPlanned: 103, // Days between start and planned end date
        daysElapsed: 74, // Example calculation
        costPlanned: 350000.00,
        costUsed: 175000.00,
        progression: 50, // Example percentage
        seuil_vert: 100,
        seuil_jaune: 80,
        seuil_rouge: 60,
        // Sample phases data for this project
        phases: [
          {
            id: 401,
            nom: 'Inspection',
            date_debut_prevue: '2025-02-01',
            date_fin_prevue: '2025-03-15',
            date_debut_reelle: '2025-02-05',
            date_fin_reelle: '2025-03-20',
            cout_prevue: 150000,
            cout_reel: 155000,
            progression: 100,
            seuil_vert: 100,
            seuil_jaune: 80,
            seuil_rouge: 60,
          },
          {
            id: 402,
            nom: 'Maintenance Work',
            date_debut_prevue: '2025-03-20',
            date_fin_prevue: '2025-05-15',
            date_debut_reelle: '2025-03-25',
            date_fin_reelle: null,
            cout_prevue: 200000,
            cout_reel: 20000,
            progression: 20,
            seuil_vert: 100,
            seuil_jaune: 80,
            seuil_rouge: 60,
          }
        ]
      },
      {
        id: 5,
        nom: "Offshore Platform Inspection",
        description: "Annual safety and structural integrity inspection",
        localisation: "Gulf Delta Platform",
        budget_initial: 280000.00,
        cout_actuel: 290000.00,
        date_debut: "2025-01-10",
        date_fin_prevue: "2025-02-28",
        date_fin_reelle: "2025-03-10",
        statut: "Terminé",
        responsable: 4, // Responsible user ID
        seuil_alerte_cout: 300000.00,
        seuil_alerte_delai: 5,
        date_creation: "2024-12-20T16:00:00",
        // Added Dashboard-specific data
        daysPlanned: 49, // Days between start and planned end date
        daysElapsed: 59, // Exceeded planned days
        costPlanned: 280000.00,
        costUsed: 290000.00,
        progression: 100, // Completed
        seuil_vert: 100,
        seuil_jaune: 90,
        seuil_rouge: 75,
        // Sample phases data for this project
        phases: [
          {
            id: 501,
            nom: 'Safety Inspection',
            date_debut_prevue: '2025-01-10',
            date_fin_prevue: '2025-01-31',
            date_debut_reelle: '2025-01-12',
            date_fin_reelle: '2025-02-05',
            cout_prevue: 130000,
            cout_reel: 140000,
            progression: 100,
            seuil_vert: 100,
            seuil_jaune: 90,
            seuil_rouge: 75,
          },
          {
            id: 502,
            nom: 'Structural Assessment',
            date_debut_prevue: '2025-02-01',
            date_fin_prevue: '2025-02-28',
            date_debut_reelle: '2025-02-08',
            date_fin_reelle: '2025-03-10',
            cout_prevue: 150000,
            cout_reel: 150000,
            progression: 100,
            seuil_vert: 100,
            seuil_jaune: 90,
            seuil_rouge: 75,
          }
        ]
      },
      {
        id: 6,
        nom: "New Drilling Operation",
        description: "Expansion of drilling operations in western field",
        localisation: "Western Field Complex",
        budget_initial: 900000.00,
        cout_actuel: 250000.00,
        date_debut: "2025-03-01",
        date_fin_prevue: "2025-10-30",
        date_fin_reelle: null,
        statut: "En cours",
        responsable: 6, // Responsible user ID
        seuil_alerte_cout: 950000.00,
        seuil_alerte_delai: 20,
        date_creation: "2025-02-15T10:20:00",
        // Added Dashboard-specific data
        daysPlanned: 243, // Days between start and planned end date
        daysElapsed: 75, // Example calculation
        costPlanned: 900000.00,
        costUsed: 250000.00,
        progression: 28, // Example percentage
        seuil_vert: 100,
        seuil_jaune: 80,
        seuil_rouge: 60,
        // Sample phases data for this project
        phases: [
          {
            id: 601,
            nom: 'Site Preparation',
            date_debut_prevue: '2025-03-01',
            date_fin_prevue: '2025-04-15',
            date_debut_reelle: '2025-03-05',
            date_fin_reelle: '2025-04-20',
            cout_prevue: 200000,
            cout_reel: 220000,
            progression: 100,
            seuil_vert: 100,
            seuil_jaune: 80,
            seuil_rouge: 60,
          },
          {
            id: 602,
            nom: 'Initial Drilling',
            date_debut_prevue: '2025-04-20',
            date_fin_prevue: '2025-07-15',
            date_debut_reelle: '2025-04-25',
            date_fin_reelle: null,
            cout_prevue: 400000,
            cout_reel: 30000,
            progression: 15,
            seuil_vert: 100,
            seuil_jaune: 80,
            seuil_rouge: 60,
          }
        ]
      },
    ];
    
    setProjects(staticProjects);
    setLoading(false);
    
    // AXIOS IMPLEMENTATION FOR LATER USE
    // Uncomment this section when ready to fetch from API
    /*
    const fetchProjects = async () => {
      try {
        const userId = localStorage.getItem('utilisateur_id'); // Get user ID from localStorage or auth context
        const response = await axios.get(`/api/projects/user/${userId}`);
        
        // Add dashboard-specific data to projects
        const enhancedProjects = response.data.map(project => {
          // Calculate days planned (between start and planned end date)
          const startDate = new Date(project.date_debut);
          const plannedEndDate = new Date(project.date_fin_prevue);
          const daysPlanned = Math.ceil((plannedEndDate - startDate) / (1000 * 60 * 60 * 24));
          
          // Calculate days elapsed (between start and today or end date if completed)
          const today = new Date();
          const endDate = project.date_fin_reelle ? new Date(project.date_fin_reelle) : today;
          const daysElapsed = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24));
          
          // Calculate progression if not already provided
          const progression = project.progression || Math.min(
            Math.round((daysElapsed / daysPlanned) * 100), 
            project.statut === "Terminé" ? 100 : 99
          );
          
          return {
            ...project,
            daysPlanned,
            daysElapsed,
            costPlanned: project.budget_initial,
            costUsed: project.cout_actuel,
            progression,
            seuil_vert: 100,
            seuil_jaune: 80,
            seuil_rouge: 60,
          };
        });
        
        setProjects(enhancedProjects);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching projects:', error);
        setLoading(false);
      }
    };
    
    fetchProjects();
    */
  }, []);

  const handleProjectClick = (project) => {
    // Navigate to dashboard with the selected project data (using state)
    navigate(`/dashboard/${project.id}`, { state: { projectData: project } });
  };

  // Filter projects based on search term and filter option
  const filteredProjects = projects.filter(project => {
    const searchLower = searchTerm.toLowerCase();
    
    switch(filterOption) {
      case 'name':
        return project.nom.toLowerCase().includes(searchLower);
      case 'responsible':
        // Since responsable is now just an ID, we'd need to get the actual name
        // For now, just filter by ID
        return String(project.responsable).includes(searchLower);
      case 'address':
        return project.localisation.toLowerCase().includes(searchLower);
      case 'all':
      default:
        return (
          project.nom.toLowerCase().includes(searchLower) ||
          String(project.responsable).includes(searchLower) ||
          project.localisation.toLowerCase().includes(searchLower) ||
          project.description.toLowerCase().includes(searchLower)
        );
    }
  });

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
  };

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
      
      {/* Loading State */}
      {loading ? (
        <div className="text-center py-8">
          <p className="text-gray-600">Loading projects...</p>
        </div>
      ) : (
        /* Project Cards Grid */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-10">
          {filteredProjects.length > 0 ? (
            filteredProjects.map((project) => (
              <ProjectCard 
                key={project.id} 
                project={project} 
                onClick={() => handleProjectClick(project)}
              />
            ))
          ) : (
            <div className="col-span-3 text-center py-8">
              <p className="text-gray-600">No projects found matching your search criteria.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ChooseProject;