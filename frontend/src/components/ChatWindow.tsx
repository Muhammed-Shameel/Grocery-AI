import React, { useRef, useEffect } from 'react';
import type { Message } from '../types/chat';
import { ChatBubble } from './ChatBubble';

interface Props {
  messages: Message[];
  isLoading: boolean;
}

export const ChatWindow: React.FC<Props> = ({ messages, isLoading }) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="flex-grow overflow-y-auto p-4 max-w-3xl mx-auto w-full">
      {messages.map((message) => (
        <ChatBubble key={message.id} message={message} />
      ))}
      {isLoading && (
        <div className="flex justify-start my-4">
          <div className="bg-gray-800 text-gray-400 p-4 rounded-2xl rounded-bl-none text-sm animate-pulse">
            Thinking...
          </div>
        </div>
      )}
      <div ref={bottomRef} />
    </div>
  );
};
