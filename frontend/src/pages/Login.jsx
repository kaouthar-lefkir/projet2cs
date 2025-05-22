// LoginPage.jsx
import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import logoImage from "../images/petro-logo.png";
import SposorImage from "../images/sponsor-logo.png";
import BackgroundImage from "../images/petro-background.png";

export default function LoginPage() {
    const [showPassword, setShowPassword] = useState(false);
    const [email, setEmail] = useState("");
    const [mot_de_passe, setMot_de_passe] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const togglePasswordVisibility = () => {
        setShowPassword(!showPassword);
    };

    const handleLogin = async (e) => {
        e.preventDefault();
        setError("");
        setLoading(true);
        
        try {
            if (!email || !mot_de_passe) {
                setError("Please fill in all fields");
                setLoading(false);
                return;
            }

            let role = "EXPERT";
            let nom = "User";
            let prenom = "Test";
            
            if (email.toLowerCase().includes("manager") || email.toLowerCase().includes("top")) {
                role = "TOP_MANAGEMENT";
                nom = "Manager";
                prenom = "Top";
            } else if (email.toLowerCase().includes("engineer") || email.toLowerCase().includes("terrain")) {
                role = "INGENIEUR_TERRAIN";
                nom = "Engineer";
                prenom = "Field";
            } else if (email.toLowerCase().includes("expert")) {
                role = "EXPERT";
                nom = "Expert";
                prenom = "Technical";
            }
            
            const utilisateur = {
                id: Math.floor(Math.random() * 1000) + 100,
                nom: nom,
                prenom: prenom,
                email: email,
                role: role,
                date_creation: new Date().toISOString(),
                statut: "ACTIF"
            };
            
            localStorage.setItem("utilisateur", JSON.stringify(utilisateur));
            localStorage.setItem("utilisateur_id", utilisateur.id.toString());

            // ✅ Notify other components of login
            window.dispatchEvent(new Event("storage"));

            if (utilisateur.role === "TOP_MANAGEMENT") {
                navigate("/chooseprojectmanager", { replace: true });
            } else {
                navigate("/chooseproject", { replace: true });
            }

            setLoading(false);
        } catch (err) {
            console.error("Login error:", err);
            setError("An unexpected error occurred. Please try again.");
            setLoading(false);
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
            <div className="absolute top-4 right-4">
                <img src={logoImage} alt="PetroMonitore Logo" className="h-16" />
            </div>

            <div className="bg-white rounded-lg shadow-lg p-8 w-full max-w-md mx-4">
                <div className="text-center mb-8">
                    <h1 className="text-2xl font-medium text-gray-800">Sign In</h1>
                    <p className="text-sm text-gray-600 mt-2">Enter your credentials to access your account</p>
                </div>

                {error && (
                    <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                        {error}
                    </div>
                )}

                <div className="bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded mb-4 text-sm">
                    <p className="font-medium mb-1">Test Accounts:</p>
                    <p>• manager@test.com - Top Management</p>
                    <p>• engineer@test.com - Field Engineer</p>
                    <p>• expert@test.com - Expert</p>
                    <p className="mt-1 text-xs">Password: any text</p>
                </div>

                <form className="space-y-6" onSubmit={handleLogin}>
                    <div className="relative">
                        <input
                            type="email"
                            placeholder="Enter Email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="w-full bg-gray-100 text-gray-800 rounded-md px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-100"
                            required
                            disabled={loading}
                        />
                        {email && !loading && (
                            <span className="absolute right-3 top-3 text-gray-400 cursor-pointer"
                                  onClick={() => setEmail("")}>
                                <svg xmlns="http://www.w3.org/2000/svg"
                                     fill="none" viewBox="0 0 24 24"
                                     stroke="currentColor" className="w-5 h-5">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                          d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </span>
                        )}
                    </div>

                    <div className="relative">
                        <input
                            type={showPassword ? "text" : "password"}
                            placeholder="••••••••"
                            value={mot_de_passe}
                            onChange={(e) => setMot_de_passe(e.target.value)}
                            className="w-full bg-gray-100 text-gray-800 rounded-md px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-100"
                            required
                            disabled={loading}
                        />
                        <span className="absolute right-3 top-3 text-gray-400 cursor-pointer"
                              onClick={togglePasswordVisibility}>
                            {showPassword ? (
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none"
                                     viewBox="0 0 24 24" stroke="currentColor" className="w-5 h-5">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                          d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243" />
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                          d="M3 3l18 18" />
                                </svg>
                            ) : (
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none"
                                     viewBox="0 0 24 24" stroke="currentColor" className="w-5 h-5">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                          d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                          d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.543 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                                </svg>
                            )}
                        </span>
                    </div>

                    <div className="text-right">
                        <Link to="/recover-password" className="text-sm text-gray-500 hover:text-gray-700">
                            Recover Password ?
                        </Link>
                    </div>

                    <button type="submit"
                            disabled={loading}
                            className="w-full bg-orange-500 hover:bg-orange-600 disabled:bg-orange-300 text-white py-3 px-4 rounded-md transition-colors duration-300 font-medium flex items-center justify-center">
                        {loading ? (
                            <>
                                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                                     xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10"
                                            stroke="currentColor" strokeWidth="4" />
                                    <path className="opacity-75" fill="currentColor"
                                          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                                </svg>
                                Signing In...
                            </>
                        ) : (
                            "Sign In"
                        )}
                    </button>
                </form>
            </div>

            <div className="absolute bottom-4 right-4">
                <img src={SposorImage} alt="Sponsor Logo" className="h-12" />
            </div>
        </div>
    );
}
