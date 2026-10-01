export interface Source {
  title?: string;
  article?: string;
  section?: string | string[];
  source?: string | string[];
  score?: number;
  category?: string;
  quality?: { is_clean: boolean };
}

export interface VisualObservation {
  object_detected?: string | null;
  classification?: string | null;
  variety?: string | null;
  confidence?: number;
  source?: string;
  status?: string;
  model_version?: string | null;
  probabilities?: Record<string, number> | null;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  subject?: string;
  imageUrl?: string;
  sources?: Source[];
  grounded?: boolean;
  visualObservation?: VisualObservation | null;
  timestamp?: number;
}

export interface ChatResponse {
  question: string;
  answer: string;
  sources: Source[];
  grounded?: boolean;
  subject?: string;
  visual_observation?: VisualObservation | null;
}
