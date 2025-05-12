// ForgetPW.jsx
import React, { useState } from "react";
import { Link } from "react-router-dom";
import axios from 'axios';
import logoImage from "../images/petro-logo.png";
import SposorImage from "../images/sponsor-logo.png";
import BackgroundImage from "../images/petro-background.png";

export default function ForgetPW() {
    const [email, setEmail] = useState("");
    const [isSubmitted, setIsSubmitted] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setError("");
        
        try {
            // Simulating API call
            await new Promise(r => setTimeout(r, 1000));
            
            // Replace with actual API call
            // const response = await axios.post(
            //     "http://localhost:8000/api/reset-password/",
            //     { email },
            //     { headers: { "Content-Type": "application/json" } }
            // );
            
            setIsSubmitted(true);
        } catch (err) {
            setError("Error sending recovery email. Please try again.");
            console.error("Password recovery error:", err.response?.data || err.message);
        } finally {
            setIsLoading(false);
        }
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
                <img src={logoImage} alt="PetroMonitore Logo" className="h-16" />
            </div>
            
            {/* Recovery Card */}
            <div className="bg-white rounded-lg shadow-lg p-8 w-full max-w-md mx-4">
                <div className="text-center mb-8">
                    <h1 className="text-2xl font-medium text-gray-800">Recover Password</h1>
                </div>
                
                {!isSubmitted ? (
                    <form className="space-y-6" onSubmit={handleSubmit}>
                        <div className="mb-2 text-center">
                            <p className="text-gray-600 text-sm">
                                Enter your email address below and we'll send you a link to reset your password.
                            </p>
                        </div>
                        
                        {/* Email Input */}
                        <div className="relative">
                            <input
                                type="email"
                                placeholder="Enter Email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="w-full bg-gray-100 text-gray-800 rounded-md px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-100"
                                required
                            />
                            {email && (
                                <span 
                                    className="absolute right-3 top-3 text-gray-400 cursor-pointer"
                                    onClick={() => setEmail("")}
                                >
                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" className="w-5 h-5">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                    </svg>
                                </span>
                            )}
                        </div>
                        
                        {error && (
                            <div className="text-red-500 text-sm text-center">
                                {error}
                            </div>
                        )}
                        
                        {/* Submit Button */}
                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full bg-orange-500 hover:bg-orange-600 text-white py-3 px-4 rounded-md transition-colors duration-300 font-medium flex items-center justify-center"
                        >
                            {isLoading ? (
                                <>
                                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                    Processing...
                                </>
                            ) : (
                                "Send Recovery Email"
                            )}
                        </button>
                        
                        {/* Back to Login Link */}
                        <div className="text-center mt-4">
                            <Link to="/login" className="text-sm text-gray-500 hover:text-gray-700">
                                Back to Login
                            </Link>
                        </div>
                    </form>
                ) : (
                    <div className="text-center space-y-6">
                        <div className="flex justify-center">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" className="w-16 h-16 text-green-500">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                        </div>
                        <h2 className="text-xl font-medium text-gray-800">Recovery Email Sent</h2>
                        <p className="text-gray-600">
                            We've sent a password recovery link to <strong>{email}</strong>. Please check your inbox and follow the instructions.
                        </p>
                        <div className="pt-4">
                            <Link 
                                to="/login" 
                                className="inline-block bg-orange-500 hover:bg-orange-600 text-white py-2 px-6 rounded-md transition-colors duration-300 font-medium"
                            >
                                Return to Login
                            </Link>
                        </div>
                    </div>
                )}
            </div>
            
            {/* Sponsor logo in bottom right */}
            <div className="absolute bottom-4 right-4">
                <img src={SposorImage} alt="Sponsor Logo" className="h-12" />
            </div>
        </div>
    );
}