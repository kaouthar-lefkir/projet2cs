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
import AddProject from "./pages/AddProject";
import ProjectTeam from "./pages/ProjectTeamExpert";
import ProjectTeamManager from "./pages/ProjectTeamManager";
import ProfilePageIngenieur from "./pages/ProfileIngenieur";
import  PhasesAndOperations from "./pages/PhasesAndOperationsExpert";
import OperationsContent from "./pages/PhasesAndOperationsManager";
function AppContent({ role, setRole }) {
  const location = useLocation();
  
  return (
    <div className="flex min-h-screen w-full bg-gray-100">
      <Sidebar role={role} />
      <div className="flex-grow overflow-y-auto">
        <Routes>
          {/* Redirect root to dashboard */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          
          {/* Keep these routes accessible if needed */}
          <Route path="/login" element={<Login />} />
          <Route path="/forgetpassword" element={<ForgotPasswordPage />} />
          
          <Route path="/dashboard" element={<Dashboard/>}/>
          <Route path="/details" element={<div className="p-6">Details Content</div>} />
          <Route path="/reports" element={<div className="p-6">Reports Content</div>} />
          <Route path="/team/expert" element={<ProjectTeam/>} />
          <Route path="/team/manager" element={<ProjectTeamManager/>} />
          <Route path="/profile" element={<ProfilePageIngenieur userId={"#12548796"}/>} />
          <Route path="/phases/expert" element={<PhasesAndOperations/>} />
            <Route path="/phases/manager" element={<OperationsContent />} />


          {/* Add a catch-all redirect */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </div>
    </div>
  );
}

function App() {
  return (
    <GoogleOAuthProvider clientId="318367454563-v857090khdr2rk94jff2apmh0ifq7irh.apps.googleusercontent.com">
      <Router>
        <AppContent role={"expert"}/> 
  
      </Router>
    </GoogleOAuthProvider>
  );
}


export default App;