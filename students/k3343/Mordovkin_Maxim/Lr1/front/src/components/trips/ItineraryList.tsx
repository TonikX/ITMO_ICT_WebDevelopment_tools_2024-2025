import React from 'react';
import { MapPin, Calendar, Trash2 } from 'lucide-react';
import { ItineraryItem } from '../../types';

interface ItineraryListProps {
    items: ItineraryItem[];
    isEditable?: boolean;
    onDelete?: (itemId: number) => void;
}

const ItineraryList: React.FC<ItineraryListProps> = ({
                                                         items,
                                                         isEditable = false,
                                                         onDelete
                                                     }) => {
    // Sort items by day number
    const sortedItems = [...items].sort((a, b) => a.day_number - b.day_number);

    if (items.length === 0) {
        return (
            <div className="text-center py-8 bg-gray-50 rounded-lg border border-dashed border-gray-300">
                <Calendar className="h-12 w-12 mx-auto mb-2 text-gray-400" />
                <p className="text-gray-500 font-medium">Пока нет пунктов маршрута</p>
                <p className="text-gray-400 text-sm mt-1">
                    Организатор поездки не добавил ни одного пункта назначения в маршрут.
                </p>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {sortedItems.map((item) => (
                <div
                    key={item.id}
                    className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm hover:shadow-md transition duration-200"
                >
                    <div className="flex items-center justify-between">
                        <div className="flex items-center">
                            <div className="flex-shrink-0 w-10 h-10 bg-teal-100 rounded-full flex items-center justify-center text-teal-700 font-semibold">
                                {item.day_number}
                            </div>
                            <div className="ml-4">
                                <div className="flex items-center">
                                    <MapPin className="h-4 w-4 text-teal-600 mr-1" />
                                    <h3 className="font-medium text-gray-800">{item.location}</h3>
                                </div>
                                {item.description && (
                                    <p className="text-gray-600 text-sm mt-1">{item.description}</p>
                                )}
                            </div>
                        </div>

                        {isEditable && onDelete && (
                            <button
                                onClick={() => onDelete(item.id)}
                                className="p-2 text-gray-400 hover:text-red-500 rounded-full hover:bg-red-50 transition duration-200"
                                aria-label="Delete itinerary item"
                            >
                                <Trash2 className="h-4 w-4" />
                            </button>
                        )}
                    </div>
                </div>
            ))}
        </div>
    );
};

export default ItineraryList;