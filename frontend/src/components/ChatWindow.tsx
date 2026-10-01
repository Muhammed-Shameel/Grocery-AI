import React, { useRef, useEffect } from 'react';
import type { Message } from '../types/chat';
import { ChatBubble } from './ChatBubble';
import { EmptyState } from './EmptyState';

interface Props {
  messages: Message[];
  isLoading: boolean;
  loadingStage?: string;
  onSelectSuggestion?: (question: string) => void;
  subjects: string[];
  selectedSubject: string;
  onSelectSubject: (subject: string) => void;
  isSubjectsLoading?: boolean;
}

export const ChatWindow: React.FC<Props> = ({
  messages,
  isLoading,
  loadingStage = 'Searching knowledge base...',
  onSelectSuggestion,
  subjects,
  selectedSubject,
  onSelectSubject,
  isSubjectsLoading = false,
}) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading, loadingStage]);

  return (
    <main
      role="log"
      aria-label="Conversation history"
      aria-live="polite"
      className="flex-grow overflow-y-auto px-4 sm:px-6 py-4 max-w-4xl mx-auto w-full flex flex-col justify-between"
    >
      <div>
        {messages.length === 0 ? (
          <EmptyState
            subjects={subjects}
            selectedSubject={selectedSubject}
            onSelectSubject={onSelectSubject}
            onSelectPrompt={(p) => onSelectSuggestion?.(p)}
            isSubjectsLoading={isSubjectsLoading}
          />
        ) : (
          messages.map((message) => <ChatBubble key={message.id} message={message} />)
        )}

        {/* Polished, Calm Assistant Loading State */}
        {isLoading && (
          <div
            role="status"
            aria-live="polite"
            className="flex justify-start my-4 animate-in fade-in duration-150"
          >
            <div className="bg-[#111114] border border-zinc-800 text-zinc-300 px-4 py-3 rounded-xl rounded-bl-sm text-xs sm:text-sm flex items-center gap-2.5 shadow-sm">
              <span className="w-1.5 h-1.5 rounded-full bg-zinc-400 animate-pulse"></span>
              <span className="font-normal text-zinc-400">{loadingStage}</span>
            </div>
          </div>
        )}
      </div>
      <div ref={bottomRef} className="h-4" />
    </main>
  );
};
