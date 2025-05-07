export interface User {
    id: number;
    username: string;
    full_name?: string;
    bio?: string;
    preferences?: string;
}

export interface Trip {
    id: number;
    title: string;
    description?: string;
    start_date: string;
    end_date: string;
    origin: string;
    destination: string;
    duration_days?: number;
    owner_id: number;
    owner?: User;
    participants?: User[];
    itinerary_items?: ItineraryItem[];
    messages?: Message[];
}

export interface ItineraryItem {
    id: number;
    trip_id: number;
    day_number: number;
    location: string;
    description?: string;
}

export interface Message {
    id: number;
    trip_id: number;
    sender_id: number;
    content: string;
    timestamp: string;
    sender?: User;
}

export interface LoginCredentials {
    username: string;
    password: string;
}

export interface RegistrationData {
    username: string;
    full_name?: string;
    bio?: string;
    preferences?: string;
    password: string;
}

export interface TripFormData {
    title: string;
    description?: string;
    start_date: string;
    end_date: string;
    origin: string;
    destination: string;
    duration_days?: number;
}

export interface ItineraryItemFormData {
    day_number: number;
    location: string;
    description?: string;
}

export interface MessageFormData {
    content: string;
}