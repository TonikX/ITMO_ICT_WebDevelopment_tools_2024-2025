import React, { useState, useEffect } from 'react';
import { tripsApi } from '../../services/api';
import TripCard from '../../components/trips/TripCard';
import { Search, Filter, MapPin, Calendar } from 'lucide-react';
import { Trip } from '../../types';
import Button from '../../components/common/Button';

import { useAuth } from '../../context/AuthContext';

const TripListPage: React.FC = () => {
    const [trips, setTrips] = useState<Trip[]>([]);
    const [filteredTrips, setFilteredTrips] = useState<Trip[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');
    const { user, isAuthenticated } = useAuth();

    // Filter states
    const [searchTerm, setSearchTerm] = useState('');
    const [locationFilter, setLocationFilter] = useState('');
    const [startDateFilter, setStartDateFilter] = useState('');
    const [showFilters, setShowFilters] = useState(false);

    useEffect(() => {
        const fetchTrips = async () => {
            setIsLoading(true);
            try {
                const data = await tripsApi.getTrips();
                setTrips(data);
                setFilteredTrips(data);
            } catch (err: any) {
                setError(err.message || 'Failed to load trips');
            } finally {
                setIsLoading(false);
            }
        };

        fetchTrips();
    }, []);

    useEffect(() => {
        // Apply filters
        let results = trips;

        if (searchTerm) {
            const term = searchTerm.toLowerCase();
            results = results.filter(
                trip =>
                    trip.title.toLowerCase().includes(term) ||
                    (trip.description && trip.description.toLowerCase().includes(term))
            );
        }

        if (locationFilter) {
            const location = locationFilter.toLowerCase();
            results = results.filter(
                trip =>
                    trip.destination.toLowerCase().includes(location) ||
                    trip.origin.toLowerCase().includes(location)
            );
        }

        if (startDateFilter) {
            results = results.filter(trip => {
                const tripStartDate = new Date(trip.start_date).getTime();
                const filterDate = new Date(startDateFilter).getTime();
                return tripStartDate >= filterDate;
            });
        }

        setFilteredTrips(results);
    }, [searchTerm, locationFilter, startDateFilter, trips]);

    const handleJoinTrip = async (tripId: number) => {
        try {
            await tripsApi.joinTrip(tripId);
            // In a real app, you would update the trip in the state
            // or refetch the trips to show the updated participants
            alert('Successfully joined the trip!');
        } catch (err: any) {
            alert(err.message || 'Failed to join trip');
        }
    };

    const handleLeaveTrip = async (tripId: number) => {
        try {
            await tripsApi.leaveTrip(tripId);
            // In a real app, you would update the trip in the state
            // or refetch the trips to show the updated participants
            alert('Successfully left the trip!');
        } catch (err: any) {
            alert(err.message || 'Failed to leave trip');
        }
    };

    const resetFilters = () => {
        setSearchTerm('');
        setLocationFilter('');
        setStartDateFilter('');
    };

    return (
        <div className="container mx-auto px-4 py-8">
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-800 mb-2">Explore Trips</h1>
                <p className="text-gray-600">
                    Find your next adventure and connect with fellow travelers
                </p>
            </div>

            <div className="mb-8">
                <div className="flex flex-col md:flex-row md:items-center md:space-x-4">
                    <div className="flex-1 relative mb-4 md:mb-0">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                            <Search className="h-5 w-5 text-gray-400" />
                        </div>
                        <input
                            type="text"
                            placeholder="Search trips..."
                            className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>

                    <Button
                        variant="outline"
                        onClick={() => setShowFilters(!showFilters)}
                        className="flex items-center"
                    >
                        <Filter className="h-5 w-5 mr-2" />
                        {showFilters ? 'Hide Filters' : 'Show Filters'}
                    </Button>
                </div>

                {showFilters && (
                    <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div className="relative">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <MapPin className="h-5 w-5 text-gray-400" />
                                </div>
                                <input
                                    type="text"
                                    placeholder="Filter by location..."
                                    className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                                    value={locationFilter}
                                    onChange={(e) => setLocationFilter(e.target.value)}
                                />
                            </div>

                            <div className="relative">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <Calendar className="h-5 w-5 text-gray-400" />
                                </div>
                                <input
                                    type="date"
                                    placeholder="Starting from..."
                                    className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                                    value={startDateFilter}
                                    onChange={(e) => setStartDateFilter(e.target.value)}
                                />
                            </div>

                            <Button
                                variant="outline"
                                onClick={resetFilters}
                                className="self-end"
                            >
                                Reset Filters
                            </Button>
                        </div>
                    </div>
                )}
            </div>

            {isLoading ? (
                <div className="flex justify-center items-center py-12">
                    <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-teal-500"></div>
                </div>
            ) : error ? (
                <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
                    <p className="text-red-700">{error}</p>
                </div>
            ) : filteredTrips.length === 0 ? (
                <div className="text-center py-12 bg-gray-50 rounded-lg border border-dashed border-gray-300">
                    <MapPin className="h-16 w-16 mx-auto mb-4 text-gray-400" />
                    <h3 className="text-xl font-medium text-gray-700 mb-2">No trips found</h3>
                    <p className="text-gray-500 max-w-md mx-auto">
                        {searchTerm || locationFilter || startDateFilter
                            ? "No trips match your filters. Try adjusting your search criteria."
                            : "There are no trips available at the moment. Check back later or create your own trip!"}
                    </p>
                    {isAuthenticated && (
                        <Button
                            variant="primary"
                            className="mt-4"
                            onClick={() => window.location.href = '/trips/create'}
                        >
                            Create a Trip
                        </Button>
                    )}
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {filteredTrips.map((trip) => (
                        <TripCard
                            key={trip.id}
                            trip={trip}
                            isOwner={user?.id === trip.owner_id}
                            onJoin={() => handleJoinTrip(trip.id)}
                            onLeave={() => handleLeaveTrip(trip.id)}
                        />
                    ))}
                </div>
            )}
        </div>
    );
};

export default TripListPage;