import React, { useRef, useEffect } from 'react';
import type { Message } from '../types/chat';
import { ChatBubble } from './ChatBubble';

interface Props {
  messages: Message[];
}

export const ChatWindow: React.FC<Props> = ({ messages }) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex-grow overflow-y-auto p-4 max-w-3xl mx-auto w-full">
      {messages.map((message) => (
        <ChatBubble key={message.id} message={message} />
      ))}
      <div ref={bottomRef} />
    </div>
  );
};
