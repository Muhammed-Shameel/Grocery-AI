import { useState } from 'react';
import type { Message, ChatResponse } from '../types/chat';

export const useChat = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = async (question: string) => {
    setIsLoading(true);
    setError(null);

    const newUserMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: question,
    };

    setMessages((prev) => [...prev, newUserMessage]);

    try {
      const response = await fetch('http://127.0.0.1:8000/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question }),
      });

      if (!response.ok) {
        throw new Error('Unable to contact the Grocery AI server.');
      }

      const data: ChatResponse = await response.json();

      const newAssistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.answer,
        sources: (data.sources || []).map((s) => ({
          title: s.article,
          source: s.section,
          score: s.score,
        })),
      };

      setMessages((prev) => [...prev, newAssistantMessage]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred.');
    } finally {
      setIsLoading(false);
    }
  };

  return { messages, sendMessage, isLoading, error };
};
