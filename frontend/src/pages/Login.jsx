// LoginPage.jsx
import React, { useState } from "react";
import { Link } from "react-router-dom";
import { GoogleLogin } from '@react-oauth/google';
import axios from 'axios';
import logoImage from "../images/petro-logo.png";
import SposorImage from "../images/sponsor-logo.png";
import BackgroundImage from "../images/petro-background.png";

export default function LoginPage() {
    const [showPassword, setShowPassword] = useState(false);

    const togglePasswordVisibility = () => {
        setShowPassword(!showPassword);
    };

    return (
        <div className="min-h-screen flex items-center justify-center" 
             style={{ 
                backgroundImage: `url(${BackgroundImage})`, 
                backgroundRepeat: "no-repeat",
                backgroundPosition: "center",
                backgroundSize: "100% 100%"
             }}>
            
            {/* Logo in top right corner */}
            <div className="absolute top-4 right-4">
                <img src={logoImage } alt="PetroMonitore Logo" className="h-16" />
            </div>
            
            {/* Login Card */}
            <div className="bg-white rounded-lg shadow-lg p-8 w-full max-w-md mx-4">
                <div className="text-center mb-8">
                    <h1 className="text-2xl font-medium text-gray-800">Sign In</h1>
                </div>
                
                <form className="space-y-6">
                    {/* Email Input */}
                    <div className="relative">
                        <input
                            type="email"
                            placeholder="Enter Email"
                            className="w-full bg-gray-100 text-gray-800 rounded-md px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-100"
                        />
                        <span className="absolute right-3 top-3 text-gray-400 cursor-pointer">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" className="w-5 h-5">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </span>
                    </div>
                    
                    {/* Password Input */}
                    <div className="relative">
                        <input
                            type={showPassword ? "text" : "password"}
                            placeholder="••••••••"
                            className="w-full bg-gray-100 text-gray-800 rounded-md px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-100"
                        />
                        <span className="absolute right-3 top-3 text-gray-400 cursor-pointer" onClick={togglePasswordVisibility}>
                            {showPassword ? (
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" className="w-5 h-5">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                                </svg>
                            ) : (
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" className="w-5 h-5">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                                </svg>
                            )}
                        </span>
                    </div>
                    
                    {/* Recover Password Link */}
                    <div className="text-right">
                        <Link to="/recover-password" className="text-sm text-gray-500 hover:text-gray-700">
                            Recover Password ?
                        </Link>
                    </div>
                    
                    {/* Sign In Button */}
                    <button
                        type="submit"
                        className="w-full bg-orange-500 hover:bg-orange-600 text-white py-3 px-4 rounded-md transition-colors duration-300 font-medium"
                    >
                        Sign In
                    </button>
                </form>
                
                {/* Optional: Google Login */}
                <div className="mt-6">
                    <div className="flex items-center justify-center my-4">
                        <div className="border-t border-gray-300 w-1/3" />
                        <span className="mx-2 text-gray-500 text-sm">Or sign in with</span>
                        <div className="border-t border-gray-300 w-1/3" />
                    </div>
                    
                    <div className="flex justify-center">
                        <GoogleLogin
                            clientId="318367454563-v857090khdr2rk94jff2apmh0ifq7irh.apps.googleusercontent.com"
                            onSuccess={async (credentialResponse) => {
                                const { credential } = credentialResponse;
                                if (!credential) return;

                                try {
                                    const response = await axios.post(
                                        "http://localhost:8000/api/google-login/",
                                        { token: credential },
                                        { headers: { "Content-Type": "application/json" } }
                                    );

                                    const data = response.data;
                                    console.log("Backend response:", data);

                                    if (data.success) {
                                        localStorage.setItem("user", JSON.stringify(data));
                                        
                                        if (data.user_type === "rh") {
                                            window.location.href = "/rh/dashboard";
                                        } else {
                                            window.location.href = "/employee/demande";
                                        }
                                    }
                                } catch (err) {
                                    console.error("Authentication error:", err.response?.data || err.message);
                                }
                            }}
                            onError={() => {
                                console.error("Google authentication failed");
                            }}
                            useOneTap
                        />
                    </div>
                </div>
            </div>
            
            {/* Sponsor logo in bottom right */}
            <div className="absolute bottom-4 right-4">
                <img src={SposorImage} alt="Sponsor Logo" className="h-12" />
            </div>
        </div>
    );
}