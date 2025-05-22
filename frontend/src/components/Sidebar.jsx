import React, { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { FiMenu, FiX } from "react-icons/fi";
import { 
  RiDashboardLine, 
  RiFileList3Line, 
  RiTimeLine, 
  RiTeamLine, 
  RiUserLine, 
  RiLogoutBoxLine 
} from "react-icons/ri";
import logoImage from "../images/petro-logo.png";

const Sidebar = ({ role }) => {
  const [isOpen, setIsOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
  localStorage.removeItem("utilisateur");
  window.location.href = "/login";
};

  const menuItems = {
    TOP_MANAGEMENT: [
      { label: "Dashboard", icon: <RiDashboardLine className="text-xl" />, path: "/dashboard" },
      { label: "Details", icon: <RiFileList3Line className="text-xl" />, path: "/details" },
      { label: "Phases", icon: <RiTimeLine className="text-xl" />, path: "/phases/manager" },
      { label: "Reports", icon: <RiFileList3Line className="text-xl" />, path: "/reports/manager" },
      { label: "Project Team", icon: <RiTeamLine className="text-xl" />, path: "/team/manager" }
    ],
    INGENIEUR_TERRAIN: [
      { label: "Rapport", icon: <RiFileList3Line className="text-xl" />, path: "/reports/ingenieur" },
      { label: "Profile", icon: <RiUserLine className="text-xl" />, path: "/profile" }
    ],
    EXPERT: [
      { label: "Dashboard", icon: <RiDashboardLine className="text-xl" />, path: "/dashboard" },
      { label: "Details", icon: <RiFileList3Line className="text-xl" />, path: "/details" },
      { label: "Phases", icon: <RiTimeLine className="text-xl" />, path: "/phases/expert" },
      { label: "Reports", icon: <RiFileList3Line className="text-xl" />, path: "/reports/expert" },
      { label: "Project Team", icon: <RiTeamLine className="text-xl" />, path: "/team/expert" }
    ],
  };

  const footerItems = [
    { label: "Déconnexion", icon: <RiLogoutBoxLine className="text-xl" />, onClick: handleLogout },
  ];

  const getItemClass = (path) => {
    const isActive = location.pathname === path;
    return `px-4 py-3 rounded-lg flex items-center gap-3 cursor-pointer transition-colors ${
      isActive
        ? "text-blue-600 bg-blue-50"
        : "text-gray-400 hover:text-blue-600 hover:bg-blue-50"
    }`;
  };

  const getIconClass = (isActive) => {
    return isActive ? "text-blue-600" : "text-gray-400 group-hover:text-blue-600";
  };

  const renderMenuItem = (item, isMobile = false) => {
    const isActive = location.pathname === item.path;
    
    return (
      <div 
        key={item.label} 
        className={`group ${getItemClass(item.path)}`}
        onClick={() => {
          if (item.onClick) {
            item.onClick();
          } else if (item.path) {
            navigate(item.path);
            if (isMobile) setIsOpen(false);
          }
        }}
      >
        <div className={getIconClass(isActive)}>
          {item.icon}
        </div>
        <span className="flex-grow text-sm font-medium">{item.label}</span>
      </div>
    );
  };

  const renderMenu = (isMobile = false, section = "main") => {
    const itemsToRender =
      section === "main" ? menuItems[role] || [] : footerItems;
    
    return (
      <div className="w-full space-y-1">
        {itemsToRender.map((item) => renderMenuItem(item, isMobile))}
      </div>
    );
  };

  return (
    <>
     {/* Desktop Sidebar */}
     <div className="hidden sm:flex flex-col w-64 bg-white border-r border-gray-200 shadow-sm sidebar-container">
        <div className="flex justify-center items-center h-20 border-b border-gray-200">
          <div className="flex items-center">
            <img 
              src={logoImage} 
              alt="PetroMonitore" 
              className="h-20"
            />
          </div>
        </div>
        
        <div className="flex flex-col justify-between h-[calc(100vh-5rem)] p-4 overflow-y-auto">
          <div className="relative">
            {location.pathname && (
              <div 
                className="absolute left-0 w-1 h-12 bg-blue-600 rounded-r-md"
                style={{
                  top: menuItems[role]?.findIndex(item => item.path === location.pathname) * 48 + 24,
                  transform: 'translateY(-50%)',
                  display: menuItems[role]?.findIndex(item => item.path === location.pathname) > -1 ? 'block' : 'none'
                }}
              />
            )}
            <div className="space-y-6">
              {renderMenu(false, "main")}
            </div>
          </div>
          
          <div className="pt-6 border-t border-gray-200 mt-6">
            {renderMenu(false, "footer")}
          </div>
        </div>
      </div>

      {/* Mobile button */}
      <div className="sm:hidden fixed top-4 right-4 z-50">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="bg-white p-2 rounded-md text-gray-600 shadow-md focus:outline-none"
        >
          {isOpen ? <FiX size={24} /> : <FiMenu size={24} />}
        </button>
      </div>

      {/* Mobile Sidebar */}
      {isOpen && (
        <div className="sm:hidden fixed inset-0 bg-white z-40 flex flex-col">
          <div className="flex items-center justify-center h-20 border-b border-gray-200">
            <div className="flex items-center">
              <img 
               src={logoImage}
                alt="PetroMonitore" 
                className="h-20"
              />
            </div>
          </div>
          
          <div className="flex flex-col justify-between flex-grow p-4 overflow-y-auto">
            <div className="space-y-6">
              {renderMenu(true, "main")}
            </div>
            
            <div className="pt-6 border-t border-gray-200 mt-6">
              {renderMenu(true, "footer")}
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default Sidebar;