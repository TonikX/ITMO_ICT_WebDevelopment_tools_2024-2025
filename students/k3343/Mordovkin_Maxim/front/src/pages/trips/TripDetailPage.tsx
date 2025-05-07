import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { tripsApi, itineraryApi, messagesApi } from '../../services/api';
import { Trip, ItineraryItem, Message, MessageFormData } from '../../types';
import { Calendar, MapPin, Users, Clock, Edit, ArrowLeft, Send, Trash } from 'lucide-react';
import Button from '../../components/common/Button';
import ItineraryList from '../../components/trips/ItineraryList';
import MessageList from '../../components/trips/MessageList';
import { useAuth } from '../../context/AuthContext';

const TripDetailPage: React.FC = () => {
    const { tripId } = useParams<{ tripId: string }>();
    const [trip, setTrip] = useState<Trip | null>(null);
    const [itinerary, setItinerary] = useState<ItineraryItem[]>([]);
    const [messages, setMessages] = useState<Message[]>([]);
    const [newMessage, setNewMessage] = useState('');
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');
    const [activeTab, setActiveTab] = useState<'details' | 'itinerary' | 'messages'>('details');

    const { user, isAuthenticated } = useAuth();
    const navigate = useNavigate();

    const numericTripId = tripId ? parseInt(tripId, 10) : 0;
    const isOwner = trip && user && trip.owner_id === user.id;
    const isParticipant = trip?.participants?.some(p => p.id === user?.id);

    useEffect(() => {
        const fetchData = async () => {
            if (!tripId) return;

            setIsLoading(true);

            try {
                const [tripData, itineraryData, messagesData] = await Promise.all([
                    tripsApi.getTrip(parseInt(tripId, 10)),
                    itineraryApi.getItineraryItems(parseInt(tripId, 10)),
                    messagesApi.getMessages(parseInt(tripId, 10))
                ]);

                setTrip(tripData);
                setItinerary(itineraryData);
                setMessages(messagesData);
            } catch (err: any) {
                setError(err.message || 'Не удалось загрузить данные о поездке');
            } finally {
                setIsLoading(false);
            }
        };

        fetchData();
    }, [tripId]);

    const handleJoinTrip = async () => {
        if (!isAuthenticated) {
            navigate('/login', { state: { redirect: `/trips/${tripId}` } });
            return;
        }

        try {
            await tripsApi.joinTrip(numericTripId);
            // Refetch trip to update participants
            const updatedTrip = await tripsApi.getTrip(numericTripId);
            setTrip(updatedTrip);
        } catch (err: any) {
            alert(err.message || 'Не удалось присоединиться к поездке');
        }
    };

    const handleLeaveTrip = async () => {
        try {
            await tripsApi.leaveTrip(numericTripId);
            // Refetch trip to update participants
            const updatedTrip = await tripsApi.getTrip(numericTripId);
            setTrip(updatedTrip);
        } catch (err: any) {
            alert(err.message || 'Не удалось покинуть поездку');
        }
    };

    const handleDeleteTrip = async () => {
        if (!isOwner || !confirm('Вы уверены, что хотите удалить эту поездку? Это действие не может быть отменено.')) {
            return;
        }

        try {
            await tripsApi.deleteTrip(numericTripId);
            navigate('/trips');
        } catch (err: any) {
            alert(err.message || 'Не удалось удалить поездку');
        }
    };

    const handleSendMessage = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!newMessage.trim() || !isAuthenticated) return;

        const messageData: MessageFormData = {
            content: newMessage.trim()
        };

        try {
            const sentMessage = await messagesApi.createMessage(numericTripId, messageData);
            setMessages(prev => [...prev, sentMessage]);
            setNewMessage('');
        } catch (err: any) {
            alert(err.message || 'Не удалось отправить сообщение');
        }
    };

    if (isLoading) {
        return (
            <div className="flex justify-center items-center py-20">
                <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-teal-500"></div>
            </div>
        );
    }

    if (error || !trip) {
        return (
            <div className="container mx-auto px-4 py-12 max-w-4xl">
                <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded mb-6">
                    <p className="text-red-700">{error || 'Trip not found'}</p>
                </div>
                <Link to="/trips" className="flex items-center text-teal-600 hover:text-teal-700">
                    <ArrowLeft className="h-5 w-5 mr-1" />
                    Назад к поездкам
                </Link>
            </div>
        );
    }

    // Format dates
    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
        }).format(date);
    };

    return (
        <div className="container mx-auto px-4 py-8 max-w-4xl">
            <Link to="/trips" className="flex items-center text-teal-600 hover:text-teal-700 mb-6">
                <ArrowLeft className="h-5 w-5 mr-1" />
                Back to all trips
            </Link>

            <div className="bg-gradient-to-r from-teal-500 to-teal-700 rounded-t-lg p-6 text-white">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between">
                    <h1 className="text-3xl font-bold mb-2 md:mb-0">{trip.title}</h1>

                    {isAuthenticated && (
                        <div className="space-x-2">
                            {isOwner ? (
                                <>
                                    <Link to={`/trips/${trip.id}/edit`}>
                                        <Button variant="secondary" size="sm" className="bg-white/20 hover:bg-white/30">
                                            <Edit className="h-4 w-4 mr-1" />
                                            Edit Trip
                                        </Button>
                                    </Link>
                                    <Button
                                        variant="danger"
                                        size="sm"
                                        className="bg-red-500/70 hover:bg-red-500"
                                        onClick={handleDeleteTrip}
                                    >
                                        <Trash className="h-4 w-4 mr-1" />
                                        Delete
                                    </Button>
                                </>
                            ) : isParticipant ? (
                                <Button
                                    variant="danger"
                                    size="sm"
                                    className="bg-red-500/70 hover:bg-red-500"
                                    onClick={handleLeaveTrip}
                                >
                                    Leave Trip
                                </Button>
                            ) : (
                                <Button
                                    variant="primary"
                                    size="sm"
                                    className="bg-white text-teal-700 hover:bg-teal-50"
                                    onClick={handleJoinTrip}
                                >
                                    Join Trip
                                </Button>
                            )}
                        </div>
                    )}
                </div>

                <div className="flex flex-wrap items-center mt-4 text-teal-100">
                    <div className="flex items-center mr-6 mb-2">
                        <MapPin className="h-5 w-5 mr-1" />
                        <span>{trip.origin} → {trip.destination}</span>
                    </div>

                    <div className="flex items-center mr-6 mb-2">
                        <Calendar className="h-5 w-5 mr-1" />
                        <span>{formatDate(trip.start_date)} - {formatDate(trip.end_date)}</span>
                    </div>

                    {trip.duration_days && (
                        <div className="flex items-center mr-6 mb-2">
                            <Clock className="h-5 w-5 mr-1" />
                            <span>{trip.duration_days} days</span>
                        </div>
                    )}

                    <div className="flex items-center mb-2">
                        <Users className="h-5 w-5 mr-1" />
                        <span>{trip.participants?.length || 0} participant(s)</span>
                    </div>
                </div>
            </div>

            <div className="bg-white shadow-md rounded-b-lg">
                <div className="border-b border-gray-200">
                    <nav className="flex">
                        <button
                            className={`px-4 py-3 text-sm font-medium border-b-2 focus:outline-none ${
                                activeTab === 'details'
                                    ? 'border-teal-500 text-teal-600'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            }`}
                            onClick={() => setActiveTab('details')}
                        >
                            Подробности поездки
                        </button>
                        <button
                            className={`px-4 py-3 text-sm font-medium border-b-2 focus:outline-none ${
                                activeTab === 'itinerary'
                                    ? 'border-teal-500 text-teal-600'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            }`}
                            onClick={() => setActiveTab('itinerary')}
                        >
                            Маршрут
                        </button>
                        <button
                            className={`px-4 py-3 text-sm font-medium border-b-2 focus:outline-none ${
                                activeTab === 'messages'
                                    ? 'border-teal-500 text-teal-600'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            }`}
                            onClick={() => setActiveTab('messages')}
                        >
                            Сообщения
                        </button>
                    </nav>
                </div>

                <div className="p-6">
                    {activeTab === 'details' && (
                        <div>
                            <h2 className="text-xl font-semibold mb-4">About this trip</h2>
                            <p className="text-gray-700 mb-6">
                                {trip.description || "No description provided."}
                            </p>

                            <h3 className="text-lg font-semibold mb-3">Trip Organizer</h3>
                            <div className="bg-gray-50 p-4 rounded-lg mb-6">
                                <p className="font-medium">{trip.owner?.username || "Unknown"}</p>
                                {trip.owner?.full_name && <p className="text-gray-600">{trip.owner.full_name}</p>}
                            </div>

                            <h3 className="text-lg font-semibold mb-3">Participants</h3>
                            {trip.participants && trip.participants.length > 0 ? (
                                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                                    {trip.participants.map((participant) => (
                                        <div key={participant.id} className="bg-gray-50 p-3 rounded-lg">
                                            <p className="font-medium">{participant.username}</p>
                                            {participant.full_name && <p className="text-gray-600 text-sm">{participant.full_name}</p>}
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <p className="text-gray-500">No one has joined this trip yet.</p>
                            )}
                        </div>
                    )}

                    {activeTab === 'itinerary' && (
                        <div>
                            <div className="flex justify-between items-center mb-4">
                                <h2 className="text-xl font-semibold">Trip Itinerary</h2>
                                {isOwner && (
                                    <Link to={`/trips/${trip.id}/itinerary/edit`}>
                                        <Button variant="outline" size="sm">
                                            <Edit className="h-4 w-4 mr-1" />
                                            Edit Itinerary
                                        </Button>
                                    </Link>
                                )}
                            </div>
                            <ItineraryList items={itinerary} />
                        </div>
                    )}

                    {activeTab === 'messages' && (
                        <div>
                            <h2 className="text-xl font-semibold mb-4">Trip Discussion</h2>

                            <div className="bg-gray-50 rounded-lg border border-gray-200 mb-4">
                                <MessageList messages={messages} users={trip.participants || []} />

                                {isAuthenticated ? (
                                    <form onSubmit={handleSendMessage} className="border-t border-gray-200 p-4">
                                        <div className="flex">
                                            <input
                                                type="text"
                                                value={newMessage}
                                                onChange={(e) => setNewMessage(e.target.value)}
                                                placeholder="Type your message..."
                                                className="flex-1 border border-gray-300 rounded-l-md px-4 py-2 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                                            />
                                            <Button
                                                type="submit"
                                                variant="primary"
                                                disabled={!newMessage.trim()}
                                                className="rounded-l-none"
                                            >
                                                <Send className="h-5 w-5" />
                                            </Button>
                                        </div>
                                    </form>
                                ) : (
                                    <div className="border-t border-gray-200 p-4 text-center">
                                        <p className="text-gray-600 mb-2">You need to be logged in to send messages</p>
                                        <Link to="/login" className="text-teal-600 hover:text-teal-700 font-medium">
                                            Авторизуйтесь, чтобы принять участие
                                        </Link>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default TripDetailPage;