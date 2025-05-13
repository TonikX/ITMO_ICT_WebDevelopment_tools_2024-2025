import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';

// Layout components
import Navbar from './components/layout/Navbar';
import Footer from './components/layout/Footer';

// Pages
import HomePage from './pages/HomePage';
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import TripListPage from './pages/trips/TripListPage';
import TripDetailPage from './pages/trips/TripDetailPage';
import CreateTripPage from './pages/trips/CreateTripPage';

// Protected route component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const { isAuthenticated, isLoading } = useAuth();

    if (isLoading) {
        return (
            <div className="flex justify-center items-center h-screen">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-teal-500"></div>
            </div>
        );
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" />;
    }

    return <>{children}</>;
};

function App() {
    return (
        <AuthProvider>
            <Router>
                <div className="flex flex-col min-h-screen">
                    <Navbar />
                    <main className="flex-grow">
                        <Routes>
                            <Route path="/" element={<HomePage />} />
                            <Route path="/login" element={<LoginPage />} />
                            <Route path="/register" element={<RegisterPage />} />
                            <Route path="/trips" element={<TripListPage />} />
                            <Route path="/trips/:tripId" element={<TripDetailPage />} />
                            <Route
                                path="/trips/create"
                                element={
                                    <ProtectedRoute>
                                        <CreateTripPage />
                                    </ProtectedRoute>
                                }
                            />
                            <Route
                                path="/my-trips"
                                element={
                                    <ProtectedRoute>
                                        <TripListPage />
                                    </ProtectedRoute>
                                }
                            />
                            <Route path="*" element={<Navigate to="/" />} />
                        </Routes>
                    </main>
                    <Footer />
                </div>
            </Router>
        </AuthProvider>
    );
}

export default App;