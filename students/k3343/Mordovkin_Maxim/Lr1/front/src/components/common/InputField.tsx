import React from 'react';

interface InputFieldProps {
    id: string;
    label: string;
    type?: string;
    placeholder?: string;
    value: string;
    onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void;
    error?: string;
    required?: boolean;
    disabled?: boolean;
    multiline?: boolean;
    rows?: number;
    className?: string;
}

const InputField: React.FC<InputFieldProps> = ({
                                                   id,
                                                   label,
                                                   type = 'text',
                                                   placeholder,
                                                   value,
                                                   onChange,
                                                   error,
                                                   required = false,
                                                   disabled = false,
                                                   multiline = false,
                                                   rows = 3,
                                                   className = '',
                                               }) => {
    const inputClasses = `
    w-full px-3 py-2 rounded-md border ${error ? 'border-red-500' : 'border-gray-300'}
    focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent
    disabled:bg-gray-100 disabled:text-gray-500
    transition duration-200
    ${className}
  `;

    return (
        <div className="mb-4">
            <label htmlFor={id} className="block text-sm font-medium text-gray-700 mb-1">
                {label} {required && <span className="text-red-500">*</span>}
            </label>

            {multiline ? (
                <textarea
                    id={id}
                    placeholder={placeholder}
                    value={value}
                    onChange={onChange}
                    disabled={disabled}
                    rows={rows}
                    className={inputClasses}
                    required={required}
                />
            ) : (
                <input
                    id={id}
                    type={type}
                    placeholder={placeholder}
                    value={value}
                    onChange={onChange}
                    disabled={disabled}
                    className={inputClasses}
                    required={required}
                />
            )}

            {error && <p className="mt-1 text-sm text-red-500">{error}</p>}
        </div>
    );
};

export default InputField;