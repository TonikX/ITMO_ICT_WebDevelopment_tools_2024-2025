import React from 'react';
import { Link } from 'react-router-dom';
import { MapPin, Users, Calendar, Globe } from 'lucide-react';
import Button from '../components/common/Button';

const HomePage: React.FC = () => {
    return (
        <div>
            {/* Hero Section */}
            <section className="bg-gradient-to-r from-teal-500 to-teal-700 text-white">
                <div className="container mx-auto px-4 py-24 flex flex-col items-center">
                    <h1 className="text-4xl md:text-5xl font-bold text-center mb-6 leading-tight">
                        Find Your Perfect Travel Companion
                    </h1>
                    <p className="text-xl text-center mb-8 max-w-2xl">
                        Connect with like-minded travelers, share adventures, and create unforgettable memories together.
                    </p>
                    <div className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4">
                        <Link to="/trips">
                            <Button variant="primary" size="lg" className="bg-white text-teal-700 hover:bg-teal-50">
                                <Globe className="mr-2 h-5 w-5" />
                                Explore Trips
                            </Button>
                        </Link>
                        <Link to="/register">
                            <Button variant="primary" size="lg" className="bg-teal-600 border border-white hover:bg-teal-700">
                                <Users className="mr-2 h-5 w-5" />
                                Join Now
                            </Button>
                        </Link>
                    </div>
                </div>
            </section>

            {/* How It Works Section */}
            <section className="py-20 bg-gray-50">
                <div className="container mx-auto px-4">
                    <h2 className="text-3xl font-bold text-center mb-12">How It Works</h2>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                        <div className="bg-white p-6 rounded-lg shadow-md text-center">
                            <div className="w-16 h-16 bg-teal-100 rounded-full flex items-center justify-center mx-auto mb-4">
                                <Users className="h-8 w-8 text-teal-600" />
                            </div>
                            <h3 className="text-xl font-semibold mb-3">Create Your Profile</h3>
                            <p className="text-gray-600">
                                Sign up and tell others about your travel style, interests, and preferences.
                            </p>
                        </div>

                        <div className="bg-white p-6 rounded-lg shadow-md text-center">
                            <div className="w-16 h-16 bg-teal-100 rounded-full flex items-center justify-center mx-auto mb-4">
                                <MapPin className="h-8 w-8 text-teal-600" />
                            </div>
                            <h3 className="text-xl font-semibold mb-3">Plan Your Trip</h3>
                            <p className="text-gray-600">
                                Create a trip with your destination, dates, and what you're looking for in a travel companion.
                            </p>
                        </div>

                        <div className="bg-white p-6 rounded-lg shadow-md text-center">
                            <div className="w-16 h-16 bg-teal-100 rounded-full flex items-center justify-center mx-auto mb-4">
                                <Calendar className="h-8 w-8 text-teal-600" />
                            </div>
                            <h3 className="text-xl font-semibold mb-3">Connect & Travel</h3>
                            <p className="text-gray-600">
                                Find compatible travel companions, discuss trip details, and embark on your adventure together.
                            </p>
                        </div>
                    </div>
                </div>
            </section>

            {/* Featured Destinations */}
            <section className="py-20">
                <div className="container mx-auto px-4">
                    <h2 className="text-3xl font-bold text-center mb-12">Popular Destinations</h2>

                    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
                        {['Paris, France', 'Tokyo, Japan', 'Bali, Indonesia', 'New York, USA', 'Rome, Italy', 'Sydney, Australia'].map((destination, index) => (
                            <div
                                key={index}
                                className="bg-white rounded-lg shadow-md overflow-hidden transition-all duration-300 hover:shadow-lg transform hover:-translate-y-1"
                            >
                                <div
                                    className="h-48 bg-cover bg-center"
                                    style={{
                                        backgroundImage: `url(https://source.unsplash.com/featured/?${destination.split(',')[0].toLowerCase()},travel)`,
                                    }}
                                >
                                    <div className="h-full w-full flex items-end justify-start p-4 bg-gradient-to-t from-black/50 to-transparent">
                                        <h3 className="text-xl font-bold text-white">{destination}</h3>
                                    </div>
                                </div>
                                <div className="p-4">
                                    <Link to={`/trips?location=${encodeURIComponent(destination.split(',')[0])}`}>
                                        <Button variant="outline" size="sm" fullWidth>
                                            Find Trips
                                        </Button>
                                    </Link>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Testimonials */}
            <section className="py-20 bg-gray-50">
                <div className="container mx-auto px-4">
                    <h2 className="text-3xl font-bold text-center mb-12">Why Travelers Love Us</h2>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                        {[
                            {
                                quote: "I met my best friend on TravelPartner during a trip to Thailand. We've traveled to 5 countries together since!",
                                author: "Sarah J.",
                                location: "London, UK"
                            },
                            {
                                quote: "As a solo traveler, I was nervous about finding companions. TravelPartner made it easy and safe to connect with like-minded adventurers.",
                                author: "Miguel R.",
                                location: "Barcelona, Spain"
                            },
                            {
                                quote: "The detailed profiles and messaging system helped me find the perfect travel buddy with similar interests and travel style.",
                                author: "Aisha K.",
                                location: "Toronto, Canada"
                            }
                        ].map((testimonial, index) => (
                            <div key={index} className="bg-white p-6 rounded-lg shadow-md">
                                <div className="flex items-center mb-4">
                                    <div className="mr-3">
                                        <div className="w-12 h-12 rounded-full bg-teal-100 flex items-center justify-center text-teal-600 font-bold">
                                            {testimonial.author.charAt(0)}
                                        </div>
                                    </div>
                                    <div>
                                        <h4 className="font-semibold">{testimonial.author}</h4>
                                        <p className="text-sm text-gray-500">{testimonial.location}</p>
                                    </div>
                                </div>
                                <p className="text-gray-600 italic">"{testimonial.quote}"</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="bg-teal-600 text-white py-16">
                <div className="container mx-auto px-4 text-center">
                    <h2 className="text-3xl font-bold mb-6">Ready to Find Your Next Adventure?</h2>
                    <p className="text-xl mb-8 max-w-2xl mx-auto">
                        Join thousands of travelers and start planning your next trip with the perfect companions.
                    </p>
                    <Link to="/register">
                        <Button
                            variant="primary"
                            size="lg"
                            className="bg-white text-teal-700 hover:bg-teal-50 transition-all duration-300"
                        >
                            Sign Up Now
                        </Button>
                    </Link>
                </div>
            </section>
        </div>
    );
};

export default HomePage;