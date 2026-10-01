import React from 'react';

interface HeaderProps {
  subjectCount?: number;
  hasMessages?: boolean;
  onClearHistory?: () => void;
  selectedSubject?: string;
  onSelectSubject?: (subject: string) => void;
}

export const Header: React.FC<HeaderProps> = ({
  subjectCount,
  hasMessages,
  onClearHistory,
  selectedSubject,
  onSelectSubject,
}) => {
  return (
    <header className="px-5 sm:px-8 py-3.5 flex items-center justify-between border-b border-zinc-800/80 bg-[#09090b]/95 backdrop-blur-md sticky top-0 z-30">
      {/* Brand & Positioning */}
      <div className="flex items-center gap-3">
        <div className="w-7 h-7 rounded-md bg-zinc-900 border border-zinc-700/80 flex items-center justify-center text-zinc-100 font-semibold text-xs tracking-tight">
          GA
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-sm font-semibold text-zinc-100 tracking-tight">
              Grocery AI
            </h1>
            <span className="text-[10px] font-medium text-zinc-400 bg-zinc-900 border border-zinc-800 px-1.5 py-0.2 rounded tracking-wide">
              Assistant
            </span>
          </div>
          <p className="text-[11px] text-zinc-500 tracking-normal hidden xs:block">
            Nutrition Knowledge Assistant
          </p>
        </div>
      </div>

      {/* Center/Right Status & Controls */}
      <div className="flex items-center gap-2.5">
        {selectedSubject && (
          <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-zinc-900 border border-zinc-750 text-xs text-zinc-300">
            <span className="text-zinc-500 text-[11px]">Topic:</span>
            <span className="font-medium text-zinc-100">{selectedSubject}</span>
            <button
              onClick={() => onSelectSubject?.('')}
              className="text-zinc-500 hover:text-white ml-0.5 text-xs transition-colors"
              title="Clear subject filter"
              aria-label="Clear subject filter"
            >
              ×
            </button>
          </div>
        )}

        {typeof subjectCount === 'number' && subjectCount > 0 && (
          <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-zinc-900/60 border border-zinc-800 text-[11px] text-zinc-400">
            <span className="w-1.5 h-1.5 rounded-full bg-zinc-400"></span>
            <span>{subjectCount} Topics In Knowledge Base</span>
          </div>
        )}

        {hasMessages && (
          <button
            onClick={onClearHistory}
            className="px-2.5 py-1 rounded-md bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 text-zinc-400 hover:text-zinc-200 text-xs font-medium transition-colors focus-visible:ring-1 focus-visible:ring-zinc-400"
            title="Start new conversation"
            aria-label="New chat"
          >
            New Session
          </button>
        )}
      </div>
    </header>
  );
};
