import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { Message } from '../types/chat';

interface Props {
  message: Message;
}

export const ChatBubble: React.FC<Props> = ({ message }) => {
  const isUser = message.role === 'user';
  
  // Check if assistant indicates insufficient information
  const isNotEnoughInfo = !isUser && message.content.toLowerCase().includes("don't have enough information");
  
  // Sort sources by score descending and get the best one
  const bestSource = !isUser && message.sources && message.sources.length > 0
    ? [...message.sources].sort((a, b) => (b.score || 0) - (a.score || 0))[0]
    : null;

  const showSource = !isUser && bestSource && !isNotEnoughInfo;

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} my-4`}>
      <div
        className={`max-w-[85%] p-5 rounded-2xl shadow-sm ${
          isUser
            ? 'bg-green-600 text-white rounded-br-none'
            : 'bg-gray-800 text-gray-100 rounded-bl-none'
        }`}
      >
        <div className="prose prose-invert prose-p:my-2 prose-headings:my-2 prose-ul:my-2 prose-li:my-1 prose-a:text-green-400">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
        </div>
        
        {showSource && (
          <div className="mt-3 pt-3 border-t border-gray-700">
            <div className="flex items-center justify-between text-xs text-gray-400">
              <span>Best source</span>
              <span className="font-bold text-gray-200">
                {bestSource.score !== undefined
                  ? `${(bestSource.score * 100).toFixed(0)}%`
                  : 'N/A'}
              </span>
            </div>
            <div className="font-medium text-white mt-0.5 truncate" title={bestSource.title}>
              {bestSource.title}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
