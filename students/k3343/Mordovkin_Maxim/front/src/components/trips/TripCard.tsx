import React from 'react';
import { Link } from 'react-router-dom';
import { Calendar, MapPin, Users, Clock } from 'lucide-react';
import { Trip } from '../../types';
import Button from '../common/Button';

interface TripCardProps {
    trip: Trip;
    isOwner?: boolean;
    onJoin?: () => void;
    onLeave?: () => void;
}

const TripCard: React.FC<TripCardProps> = ({
                                               trip,
                                               isOwner = false,
                                               onJoin,
                                               onLeave,
                                           }) => {
    // Function to format date string (simple implementation)
    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
        }).format(date);
    };

    // Function to create a background gradient style with destination-related colors
    const getBackgroundStyle = () => {
        // Simple hash function to generate colors based on trip destination
        const hash = trip.destination.split('').reduce((acc, char) => {
            return char.charCodeAt(0) + ((acc << 5) - acc);
        }, 0);

        const hue = Math.abs(hash % 360);
        const lightness = 85 + (hash % 10); // Keep it light for text readability

        return {
            backgroundImage: `linear-gradient(135deg, hsl(${hue}, 95%, ${lightness}%), hsl(${(hue + 30) % 360}, 80%, ${lightness - 10}%))`,
        };
    };

    const isParticipant = trip.participants?.some(p => p.id === 1); // Replace 1 with actual current user id
    const formattedStartDate = formatDate(trip.start_date);
    const formattedEndDate = formatDate(trip.end_date);

    return (
        <div className="bg-white rounded-lg shadow-md overflow-hidden transition-all duration-300 hover:shadow-lg transform hover:-translate-y-1">
            <div className="h-32 w-full" style={getBackgroundStyle()}>
                <div className="h-full w-full flex items-center justify-center bg-gradient-to-t from-black/30 to-transparent">
                    <h3 className="text-xl font-bold text-white px-4 text-center drop-shadow-md">
                        {trip.title}
                    </h3>
                </div>
            </div>

            <div className="p-4">
                <div className="flex flex-col space-y-2 mb-3">
                    <div className="flex items-center text-gray-600">
                        <MapPin className="h-4 w-4 mr-2 text-teal-600" />
                        <span>{trip.origin} → {trip.destination}</span>
                    </div>

                    <div className="flex items-center text-gray-600">
                        <Calendar className="h-4 w-4 mr-2 text-teal-600" />
                        <span>{formattedStartDate} - {formattedEndDate}</span>
                    </div>

                    {trip.duration_days && (
                        <div className="flex items-center text-gray-600">
                            <Clock className="h-4 w-4 mr-2 text-teal-600" />
                            <span>{trip.duration_days} days</span>
                        </div>
                    )}

                    {trip.participants && (
                        <div className="flex items-center text-gray-600">
                            <Users className="h-4 w-4 mr-2 text-teal-600" />
                            <span>{trip.participants.length} participant(s)</span>
                        </div>
                    )}
                </div>

                <p className="text-gray-600 mb-4 line-clamp-2">
                    {trip.description || "No description provided."}
                </p>

                <div className="flex justify-between items-center">
                    <Link to={`/trips/${trip.id}`}>
                        <Button variant="outline" size="sm">
                            View Details
                        </Button>
                    </Link>

                    {!isOwner && (
                        isParticipant ? (
                            <Button
                                variant="danger"
                                size="sm"
                                onClick={onLeave}
                            >
                                Покинуть
                            </Button>
                        ) : (
                            <Button
                                variant="primary"
                                size="sm"
                                onClick={onJoin}
                            >
                                Присоединиться
                            </Button>
                        )
                    )}

                    {isOwner && (
                        <Link to={`/trips/${trip.id}/edit`}>
                            <Button variant="secondary" size="sm">
                                Редактировать поездку
                            </Button>
                        </Link>
                    )}
                </div>
            </div>
        </div>
    );
};

export default TripCard;