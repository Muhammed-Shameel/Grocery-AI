import { useState, useEffect, useCallback } from 'react';
import type { Message, ChatResponse, Source } from '../types/chat';

const API_BASE = 'http://127.0.0.1:8000';

export const useChat = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStage, setLoadingStage] = useState<string>('Searching knowledge base...');
  const [error, setError] = useState<string | null>(null);
  const [selectedSubject, setSelectedSubject] = useState<string>('');
  const [availableSubjects, setAvailableSubjects] = useState<string[]>([]);
  const [isSubjectsLoading, setIsSubjectsLoading] = useState(false);

  // Fetch verified subjects from backend
  useEffect(() => {
    let mounted = true;
    setIsSubjectsLoading(true);
    fetch(`${API_BASE}/subjects`)
      .then((res) => {
        if (!res.ok) throw new Error('Failed to fetch subjects');
        return res.json();
      })
      .then((data) => {
        if (mounted && data && Array.isArray(data.subjects)) {
          setAvailableSubjects(data.subjects);
        }
      })
      .catch((err) => {
        console.warn('Could not load subjects from API:', err);
      })
      .finally(() => {
        if (mounted) setIsSubjectsLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, []);

  const convertFileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = (error) => reject(error);
    });
  };

  const sendMessage = useCallback(async (question: string, imageFile?: File | null) => {
    const trimmedQuestion = question.trim();
    if (!trimmedQuestion && !imageFile) {
      setError('Please enter a question or attach an image.');
      return;
    }

    setIsLoading(true);
    setError(null);
    setLoadingStage('Searching Grocery AI knowledge base...');

    let imageUrl: string | undefined = undefined;
    let imageBase64: string | undefined = undefined;

    if (imageFile) {
      try {
        imageUrl = URL.createObjectURL(imageFile);
        imageBase64 = await convertFileToBase64(imageFile);
      } catch {
        setError('Could not process the selected image. Please try another image.');
        setIsLoading(false);
        return;
      }
    }

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: trimmedQuestion || (imageFile ? 'Analyze this image.' : ''),
      subject: selectedSubject || undefined,
      imageUrl,
      timestamp: Date.now(),
    };

    setMessages((prev) => [...prev, userMessage]);

    // Progressive loading status feedback
    const stageTimer = setTimeout(() => {
      setLoadingStage('Reviewing relevant grocery information...');
    }, 1200);

    try {
      const response = await fetch(`${API_BASE}/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: trimmedQuestion || 'Analyze this product',
          subject: selectedSubject || undefined,
          image_data: imageBase64 || undefined,
        }),
      });

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Grocery AI endpoint not found. Please verify the backend is running.');
        }
        throw new Error('Something went wrong while processing your request. Please try again.');
      }

      const data: ChatResponse = await response.json();

      const normalizedSources: Source[] = (data.sources || []).map((s) => ({
        title: s.title || s.article || 'Knowledge Document',
        article: s.article || s.title,
        section: s.section || s.source || 'General Reference',
        source: s.source || s.section,
        score: typeof s.score === 'number' ? s.score : undefined,
        category: s.category || 'General',
        quality: s.quality || { is_clean: true },
      }));

      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: data.answer,
        grounded: data.grounded,
        sources: normalizedSources,
        visualObservation: data.visual_observation,
        timestamp: Date.now(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unable to connect to the knowledge assistant.';
      setError(message);
    } finally {
      clearTimeout(stageTimer);
      setIsLoading(false);
      setLoadingStage('Searching knowledge base...');
    }
  }, [selectedSubject]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return {
    messages,
    sendMessage,
    clearMessages,
    isLoading,
    loadingStage,
    error,
    selectedSubject,
    setSelectedSubject,
    availableSubjects,
    isSubjectsLoading,
  };
};
