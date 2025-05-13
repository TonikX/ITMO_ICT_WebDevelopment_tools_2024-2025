import React, { createContext, useState, useEffect, useContext } from 'react';
import { User, LoginCredentials, RegistrationData } from '../types';
import { authApi } from '../services/api';

interface AuthContextType {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    login: (credentials: LoginCredentials) => Promise<void>;
    register: (data: RegistrationData) => Promise<void>;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
    const [isLoading, setIsLoading] = useState<boolean>(true);

    useEffect(() => {
        // This would be used to validate the token and fetch user data
        const validateToken = async () => {
            // For this example, we'll just check if token exists
            // In a real app, you'd make an API call to validate the token
            if (token) {
                // Mock user data since we don't have an endpoint to get current user
                setUser({
                    id: 1, // This would come from the token payload in a real app
                    username: 'currentUser', // This would come from an API call
                });
            }
            setIsLoading(false);
        };

        validateToken();
    }, [token]);

    const login = async (credentials: LoginCredentials) => {
        setIsLoading(true);
        try {
            const response = await authApi.login(credentials);
            localStorage.setItem('token', response.access_token);
            setToken(response.access_token);
            // In a real app, you'd make another call to get user details
            // or decode the JWT token if it contains user information
        } catch (error) {
            throw error;
        } finally {
            setIsLoading(false);
        }
    };

    const register = async (data: RegistrationData) => {
        setIsLoading(true);
        try {
            const user = await authApi.register(data);
            // After registration, we would typically log the user in
            await login({ username: data.username, password: data.password });
            setUser(user);
        } catch (error) {
            throw error;
        } finally {
            setIsLoading(false);
        }
    };

    const logout = () => {
        localStorage.removeItem('token');
        setToken(null);
        setUser(null);
    };

    return (
        <AuthContext.Provider
            value={{
                user,
                token,
                isAuthenticated: !!user,
                isLoading,
                login,
                register,
                logout,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth необходимо использовать внутри AuthProvider');
    }
    return context;
};