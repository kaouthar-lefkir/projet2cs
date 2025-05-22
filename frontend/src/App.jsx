import React, { useState, useEffect } from "react";
import { GoogleOAuthProvider } from '@react-oauth/google';
import {
  BrowserRouter as Router,
  Route,
  Routes,
  useLocation,
  Navigate
} from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Login from "./pages/Login";
import "./App.css";
import ForgotPasswordPage from "./pages/ForgetPW";
import Dashboard from "./pages/Dashboard";
import ChooseProjectManager from './pages/ChooseProjectManager';
import ChooseProject from './pages/ChooseProject';
import AddProject from "./pages/AddProject";
import ProjectTeam from "./pages/ProjectTeamExpert";
import ProjectTeamManager from "./pages/ProjectTeamManager";
import ProfilePageIngenieur from "./pages/ProfileIngenieur";
import PhasesAndOperationsExpert from "./pages/PhasesAndOperationsExpert";
import OperationsContent from "./pages/PhasesAndOperationsManager";
import Rapport from "./pages/Rapport";
import RapportExp from "./pages/RapportExp";
import RapportMan from "./pages/RapportMan";
import AjouterRapport from "./pages/AjouterRapport";

const ProtectedRoute = ({ children, hideSidebar = false, allowedRoles = [] }) => {
  const utilisateur = JSON.parse(localStorage.getItem("utilisateur"));
  if (!utilisateur) return <Navigate to="/login" replace />;
  if (allowedRoles.length > 0 && !allowedRoles.includes(utilisateur.role)) return <Navigate to="/login" replace />;
  return children;
};

function AppContent() {
  const location = useLocation();
  const [utilisateur, setUtilisateur] = useState(null);

  useEffect(() => {
    const loadUser = () => {
      const storedUser = localStorage.getItem("utilisateur");
      if (storedUser) setUtilisateur(JSON.parse(storedUser));
    };

    loadUser(); // Initial load
    window.addEventListener("storage", loadUser); // ✅ Listen to login updates

    return () => {
      window.removeEventListener("storage", loadUser);
    };
  }, []);

  const hideSidebarPaths = ["/login", "/forgetpassword", "/chooseproject", "/chooseprojectmanager"];
  const isHiddenPath = hideSidebarPaths.some(path => location.pathname.startsWith(path));
  const validRoles = ['TOP_MANAGEMENT', 'EXPERT', 'INGENIEUR_TERRAIN'];
  const showSidebar = utilisateur && validRoles.includes(utilisateur?.role) && !isHiddenPath;

  return (
    <div className="flex min-h-screen w-full bg-gray-100">
      {showSidebar && <Sidebar role={utilisateur?.role} />}
      <div className={`${showSidebar ? "flex-grow" : "w-full"} overflow-y-auto`}>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/forgetpassword" element={<ForgotPasswordPage />} />
          <Route path="/dashboard" element={<ProtectedRoute allowedRoles={['TOP_MANAGEMENT', 'EXPERT']}><Dashboard /></ProtectedRoute>} />
          <Route path="/chooseprojectmanager" element={<ProtectedRoute hideSidebar allowedRoles={['TOP_MANAGEMENT']}><ChooseProjectManager /></ProtectedRoute>} />
          <Route path="/add-rapport" element={<ProtectedRoute><AjouterRapport /></ProtectedRoute>} />
          <Route path="/chooseproject" element={<ProtectedRoute hideSidebar allowedRoles={['EXPERT', 'INGENIEUR_TERRAIN']}><ChooseProject /></ProtectedRoute>} />
          <Route path="/details" element={<ProtectedRoute><div className="p-6">Details Content</div></ProtectedRoute>} />
          <Route path="/reports/ingenieur" element={<ProtectedRoute allowedRoles={['INGENIEUR_TERRAIN']}><Rapport /></ProtectedRoute>} />
          <Route path="/reports/manager" element={<ProtectedRoute allowedRoles={['TOP_MANAGEMENT']}><RapportMan /></ProtectedRoute>} />
          <Route path="/reports/expert" element={<ProtectedRoute allowedRoles={['EXPERT']}><RapportExp /></ProtectedRoute>} />
          <Route path="/team/expert" element={<ProtectedRoute allowedRoles={['EXPERT']}><ProjectTeam /></ProtectedRoute>} />
          <Route path="/team/manager" element={<ProtectedRoute allowedRoles={['TOP_MANAGEMENT']}><ProjectTeamManager /></ProtectedRoute>} />
          <Route path="/profile" element={<ProtectedRoute allowedRoles={['TOP_MANAGEMENT', 'EXPERT', 'INGENIEUR_TERRAIN']}><ProfilePageIngenieur userId={utilisateur?.id} /></ProtectedRoute>} />
          <Route path="/phases/expert" element={<ProtectedRoute allowedRoles={['EXPERT']}><PhasesAndOperationsExpert /></ProtectedRoute>} />
          <Route path="/phases/manager" element={<ProtectedRoute allowedRoles={['TOP_MANAGEMENT']}><OperationsContent /></ProtectedRoute>} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </div>
    </div>
  );
}

function App() {
  return (
    <GoogleOAuthProvider clientId="318367454563-v857090khdr2rk94jff2apmh0ifq7irh.apps.googleusercontent.com">
      <Router>
        <AppContent />
      </Router>
    </GoogleOAuthProvider>
  );
}

export default App;
