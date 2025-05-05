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

function AppContent({ role, setRole }) {
  const location = useLocation();
  
  // All routes will show sidebar since we're bypassing login
  return (
    <div className="flex flex-col sm:flex-row bg-bleu_bg">
      <Sidebar role={role} />
      <div className="flex-grow">
        <Routes>
          {/* Redirect root to dashboard */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          
          {/* Keep these routes accessible if needed */}
          <Route path="/login" element={<Login />} />
          <Route path="/forgetpassword" element={<ForgotPasswordPage />} />
          
          <Route path="/dashboard" element= {<Dashboard/>}/>
          <Route path="/details" element={<div className="p-6">Details Content</div>} />
          <Route path="/phases" element={<div className="p-6">Phases Content</div>} />
          <Route path="/reports" element={<div className="p-6">Reports Content</div>} />
          <Route path="/team" element={<div className="p-6">Team Content</div>} />
          
          {/* Add a catch-all redirect */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </div>
    </div>
  );
}

function App() {
  // Hard-code the role as "admin" - no need for useState or useEffect
  
  
  // Setup mock user data in localStorage to prevent issues with components
  // that might check for authentication
 
  
  return (
    <GoogleOAuthProvider clientId="318367454563-v857090khdr2rk94jff2apmh0ifq7irh.apps.googleusercontent.com">
      <Router>
       <Login/>
      </Router>
    </GoogleOAuthProvider>
  );
}

export default App;