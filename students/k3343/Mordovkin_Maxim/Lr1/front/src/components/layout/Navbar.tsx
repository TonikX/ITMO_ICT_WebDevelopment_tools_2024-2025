import React from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Map, PlusCircle, Search, User, LogOut } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const Navbar: React.FC = () => {
    const { isAuthenticated, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <nav className="bg-teal-600 text-white shadow-md">
            <div className="container mx-auto px-4">
                <div className="flex justify-between items-center h-16">
                    <div className="flex items-center space-x-1">
                        <Map className="h-6 w-6" />
                        <Link to="/" className="text-xl font-bold">TravelPartner</Link>
                    </div>

                    <div className="hidden md:flex items-center space-x-4">
                        <Link to="/trips" className="hover:text-teal-200 px-3 py-2 rounded-md transition duration-200">
                            Найти попутчика
                        </Link>
                        {isAuthenticated && (
                            <>
                                <Link to="/trips/create" className="hover:text-teal-200 px-3 py-2 rounded-md transition duration-200">
                                    Создать поездку
                                </Link>
                                <Link to="/my-trips" className="hover:text-teal-200 px-3 py-2 rounded-md transition duration-200">
                                    Мои поездки
                                </Link>
                            </>
                        )}
                    </div>

                    <div className="flex items-center space-x-2">
                        {isAuthenticated ? (
                            <>
                                <Link to="/profile" className="hover:text-teal-200 p-2 rounded-full transition duration-200">
                                    <User className="h-5 w-5" />
                                </Link>
                                <button
                                    onClick={handleLogout}
                                    className="hover:text-teal-200 p-2 rounded-full transition duration-200"
                                >
                                    <LogOut className="h-5 w-5" />
                                </button>
                            </>
                        ) : (
                            <>
                                <Link
                                    to="/login"
                                    className="bg-white text-teal-600 px-4 py-2 rounded-md hover:bg-teal-50 transition duration-200"
                                >
                                    Log In
                                </Link>
                                <Link
                                    to="/register"
                                    className="bg-teal-500 px-4 py-2 rounded-md hover:bg-teal-400 transition duration-200"
                                >
                                    Sign Up
                                </Link>
                            </>
                        )}
                    </div>
                </div>
            </div>

            {/* Mobile Menu - shown on small screens */}
            {isAuthenticated && (
                <div className="md:hidden border-t border-teal-500 bg-teal-600">
                    <div className="flex justify-around py-2">
                        <Link to="/trips" className="text-center flex flex-col items-center p-2">
                            <Search className="h-5 w-5" />
                            <span className="text-xs">Найти попутчика</span>
                        </Link>
                        <Link to="/trips/create" className="text-center flex flex-col items-center p-2">
                            <PlusCircle className="h-5 w-5" />
                            <span className="text-xs">Создать поездку</span>
                        </Link>
                        <Link to="/my-trips" className="text-center flex flex-col items-center p-2">
                            <Map className="h-5 w-5" />
                            <span className="text-xs">Мои поездки</span>
                        </Link>
                        <Link to="/profile" className="text-center flex flex-col items-center p-2">
                            <User className="h-5 w-5" />
                            <span className="text-xs">Профиль</span>
                        </Link>
                    </div>
                </div>
            )}
        </nav>
    );
};

export default Navbar;