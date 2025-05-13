import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import Button from '../../components/common/Button';
import InputField from '../../components/common/InputField';
import { Map, UserPlus } from 'lucide-react';

const RegisterPage: React.FC = () => {
    const [formData, setFormData] = useState({
        username: '',
        password: '',
        confirmPassword: '',
        full_name: '',
        bio: '',
        preferences: '',
    });
    const [errors, setErrors] = useState<Record<string, string>>({});
    const [isLoading, setIsLoading] = useState(false);

    const { register } = useAuth();
    const navigate = useNavigate();

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        const { id, value } = e.target;
        setFormData((prev) => ({ ...prev, [id]: value }));

        // Clear error for the field being changed
        if (errors[id]) {
            setErrors((prev) => ({ ...prev, [id]: '' }));
        }
    };

    const validateForm = () => {
        const newErrors: Record<string, string> = {};

        if (!formData.username.trim()) {
            newErrors.username = 'Имя пользователя обязательно';
        }

        if (!formData.password) {
            newErrors.password = 'Пароль обязателен';
        } else if (formData.password.length < 6) {
            newErrors.password = 'Пароль должен содержать не менее 6 символов';
        }

        if (formData.password !== formData.confirmPassword) {
            newErrors.confirmPassword = 'Пароли не совпадают';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!validateForm()) {
            return;
        }

        setIsLoading(true);

        try {
            await register({
                username: formData.username,
                password: formData.password,
                full_name: formData.full_name || undefined,
                bio: formData.bio || undefined,
                preferences: formData.preferences || undefined,
            });

            navigate('/trips');
        } catch (err: any) {
            setErrors({ global: err.message || 'Регистрация не удалась. Попробуйте еще раз.' });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-[80vh] py-12 px-4 sm:px-6 lg:px-8 bg-gray-50">
            <div className="max-w-md mx-auto bg-white rounded-lg shadow-md p-8">
                <div className="text-center">
                    <div className="flex justify-center">
                        <Map className="h-12 w-12 text-teal-600" />
                    </div>
                    <h2 className="mt-4 text-3xl font-extrabold text-gray-900">Create your account</h2>
                    <p className="mt-2 text-sm text-gray-600">
                        Присоединяйтесь к нашему сообществу путешественников
                    </p>
                </div>

                {errors.global && (
                    <div className="mt-4 bg-red-50 border-l-4 border-red-500 p-4 rounded">
                        <p className="text-red-700">{errors.global}</p>
                    </div>
                )}

                <form className="mt-8 space-y-4" onSubmit={handleSubmit}>
                    <InputField
                        id="username"
                        label="Username"
                        value={formData.username}
                        onChange={handleChange}
                        error={errors.username}
                        required
                    />

                    <InputField
                        id="full_name"
                        label="Full Name"
                        value={formData.full_name}
                        onChange={handleChange}
                    />

                    <InputField
                        id="password"
                        label="Password"
                        type="password"
                        value={formData.password}
                        onChange={handleChange}
                        error={errors.password}
                        required
                    />

                    <InputField
                        id="confirmPassword"
                        label="Confirm Password"
                        type="password"
                        value={formData.confirmPassword}
                        onChange={handleChange}
                        error={errors.confirmPassword}
                        required
                    />

                    <InputField
                        id="bio"
                        label="Bio"
                        multiline
                        value={formData.bio}
                        onChange={handleChange}
                        placeholder="Расскажите немного о себе"
                    />

                    <InputField
                        id="preferences"
                        label="Travel Preferences"
                        multiline
                        value={formData.preferences}
                        onChange={handleChange}
                        placeholder="Какие путешествия вам нравятся?"
                    />

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
                Creating Account...
              </span>
                        ) : (
                            <span className="flex items-center justify-center">
                <UserPlus className="mr-2 h-5 w-5" />
                Create Account
              </span>
                        )}
                    </Button>

                    <div className="text-center mt-4">
                        <p className="text-sm text-gray-600">
                            Already have an account?{' '}
                            <Link to="/login" className="font-medium text-teal-600 hover:text-teal-500">
                                Sign in
                            </Link>
                        </p>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default RegisterPage;