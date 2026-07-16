import React, { useState } from 'react';

interface Props {
  onSend: (message: string) => void;
  isLoading: boolean;
}

export const MessageInput: React.FC<Props> = ({ onSend, isLoading }) => {
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (input.trim() && !isLoading) {
      onSend(input);
      setInput('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="p-3 bg-gray-950/80 backdrop-blur-sm border-t border-gray-800">
      <div className="max-w-3xl mx-auto flex gap-2 shadow-lg shadow-black/50">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
          placeholder="Ask a question..."
          className="flex-grow p-3 md:p-4 rounded-xl bg-gray-900 border border-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-green-600/50 transition-all text-sm md:text-base"
        />
        <button
          onClick={handleSend}
          disabled={isLoading || !input.trim()}
          className="px-5 md:px-6 py-3 md:py-4 rounded-xl bg-green-600 text-white font-semibold disabled:opacity-50 hover:bg-green-700 transition-all shadow-md shadow-green-900/20 text-sm md:text-base"
        >
          {isLoading ? '...' : 'Send'}
        </button>
      </div>
    </div>
  );
};
