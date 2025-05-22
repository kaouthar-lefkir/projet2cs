import { useState, useEffect } from 'react';
import { User, ArrowLeft } from 'lucide-react';

export default function ProfilePage({ userId, onBackClick }) {
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
  
  useEffect(() => {
   
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
    
    if (userId && mockUsers[userId]) {
      setUserData(mockUsers[userId]);
    } else {
      // Valeurs par défaut ou gestion d'erreur
      console.log("Utilisateur non trouvé");
    }
  }, [userId]);

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

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* En-tête */}
      <div className="bg-white shadow-sm p-4 flex justify-between items-center">
        <h1 className="text-xl font-semibold text-gray-800">Profil Utilisateur</h1>
        <button 
          onClick={onBackClick}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors flex items-center gap-2"
        >
          <ArrowLeft size={16} />
          Retour à la liste
        </button>
      </div>
      
      {/* Contenu */}
      <div className="flex-1 p-8">
        <div className="bg-white rounded-lg shadow-sm p-8 max-w-4xl mx-auto">
          <div className="flex flex-col md:flex-row items-center md:items-start gap-8">
            {/* Photo de profil */}
            <div className="flex-shrink-0">
              <div className="relative w-32 h-32 rounded-full overflow-hidden bg-gray-100 flex items-center justify-center">
                <User size={64} className="text-gray-400" />
              </div>
            </div>
            
            {/* Informations utilisateur */}
            <div className="flex-grow space-y-6 w-full">
              <h1 className="text-2xl font-bold text-gray-800">{userData.prenom} {userData.nom}</h1>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <h3 className="text-sm font-medium text-gray-500">ID</h3>
                    <p className="mt-1 text-base text-gray-900">{userData.id}</p>
                  </div>
                  
                  <div>
                    <h3 className="text-sm font-medium text-gray-500">Prénom</h3>
                    <p className="mt-1 text-base text-gray-900">{userData.prenom}</p>
                  </div>
                  
                  <div>
                    <h3 className="text-sm font-medium text-gray-500">Nom</h3>
                    <p className="mt-1 text-base text-gray-900">{userData.nom}</p>
                  </div>
                  
                  <div>
                    <h3 className="text-sm font-medium text-gray-500">Email</h3>
                    <p className="mt-1 text-base text-gray-900">{userData.email}</p>
                  </div>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <h3 className="text-sm font-medium text-gray-500">Rôle</h3>
                    <p className="mt-1 text-base text-gray-900">{userData.role}</p>
                  </div>
                  
                  <div>
                    <h3 className="text-sm font-medium text-gray-500">Date de création</h3>
                    <p className="mt-1 text-base text-gray-900">{formatDate(userData.date_creation)}</p>
                  </div>
                  
                  <div>
                    <h3 className="text-sm font-medium text-gray-500">Statut</h3>
                    <p className="mt-1 text-base text-gray-900">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        userData.statut === 'Actif' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {userData.statut}
                      </span>
                    </p>
                  </div>
                  
                  <div>
                    <h3 className="text-sm font-medium text-gray-500">Mot de passe</h3>
                    <p className="mt-1 text-base text-gray-900">{userData.mot_de_passe}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}