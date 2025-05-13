import {
    User,
    Trip,
    ItineraryItem,
    Message,
    LoginCredentials,
    RegistrationData,
    TripFormData,
    ItineraryItemFormData,
    MessageFormData
} from '../types';

const API_BASE_URL = 'http://localhost:8000';

// Helper function to handle API responses
const handleResponse = async (response: Response) => {
    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || 'Something went wrong');
    }
    return response.json();
};

// Function to get the auth token from localStorage
const getToken = (): string | null => localStorage.getItem('token');

// Auth API functions
export const authApi = {
    register: async (data: RegistrationData): Promise<User> => {
        const response = await fetch(`${API_BASE_URL}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        return handleResponse(response);
    },

    login: async (credentials: LoginCredentials): Promise<{ access_token: string }> => {
        const formData = new FormData();
        formData.append('username', credentials.username);
        formData.append('password', credentials.password);

        const response = await fetch(`${API_BASE_URL}/login`, {
            method: 'POST',
            body: formData,
        });
        return handleResponse(response);
    },
};

// Trips API functions
export const tripsApi = {
    getTrips: async (): Promise<Trip[]> => {
        const response = await fetch(`${API_BASE_URL}/trips`, {
            headers: { Authorization: `Bearer ${getToken()}` },
        });
        return handleResponse(response);
    },

    getTrip: async (id: number): Promise<Trip> => {
        const response = await fetch(`${API_BASE_URL}/trips/${id}`, {
            headers: { Authorization: `Bearer ${getToken()}` },
        });
        return handleResponse(response);
    },

    createTrip: async (data: TripFormData): Promise<Trip> => {
        const response = await fetch(`${API_BASE_URL}/trips`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${getToken()}`,
            },
            body: JSON.stringify(data),
        });
        return handleResponse(response);
    },

    updateTrip: async (id: number, data: TripFormData): Promise<Trip> => {
        const response = await fetch(`${API_BASE_URL}/trips/${id}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${getToken()}`,
            },
            body: JSON.stringify(data),
        });
        return handleResponse(response);
    },

    deleteTrip: async (id: number): Promise<void> => {
        const response = await fetch(`${API_BASE_URL}/trips/${id}`, {
            method: 'DELETE',
            headers: { Authorization: `Bearer ${getToken()}` },
        });
        return handleResponse(response);
    },

    joinTrip: async (id: number): Promise<{ status: string }> => {
        const response = await fetch(`${API_BASE_URL}/trips/${id}/join`, {
            method: 'POST',
            headers: { Authorization: `Bearer ${getToken()}` },
        });
        return handleResponse(response);
    },

    leaveTrip: async (id: number): Promise<{ status: string }> => {
        const response = await fetch(`${API_BASE_URL}/trips/${id}/leave`, {
            method: 'DELETE',
            headers: { Authorization: `Bearer ${getToken()}` },
        });
        return handleResponse(response);
    },
};

// Itinerary API functions
export const itineraryApi = {
    getItineraryItems: async (tripId: number): Promise<ItineraryItem[]> => {
        const response = await fetch(`${API_BASE_URL}/trips/${tripId}/itinerary`, {
            headers: { Authorization: `Bearer ${getToken()}` },
        });
        return handleResponse(response);
    },

    createItineraryItem: async (tripId: number, data: ItineraryItemFormData): Promise<ItineraryItem> => {
        const response = await fetch(`${API_BASE_URL}/trips/${tripId}/itinerary`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${getToken()}`,
            },
            body: JSON.stringify(data),
        });
        return handleResponse(response);
    },

    deleteItineraryItem: async (tripId: number, itemId: number): Promise<void> => {
        const response = await fetch(`${API_BASE_URL}/trips/${tripId}/itinerary/${itemId}`, {
            method: 'DELETE',
            headers: { Authorization: `Bearer ${getToken()}` },
        });
        return handleResponse(response);
    },
};

// Messages API functions
export const messagesApi = {
    getMessages: async (tripId: number): Promise<Message[]> => {
        const response = await fetch(`${API_BASE_URL}/trips/${tripId}/messages`, {
            headers: { Authorization: `Bearer ${getToken()}` },
        });
        return handleResponse(response);
    },

    createMessage: async (tripId: number, data: MessageFormData): Promise<Message> => {
        const response = await fetch(`${API_BASE_URL}/trips/${tripId}/messages`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${getToken()}`,
            },
            body: JSON.stringify(data),
        });
        return handleResponse(response);
    },
};