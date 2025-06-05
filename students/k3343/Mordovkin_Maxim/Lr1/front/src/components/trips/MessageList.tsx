import React from 'react';
import { Message, User } from '../../types';
import { useAuth } from '../../context/AuthContext';

interface MessageListProps {
    messages: Message[];
    users?: User[];
}

const MessageList: React.FC<MessageListProps> = ({ messages, users = [] }) => {
    const { user } = useAuth();

    // TODO вроде как не ищется юзер по id
    // Helper to find user by ID
    const findUser = (id: number) => {
        return users.find(u => u.id === id) || { username: 'Unknown User' };
    };

    // Format timestamp
    const formatTime = (timestamp: string) => {
        try {
            const date = new Date(timestamp);
            return date.toLocaleString('en-US', {
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
            });
        } catch (e) {
            return timestamp;
        }
    };

    if (messages.length === 0) {
        return (
            <div className="text-center py-8">
                <p className="text-gray-500">Пока сообщений нет.</p>
            </div>
        );
    }

    return (
        <div className="space-y-4 max-h-[400px] overflow-y-auto p-2">
            {messages.map((message) => {
                const sender = message.sender || findUser(message.sender_id);
                const isCurrentUser = user?.id === message.sender_id;

                return (
                    <div
                        key={message.id}
                        className={`flex ${isCurrentUser ? 'justify-end' : 'justify-start'}`}
                    >
                        <div
                            className={`max-w-[80%] rounded-lg px-4 py-2 ${
                                isCurrentUser
                                    ? 'bg-teal-500 text-white rounded-tr-none'
                                    : 'bg-gray-100 text-gray-800 rounded-tl-none'
                            }`}
                        >
                            <div className="flex items-center mb-1">
                <span
                    className={`font-medium text-sm ${
                        isCurrentUser ? 'text-teal-100' : 'text-gray-600'
                    }`}
                >
                  {isCurrentUser ? 'You' : sender.username}
                </span>
                                <span
                                    className={`text-xs ml-2 ${
                                        isCurrentUser ? 'text-teal-200' : 'text-gray-500'
                                    }`}
                                >
                  {formatTime(message.timestamp)}
                </span>
                            </div>
                            <p className="break-words">{message.content}</p>
                        </div>
                    </div>
                );
            })}
        </div>
    );
};

export default MessageList;