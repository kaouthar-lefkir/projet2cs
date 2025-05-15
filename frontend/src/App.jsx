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
import Dashboard from "./pages/Dashboard"
import ForgetPW from "./pages/ForgetPW";
import ChooseProjectManager from './pages/ChooseProjectManager';
import ChooseProject from './pages/ChooseProject';
import AddProject from "./pages/AddProject";
import ProjectTeam from "./pages/ProjectTeamExpert";
import ProjectTeamManager from "./pages/ProjectTeamManager";
import ProfilePageIngenieur from "./pages/ProfileIngenieur";
import PhasesAndOperations from "./pages/PhasesAndOperationsExpert";
import OperationsContent from "./pages/PhasesAndOperationsManager";
import Rapport from "./pages/Rapport";
import RapportExp from "./pages/RapportExp";
import RapportMan from "./pages/RapportMan";

// Protected route component with sidebar handling
const ProtectedRoute = ({ children, hideSidebar = false }) => {
  const utilisateur = JSON.parse(localStorage.getItem("utilisateur"));
  
  if (!utilisateur) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
};

function AppContent() {
  const location = useLocation();
  const [utilisateur, setUtilisateur] = useState(null);
  
  useEffect(() => {
    const storedUser = localStorage.getItem("utilisateur");
    if (storedUser) {
      setUtilisateur(JSON.parse(storedUser));
    }
  }, []);

  // Paths where sidebar should be hidden
  const hideSidebarPaths = [
    "/login", 
    "/forgetpassword", 
    "/chooseproject", 
    "/chooseprojectmanager"
  ];
  
  // Check if current path is in the hideSidebarPaths list
  const isHiddenPath = hideSidebarPaths.some(path => 
    location.pathname.startsWith(path)
  );
  
  // Show sidebar if user exists and current path is not in hideSidebarPaths
  const showSidebar = utilisateur && !isHiddenPath;
  
  return (
    <div className="flex min-h-screen w-full bg-gray-100">
      {showSidebar && <Sidebar role={utilisateur?.role} />}
      
      <div className={`${showSidebar ? "flex-grow" : "w-full"} overflow-y-auto`}>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/forgetpassword" element={<ForgotPasswordPage />} />
          
          {/* Protected routes */}
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }/>
          
          <Route path="/chooseprojectmanager" element={
            <ProtectedRoute hideSidebar>
              <ChooseProjectManager />
            </ProtectedRoute>
          }/>
          
          <Route path="/chooseproject" element={
            <ProtectedRoute hideSidebar>
              <ChooseProject />
            </ProtectedRoute>
          }/>
          
          <Route path="/details" element={
            <ProtectedRoute>
              <div className="p-6">Details Content</div>
            </ProtectedRoute>
          } />
          
          <Route path="/reports" element={
            <ProtectedRoute>
              <Rapport/>
            </ProtectedRoute>
          } />
          
          

          
          <Route path="/team/expert" element={
            <ProtectedRoute>
              <ProjectTeam />
            </ProtectedRoute>
          } />
          
          <Route path="/team/manager" element={
            <ProtectedRoute>
              <ProjectTeamManager />
            </ProtectedRoute>
          } />
          
          <Route path="/profile" element={
            <ProtectedRoute>
              <ProfilePageIngenieur userId={utilisateur?.id} />
            </ProtectedRoute>
          } />
          
          <Route path="/phases/expert" element={
            <ProtectedRoute>
              <PhasesAndOperations />
            </ProtectedRoute>
          } />
          
          <Route path="/phases/manager" element={
            <ProtectedRoute>
              <OperationsContent />
            </ProtectedRoute>
          } />

          {/* Add a catch-all redirect */}
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