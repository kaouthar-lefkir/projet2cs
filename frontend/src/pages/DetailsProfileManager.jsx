import { useState, useEffect } from 'react';
import { User, ArrowLeft, Edit2, Save, X } from 'lucide-react';

export default function ProfilePageManager({ userId, onBackClick }) {
  // État pour stocker les données utilisateur
  const [userData, setUserData] = useState({
    id: '',
    nom: '',
    prenom: '',
    email: '',
    mot_de_passe: '••••••••', 
    role: '',
    date_creation: '',
    statut: 'Actif'
  });

  // État pour les projets de l'utilisateur
  const [userProjects, setUserProjects] = useState([]);
  
  // État pour le mode édition
  const [isEditing, setIsEditing] = useState(false);
  
  // État temporaire pour stocker les modifications
  const [editData, setEditData] = useState({});

  useEffect(() => {
    // Données utilisateur simulées
    const mockUsers = {
      "#12548796": {
        id: "#12548796",
        nom: "Bator",
        prenom: "Livia",
        email: "livia.bator@example.com",
        mot_de_passe: "••••••••",
        role: "Eng terrain",
        date_creation: "2024-01-28T12:30:00",
        statut: "Actif"
      },
      "#12548797": {
        id: "#12548797",
        nom: "Martin",
        prenom: "Alex",
        email: "alex.martin@example.com",
        mot_de_passe: "••••••••",
        role: "Architect",
        date_creation: "2024-01-18T09:15:00",
        statut: "Actif"
      },
      "#12548798": {
        id: "#12548798",
        nom: "Chen",
        prenom: "Sarah",
        email: "sarah.chen@example.com",
        mot_de_passe: "••••••••",
        role: "Project Manager",
        date_creation: "2024-01-15T14:40:00",
        statut: "Actif"
      }
    };
    
    // Projets simulés
    const mockProjects = [
      {
        projectName: "Project 1",
        projectID: "#12548796",
        type: "Shopping",
        enrollmentDate: "2024-01-28T12:30:00"
      },
      {
        projectName: "Project 2",
        projectID: "#12548796",
        type: "Approvis",
        enrollmentDate: "2024-01-25T10:40:00"
      },
      {
        projectName: "Project 3",
        projectID: "#12548796",
        type: "Service",
        enrollmentDate: "2024-01-20T10:40:00"
      },
      {
        projectName: "Project 4",
        projectID: "#12548796",
        type: "Transfer",
        enrollmentDate: "2024-01-15T03:29:00"
      },
      {
        projectName: "Project 5",
        projectID: "#12548796",
        type: "Transfer",
        enrollmentDate: "2024-01-14T10:40:00"
      }
    ];
    
    if (userId && mockUsers[userId]) {
      setUserData(mockUsers[userId]);
      setEditData(mockUsers[userId]);
      setUserProjects(mockProjects);
    } else {
      // Valeurs par défaut ou gestion d'erreur
      console.log("Utilisateur non trouvé");
    }
  }, [userId]);

  // Gestion du changement dans les champs de formulaire
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setEditData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Sauvegarder les modifications
  const saveChanges = () => {
    setUserData(editData);
    setIsEditing(false);
  };

  // Annuler les modifications
  const cancelEdit = () => {
    setEditData(userData);
    setIsEditing(false);
  };

  // Formatage de la date
  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('fr-FR', {
      day: '2-digit',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };

  // Format date court (pour les projets)
  const formatShortDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    const day = date.getDate();
    const month = date.toLocaleString('en-US', { month: 'short' });
    const hours = date.getHours();
    const minutes = date.getMinutes().toString().padStart(2, '0');
    const ampm = hours >= 12 ? 'PM' : 'AM';
    const formattedHours = hours % 12 || 12;
    
    return `${day} ${month}, ${formattedHours}:${minutes} ${ampm}`;
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* En-tête fixe */}
      <div className="bg-white shadow-sm p-4 flex justify-between items-center">
        <h1 className="text-xl font-semibold text-gray-800">Profile</h1>
        <button 
          onClick={onBackClick}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors flex items-center gap-2"
        >
          <ArrowLeft size={16} />
          Retour à la liste
        </button>
      </div>
      
      {/* Contenu scrollable avec fond fixe */}
      <div className="flex-1 p-6 overflow-y-auto bg-gray-50">
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex flex-col md:flex-row items-center md:items-start gap-8">
            {/* Photo de profil */}
            <div className="flex-shrink-0">
              <div className="relative w-32 h-32 rounded-full overflow-hidden bg-gray-100 flex items-center justify-center">
                <User size={64} className="text-gray-400" />
              </div>
            </div>
            
            {/* Informations utilisateur */}
            <div className="flex-grow space-y-6 w-full">
              <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold text-gray-800">{userData.prenom} {userData.nom}</h1>
                {isEditing ? (
                  <div className="flex gap-2">
                    <button 
                      onClick={saveChanges}
                      className="p-2 bg-green-500 text-white rounded hover:bg-green-600"
                    >
                      <Save size={18} />
                    </button>
                    <button 
                      onClick={cancelEdit}
                      className="p-2 bg-red-500 text-white rounded hover:bg-red-600"
                    >
                      <X size={18} />
                    </button>
                  </div>
                ) : (
                  <button 
                    onClick={() => setIsEditing(true)}
                    className="p-2 bg-gray-100 text-gray-600 rounded hover:bg-gray-200"
                  >
                    <Edit2 size={18} />
                  </button>
                )}
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-sm font-medium text-gray-500">Username</h3>
                      {isEditing ? (
                        <input
                          type="text"
                          name="prenom"
                          value={editData.prenom}
                          onChange={handleInputChange}
                          className="mt-1 p-2 border rounded w-full"
                        />
                      ) : (
                        <p className="mt-1 text-base text-gray-900">{userData.prenom} {userData.nom}</p>
                      )}
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="text-sm font-medium text-gray-500">User ID</h3>
                    <p className="mt-1 text-base text-gray-900">{userData.id}</p>
                  </div>
                  
                  <div>
                    <h3 className="text-sm font-medium text-gray-500">Field</h3>
                    {isEditing ? (
                      <input
                        type="text"
                        name="role"
                        value={editData.role}
                        onChange={handleInputChange}
                        className="mt-1 p-2 border rounded w-full"
                      />
                    ) : (
                      <p className="mt-1 text-base text-gray-900">{userData.role}</p>
                    )}
                  </div>
                </div>
                
                <div className="space-y-4">  
                  <div>
                    <h3 className="text-sm font-medium text-gray-500">Date</h3>
                    <p className="mt-1 text-base text-gray-900">{formatShortDate(userData.date_creation)}</p>
                  </div>
                  
                  <div>
                    <h3 className="text-sm font-medium text-gray-500">Email</h3>
                    {isEditing ? (
                      <input
                        type="email"
                        name="email"
                        value={editData.email}
                        onChange={handleInputChange}
                        className="mt-1 p-2 border rounded w-full"
                      />
                    ) : (
                      <p className="mt-1 text-base text-gray-900">{userData.email}</p>
                    )}
                  </div>
                  
                  <div>
                    <h3 className="text-sm font-medium text-gray-500">Status</h3>
                    {isEditing ? (
                      <select
                        name="statut"
                        value={editData.statut}
                        onChange={handleInputChange}
                        className="mt-1 p-2 border rounded w-full"
                      >
                        <option value="Actif">Actif</option>
                        <option value="Inactif">Inactif</option>
                      </select>
                    ) : (
                      <p className="mt-1 text-base text-gray-900">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          userData.statut === 'Actif' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                        }`}>
                          {userData.statut}
                        </span>
                      </p>
                    )}
                  </div>
                </div>
              </div>
              
            
            </div>
          </div>
        </div>
        
        {/* Liste des projets */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-6">Projects</h2>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    ProjectName
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    ProjectID
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    enrollment date
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {userProjects.map((project, index) => (
                  <tr key={index}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {project.projectName}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {project.projectID}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {project.type}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatShortDate(project.enrollmentDate)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}