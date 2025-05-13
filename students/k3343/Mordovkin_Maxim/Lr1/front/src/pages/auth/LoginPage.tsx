import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import Button from '../../components/common/Button';
import InputField from '../../components/common/InputField';
import { Map, Lock } from 'lucide-react';

const LoginPage: React.FC = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');

        try {
            await login({ username, password });
            navigate('/trips');
        } catch (err: any) {
            setError(err.message || 'Не удалось войти. Проверьте свои учетные данные.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-[80vh] flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-md w-full space-y-8 bg-white p-8 rounded-lg shadow-md">
                <div className="text-center">
                    <div className="flex justify-center">
                        <Map className="h-12 w-12 text-teal-600" />
                    </div>
                    <h2 className="mt-4 text-3xl font-extrabold text-gray-900">Добро пожаловать</h2>
                    <p className="mt-2 text-sm text-gray-600">
                        Войдите, чтобы найти свое следующее путешествие
                    </p>
                </div>

                {error && (
                    <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
                        <p className="text-red-700">{error}</p>
                    </div>
                )}

                <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
                    <div className="space-y-4">
                        <InputField
                            id="username"
                            label="Username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                        />

                        <InputField
                            id="password"
                            label="Password"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>

                    <Button
                        type="submit"
                        variant="primary"
                        fullWidth
                        disabled={isLoading}
                    >
                        {isLoading ? (
                            <span className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Signing in...
              </span>
                        ) : (
                            <span className="flex items-center justify-center">
                <Lock className="mr-2 h-5 w-5" />
                Sign in
              </span>
                        )}
                    </Button>

                    <div className="text-center mt-4">
                        <p className="text-sm text-gray-600">
                            Don't have an account?{' '}
                            <Link to="/register" className="font-medium text-teal-600 hover:text-teal-500">
                                Sign up now
                            </Link>
                        </p>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default LoginPage;