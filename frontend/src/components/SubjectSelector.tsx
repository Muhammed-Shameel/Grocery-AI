import React, { useState, useEffect, useRef, useId } from 'react';

interface Props {
  selectedSubject: string;
  onSelectSubject: (subject: string) => void;
  subjects: string[];
  isLoading?: boolean;
  dropUp?: boolean;
}

export const SubjectSelector: React.FC<Props> = ({
  selectedSubject,
  onSelectSubject,
  subjects,
  isLoading = false,
  dropUp = true,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const dropdownRef = useRef<HTMLDivElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);
  const searchId = useId();

  // Handle clicking outside to close
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Handle escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        setIsOpen(false);
      }
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen]);

  // Autofocus search on open
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => {
        searchInputRef.current?.focus();
      }, 50);
    } else {
      setSearchQuery('');
    }
  }, [isOpen]);

  const filteredSubjects = subjects.filter((s) =>
    s.toLowerCase().includes(searchQuery.toLowerCase().trim())
  );

  return (
    <div className="relative inline-block text-left" ref={dropdownRef}>
      {/* Trigger Button */}
      <button
        type="button"
        onClick={() => setIsOpen((prev) => !prev)}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-medium transition-all focus:outline-none focus-visible:ring-1 focus-visible:ring-zinc-400 ${
          selectedSubject
            ? 'bg-zinc-800 border-zinc-600 text-zinc-100 hover:bg-zinc-750'
            : 'bg-zinc-900 border-zinc-800 text-zinc-300 hover:text-white hover:border-zinc-700'
        }`}
        title="Filter by subject in the knowledge base"
      >
        <span className="text-[10px] uppercase tracking-wider text-zinc-500 font-semibold">
          Topic:
        </span>
        <span className="font-medium truncate max-w-[110px] sm:max-w-[140px]">
          {selectedSubject || 'All Topics'}
        </span>
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className={`h-3.5 w-3.5 text-zinc-500 transition-transform duration-150 ${
            isOpen ? (dropUp ? '' : 'rotate-180') : dropUp ? 'rotate-180' : ''
          }`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Popover Dropdown */}
      {isOpen && (
        <div
          role="listbox"
          aria-label="Available grocery knowledge subjects"
          className={`absolute ${
            dropUp ? 'bottom-full mb-2' : 'top-full mt-2'
          } left-0 w-64 rounded-xl bg-[#141417] border border-zinc-800 shadow-2xl z-50 overflow-hidden backdrop-blur-xl animate-in fade-in duration-100`}
        >
          <div className="p-2.5 border-b border-zinc-800">
            <label htmlFor={searchId} className="sr-only">
              Search knowledge base subjects
            </label>
            <div className="relative">
              <input
                id={searchId}
                ref={searchInputRef}
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search topics..."
                className="w-full pl-7 pr-3 py-1.5 bg-zinc-950 border border-zinc-800 rounded-lg text-xs text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-zinc-600 focus:ring-1 focus:ring-zinc-600"
              />
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-3.5 w-3.5 text-zinc-500 absolute left-2 top-2"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
            </div>
          </div>

          <div className="max-h-56 overflow-y-auto p-1.5 space-y-0.5" tabIndex={-1}>
            {/* All subjects reset option */}
            <button
              type="button"
              role="option"
              aria-selected={!selectedSubject}
              onClick={() => {
                onSelectSubject('');
                setIsOpen(false);
              }}
              className={`w-full text-left px-2.5 py-1.5 rounded-lg text-xs transition-colors flex items-center justify-between ${
                !selectedSubject
                  ? 'bg-zinc-800 text-white font-medium'
                  : 'text-zinc-400 hover:bg-zinc-800/60 hover:text-zinc-200'
              }`}
            >
              <span>All Topics (Broad Search)</span>
              {!selectedSubject && (
                <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5 text-zinc-300" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              )}
            </button>

            {isLoading ? (
              <div className="p-3 text-center text-xs text-zinc-500">
                Loading topics from knowledge base...
              </div>
            ) : filteredSubjects.length > 0 ? (
              filteredSubjects.map((sub) => {
                const isSelected = selectedSubject === sub;
                return (
                  <button
                    key={sub}
                    type="button"
                    role="option"
                    aria-selected={isSelected}
                    onClick={() => {
                      onSelectSubject(sub);
                      setIsOpen(false);
                    }}
                    className={`w-full text-left px-2.5 py-1.5 rounded-lg text-xs transition-colors flex items-center justify-between ${
                      isSelected
                        ? 'bg-zinc-800 text-white font-medium'
                        : 'text-zinc-400 hover:bg-zinc-800/60 hover:text-zinc-200'
                    }`}
                  >
                    <span className="truncate">{sub}</span>
                    {isSelected && (
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5 text-zinc-300" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    )}
                  </button>
                );
              })
            ) : (
              <div className="p-3 text-center text-xs text-zinc-500">
                No matching topics found
              </div>
            )}
          </div>

          <div className="px-2.5 py-1.5 bg-zinc-950 border-t border-zinc-800/80 text-[10px] text-zinc-500 flex justify-between items-center">
            <span>{subjects.length} verified topics</span>
            <span className="text-zinc-600">Esc to close</span>
          </div>
        </div>
      )}
    </div>
  );
};
