export interface Source {
  title: string;
  source: string;
  score?: number;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
}

export interface ChatResponse {
  question: string;
  answer: string;
  sources: Source[];
}
