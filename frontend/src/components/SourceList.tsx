import React, { useState, useId } from 'react';
import type { Source } from '../types/chat';

interface Props {
  sources: Source[];
}

export const SourceList: React.FC<Props> = ({ sources }) => {
  const [isOpen, setIsOpen] = useState(false);
  const contentId = useId();

  if (!sources || sources.length === 0) return null;

  return (
    <div className="mt-3.5 pt-3 border-t border-zinc-800/80">
      <button
        type="button"
        onClick={() => setIsOpen((prev) => !prev)}
        aria-expanded={isOpen}
        aria-controls={contentId}
        className="inline-flex items-center gap-2 text-xs font-medium text-zinc-400 hover:text-zinc-200 transition-colors focus:outline-none focus-visible:ring-1 focus-visible:ring-zinc-400 rounded px-1 -mx-1"
      >
        <span className="w-1.5 h-1.5 rounded-full bg-zinc-500"></span>
        <span>
          {isOpen ? 'Hide Sources' : `Sources · ${sources.length}`}
        </span>
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className={`h-3 w-3 text-zinc-500 transition-transform duration-150 ${
            isOpen ? 'rotate-180' : ''
          }`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div id={contentId} className="mt-2.5 space-y-2 animate-in fade-in duration-150">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {sources.map((source, idx) => {
              const displayTitle = source.article || source.title || 'Knowledge Base Document';
              const rawSection = source.section || source.source;
              const displaySection = Array.isArray(rawSection)
                ? rawSection.join(', ')
                : typeof rawSection === 'string'
                ? rawSection
                : 'General Reference';
              const matchPercent =
                typeof source.score === 'number'
                  ? Math.round(source.score * 100)
                  : null;

              return (
                <div
                  key={idx}
                  className="p-2.5 rounded-lg bg-zinc-900/60 border border-zinc-800/80 hover:border-zinc-700/80 transition-colors text-xs space-y-1.5"
                >
                  <div className="flex items-start justify-between gap-2">
                    <span
                      className="font-medium text-zinc-200 truncate leading-snug"
                      title={displayTitle}
                    >
                      {displayTitle}
                    </span>
                    {matchPercent !== null && (
                      <span className="px-1.5 py-0.5 rounded text-[10px] font-medium bg-zinc-800 text-zinc-300 border border-zinc-700 shrink-0">
                        {matchPercent}% match
                      </span>
                    )}
                  </div>

                  <div className="flex items-center gap-1.5 text-[11px] text-zinc-400 truncate">
                    <span className="text-zinc-500">Section:</span>
                    <span className="text-zinc-300 truncate" title={displaySection}>
                      {displaySection}
                    </span>
                  </div>

                  {source.category && (
                    <div className="pt-0.5">
                      <span className="inline-block text-[9px] uppercase tracking-wider text-zinc-400 bg-zinc-800 px-1.5 py-0.5 rounded">
                        {source.category}
                      </span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
