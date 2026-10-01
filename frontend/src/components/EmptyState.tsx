import React from 'react';
import { SubjectSelector } from './SubjectSelector';

interface EmptyStateProps {
  subjects: string[];
  selectedSubject: string;
  onSelectSubject: (subject: string) => void;
  onSelectPrompt: (prompt: string) => void;
  isSubjectsLoading?: boolean;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  subjects,
  selectedSubject,
  onSelectSubject,
  onSelectPrompt,
  isSubjectsLoading = false,
}) => {
  // Common subject pills to highlight for 1-click exploration
  const featuredSubjects = subjects
    .filter((s) => ['Apple', 'Milk', 'Egg as food', 'Broccoli', 'Tomato', 'Spinach', 'Banana'].includes(s))
    .slice(0, 6);

  // Dynamic context-aware prompts based on selected subject
  const promptSuggestions = selectedSubject
    ? [
        `What nutrients and vitamins are found in ${selectedSubject.toLowerCase()}?`,
        `How should I store ${selectedSubject.toLowerCase()} properly for maximum shelf life?`,
        `What are the food safety guidelines and storage temperatures for ${selectedSubject.toLowerCase()}?`,
        `What are common varieties or culinary uses of ${selectedSubject.toLowerCase()}?`,
      ]
    : [
        'Compare the protein content of milk and eggs.',
        'How should I store fresh spinach to prevent wilting?',
        'What nutrients are found in apples?',
        'What is the recommended storage temperature for whole milk?',
      ];

  return (
    <div className="flex flex-col items-center justify-center text-center py-12 sm:py-20 px-4 max-w-2xl mx-auto w-full animate-in fade-in duration-200">
      {/* Monogram Badge */}
      {/* Main Title & Positioning */}
      <h2 className="text-xl sm:text-2xl font-semibold text-zinc-100 tracking-tight mb-2">
        Grocery AI
      </h2>
      <p className="text-[11px] font-medium text-zinc-500 uppercase tracking-widest mb-3">
        Nutrition Knowledge Assistant
      </p>
      <p className="text-xs sm:text-sm text-zinc-400 max-w-md mb-7 leading-relaxed font-normal">
        A grounded knowledge reference for produce, dairy, poultry, and pantry items.
      </p>

      {/* Hero Subject Selector */}
      <div className="mb-7 flex flex-col items-center gap-2">
        <span className="text-[11px] text-zinc-500 font-medium">
          Select a topic to focus your inquiry (optional)
        </span>
        <SubjectSelector
          selectedSubject={selectedSubject}
          onSelectSubject={onSelectSubject}
          subjects={subjects}
          isLoading={isSubjectsLoading}
          dropUp={false}
        />
      </div>

      {/* Featured Subject Quick Tags */}
      {featuredSubjects.length > 0 && (
        <div className="mb-9 flex flex-wrap items-center justify-center gap-1.5 max-w-lg">
          {featuredSubjects.map((sub) => {
            const isSelected = selectedSubject === sub;
            return (
              <button
                key={sub}
                type="button"
                onClick={() => onSelectSubject(isSelected ? '' : sub)}
                className={`px-2.5 py-1 rounded-md text-xs transition-colors border ${
                  isSelected
                    ? 'bg-zinc-800 border-zinc-600 text-white font-medium'
                    : 'bg-zinc-900/60 border-zinc-800 text-zinc-400 hover:border-zinc-700 hover:text-zinc-200'
                }`}
              >
                {sub}
              </button>
            );
          })}
        </div>
      )}

      {/* Prompt Suggestions */}
      <div className="w-full text-left space-y-2">
        <div className="flex items-center justify-between text-[11px] text-zinc-500 uppercase tracking-wider font-medium px-1">
          <span>{selectedSubject ? `Suggested questions for ${selectedSubject}` : 'Inquiry examples'}</span>
          <span>Click to ask</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {promptSuggestions.map((prompt, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => onSelectPrompt(prompt)}
              className="p-3 rounded-lg bg-zinc-900/60 border border-zinc-800/80 hover:border-zinc-700 hover:bg-zinc-900 text-zinc-300 hover:text-white transition-all text-xs text-left shadow-sm flex items-center justify-between group focus:outline-none focus-visible:ring-1 focus-visible:ring-zinc-400"
            >
              <span className="line-clamp-2 leading-relaxed pr-2 text-zinc-300 group-hover:text-white">{prompt}</span>
              <span className="text-zinc-600 group-hover:text-zinc-300 group-hover:translate-x-0.5 transition-all text-xs shrink-0">
                →
              </span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
