import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { tripsApi } from '../../services/api';
import { TripFormData } from '../../types';
import Button from '../../components/common/Button';
import InputField from '../../components/common/InputField';
import { ArrowLeft } from 'lucide-react';

const CreateTripPage: React.FC = () => {
    const [step, setStep] = useState(1);
    const [formData, setFormData] = useState<TripFormData>({
        title: '',
        description: '',
        start_date: '',
        end_date: '',
        origin: '',
        destination: '',
        duration_days: undefined,
    });
    const [errors, setErrors] = useState<Record<string, string>>({});
    const [isSubmitting, setIsSubmitting] = useState(false);

    const navigate = useNavigate();

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        const { id, value } = e.target;
        setFormData((prev) => ({ ...prev, [id]: value }));

        // Clear error for the field being changed
        if (errors[id]) {
            setErrors((prev) => ({ ...prev, [id]: '' }));
        }
    };

    const validateStepOne = () => {
        const newErrors: Record<string, string> = {};

        if (!formData.title.trim()) {
            newErrors.title = 'Название обязательно';
        }

        if (!formData.start_date) {
            newErrors.start_date = 'Требуется дата начала';
        }

        if (!formData.end_date) {
            newErrors.end_date = 'Дата окончания обязательна';
        } else if (formData.start_date && new Date(formData.end_date) < new Date(formData.start_date)) {
            newErrors.end_date = 'Дата окончания не может быть раньше даты начала';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const validateStepTwo = () => {
        const newErrors: Record<string, string> = {};

        if (!formData.origin.trim()) {
            newErrors.origin = 'Origin is required';
        }

        if (!formData.destination.trim()) {
            newErrors.destination = 'Требуется указать пункт назначения';
        }

        if (formData.duration_days !== undefined && formData.duration_days <= 0) {
            newErrors.duration_days = 'Длительность должна быть положительным числом.';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const nextStep = () => {
        if (step === 1 && validateStepOne()) {
            setStep(2);
        } else if (step === 2 && validateStepTwo()) {
            handleSubmit();
        }
    };

    const prevStep = () => {
        setStep(1);
    };

    const handleSubmit = async () => {
        if (!validateStepOne() || !validateStepTwo()) {
            return;
        }

        setIsSubmitting(true);

        try {
            const createdTrip = await tripsApi.createTrip(formData);
            navigate(`/trips/${createdTrip.id}`);
        } catch (err: any) {
            setErrors({ global: err.message || 'Не удалось создать поездку' });
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="container mx-auto px-4 py-8 max-w-2xl">
            <Link to="/trips" className="flex items-center text-teal-600 hover:text-teal-700 mb-6">
                <ArrowLeft className="h-5 w-5 mr-1" />
                Назад к поездкам
            </Link>

            <div className="bg-white rounded-lg shadow-md overflow-hidden">
                <div className="bg-teal-600 p-6 text-white">
                    <h1 className="text-2xl font-bold">Создание поездки</h1>
                    <p className="mt-1 text-teal-100">Найдите попутчиков для вашего приключения</p>
                </div>

                <div className="p-6">
                    {errors.global && (
                        <div className="mb-6 bg-red-50 border-l-4 border-red-500 p-4 rounded">
                            <p className="text-red-700">{errors.global}</p>
                        </div>
                    )}

                    <div className="mb-6">
                        <div className="relative">
                            <div className="flex items-center justify-between mb-4">
                                <div
                                    className={`w-10 h-10 rounded-full flex items-center justify-center ${
                                        step === 1 ? 'bg-teal-600 text-white' : 'bg-teal-100 text-teal-600'
                                    }`}
                                >
                                    1
                                </div>
                                <div className="flex-1 h-1 mx-2 bg-gray-200">
                                    <div
                                        className={`h-full ${
                                            step === 2 ? 'bg-teal-600' : 'bg-gray-200'
                                        }`}
                                    ></div>
                                </div>
                                <div
                                    className={`w-10 h-10 rounded-full flex items-center justify-center ${
                                        step === 2 ? 'bg-teal-600 text-white' : 'bg-teal-100 text-teal-600'
                                    }`}
                                >
                                    2
                                </div>
                            </div>

                            <p className="text-center text-sm text-gray-500 mb-6">
                                {step === 1 ? 'Basic Information' : 'Trip Details'}
                            </p>
                        </div>
                    </div>

                    {step === 1 && (
                        <div className="space-y-4">
                            <InputField
                                id="title"
                                label="Название поездки"
                                value={formData.title}
                                onChange={handleChange}
                                error={errors.title}
                                required
                                placeholder="например, поход по Европе"
                            />

                            <InputField
                                id="description"
                                label="Описание поездки"
                                multiline
                                rows={4}
                                value={formData.description || ''}
                                onChange={handleChange}
                                error={errors.description}
                                placeholder="Опишите свою поездку, что вы планируете делать, каких попутчиков вы ищете и т. д."
                            />

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <InputField
                                    id="start_date"
                                    label="Дата начала"
                                    type="date"
                                    value={formData.start_date}
                                    onChange={handleChange}
                                    error={errors.start_date}
                                    required
                                />

                                <InputField
                                    id="end_date"
                                    label="Дата окончания"
                                    type="date"
                                    value={formData.end_date}
                                    onChange={handleChange}
                                    error={errors.end_date}
                                    required
                                />
                            </div>
                        </div>
                    )}

                    {step === 2 && (
                        <div className="space-y-4">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <InputField
                                    id="origin"
                                    label="Откуда"
                                    value={formData.origin}
                                    onChange={handleChange}
                                    error={errors.origin}
                                    required
                                    placeholder="Санкт-Петербург"
                                />

                                <InputField
                                    id="destination"
                                    label="Куда"
                                    value={formData.destination}
                                    onChange={handleChange}
                                    error={errors.destination}
                                    required
                                    placeholder="Москва"
                                />
                            </div>

                            <InputField
                                id="duration_days"
                                label="Продолжительность (дней)"
                                type="number"
                                value={formData.duration_days?.toString() || ''}
                                onChange={(e) => handleChange({
                                    ...e,
                                    target: {
                                        ...e.target,
                                        value: e.target.value ? parseInt(e.target.value, 10).toString() : '',
                                        id: 'duration_days',
                                    },
                                })}
                                error={errors.duration_days}
                                placeholder="e.g., 7"
                            />
                        </div>
                    )}

                    <div className="mt-8 flex justify-between">
                        {step === 1 ? (
                            <div></div>
                        ) : (
                            <Button
                                variant="outline"
                                onClick={prevStep}
                            >
                                Back
                            </Button>
                        )}

                        <Button
                            variant="primary"
                            onClick={nextStep}
                            disabled={isSubmitting}
                        >
                            {isSubmitting ? (
                                <span className="flex items-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Creating...
                </span>
                            ) : step === 1 ? (
                                'Next'
                            ) : (
                                'Create Trip'
                            )}
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default CreateTripPage;