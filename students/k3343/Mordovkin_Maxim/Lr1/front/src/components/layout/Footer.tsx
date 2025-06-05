import React from 'react';
import { MapPin } from 'lucide-react';

const Footer: React.FC = () => {
    return (
        <footer className="bg-gray-800 text-white">
            <div className="container mx-auto px-4 py-8">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    <div>
                        <h3 className="text-xl font-bold mb-4 flex items-center">
                            <MapPin className="h-5 w-5 mr-2" /> TravelPartner
                        </h3>
                        <p className="text-gray-300">
                            Свяжитесь с попутчиками и найдите идеального попутчика. Откройте для себя новые направления вместе и создайте незабываемые воспоминания.
                        </p>
                    </div>

                    <div>
                        <h3 className="text-xl font-bold mb-4">Quick Links</h3>
                        <ul className="space-y-2">
                            <li><a href="/" className="text-gray-300 hover:text-white transition duration-200">Home</a></li>
                            <li><a href="/trips" className="text-gray-300 hover:text-white transition duration-200">Explore Trips</a></li>
                        </ul>
                    </div>
                </div>
            </div>
        </footer>
    );
};

export default Footer;