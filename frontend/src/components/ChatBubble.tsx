import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { Message } from '../types/chat';
import { SourceList } from './SourceList';

interface Props {
  message: Message;
}

export const ChatBubble: React.FC<Props> = ({ message }) => {
  const isUser = message.role === 'user';
  const [copied, setCopied] = useState(false);

  const hasSources = !isUser && message.sources && message.sources.length > 0;
  const isGrounded = !isUser && message.grounded === true && hasSources;
  const isRefusal = !isUser && (message.grounded === false || message.content.includes("couldn't find information"));

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <article
      aria-label={`${isUser ? 'User question' : 'Knowledge assistant answer'}`}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} my-4 md:my-5 animate-in fade-in duration-150`}
    >
      <div
        className={`w-full ${
          isUser
            ? 'max-w-[85%] sm:max-w-[75%] p-4 rounded-xl bg-zinc-800/90 border border-zinc-700/60 text-zinc-100 rounded-br-sm shadow-sm'
            : 'max-w-[95%] sm:max-w-[90%] md:max-w-[86%] p-5 sm:p-6 rounded-xl bg-[#111114] border border-zinc-800/70 text-zinc-100 shadow-md'
        }`}
      >
        {/* User Message Header (Subject tag / Attached image) */}
        {isUser && (
          <div className="space-y-2 mb-2">
            {message.subject && (
              <div className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-zinc-900 border border-zinc-700 text-[11px] text-zinc-300 font-medium">
                <span className="text-zinc-500">Topic:</span>
                <span>{message.subject}</span>
              </div>
            )}
            {message.imageUrl && (
              <div className="relative w-fit max-w-xs overflow-hidden rounded-md border border-zinc-700 bg-black/40">
                <img
                  src={message.imageUrl}
                  alt="User uploaded grocery item"
                  className="max-h-48 max-w-full object-contain rounded-md"
                />
              </div>
            )}
          </div>
        )}

        {/* Assistant Header: Grounding Status & Actions */}
        {!isUser && (
          <div className="flex items-center justify-between gap-2 mb-3 pb-2.5 border-b border-zinc-800/80 text-xs">
            <div className="flex items-center gap-2 flex-wrap">
              {isGrounded ? (
                <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-zinc-900 border border-zinc-750 text-zinc-300 text-[11px] font-medium">
                  <svg className="w-3 h-3 text-zinc-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  Grounded in Grocery Knowledge Base
                </span>
              ) : isRefusal ? (
                <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-zinc-900 border border-zinc-800 text-zinc-400 text-[11px] font-medium">
                  <svg className="w-3 h-3 text-zinc-500" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                  </svg>
                  Knowledge-Base Limitation
                </span>
              ) : (
                <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-zinc-900 border border-zinc-800 text-zinc-400 text-[11px] font-medium">
                  Verified Response
                </span>
              )}

              {message.visualObservation?.classification && message.visualObservation.classification !== "pending_cv_implementation" && (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-zinc-400 text-[10px]">
                  Detected: {message.visualObservation.classification}
                  {typeof message.visualObservation.confidence === "number" && message.visualObservation.confidence > 0
                    ? ` · ${Math.round(message.visualObservation.confidence * 100)}%`
                    : ""}
                  <span className="ml-0.5 px-1 rounded bg-amber-950/40 border border-amber-900/40 text-amber-500/80 text-[9px] uppercase tracking-wide">
                    {message.visualObservation.model_version || "cv trial"}
                  </span>
                </span>
              )}

              {message.visualObservation?.status === "cv_unavailable" && (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-zinc-500 text-[10px]">
                  Image recognition (v0.0.1 trial) unavailable on this host
                </span>
              )}
            </div>

            <button
              type="button"
              onClick={handleCopy}
              className="text-zinc-500 hover:text-zinc-300 text-xs px-1.5 py-1 rounded transition-colors focus:outline-none focus-visible:ring-1 focus-visible:ring-zinc-400 flex items-center gap-1"
              title="Copy answer"
              aria-label="Copy answer text"
            >
              {copied ? (
                <>
                  <svg className="w-3.5 h-3.5 text-zinc-300" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  <span className="text-[11px] text-zinc-300 font-medium">Copied</span>
                </>
              ) : (
                <>
                  <svg className="w-3.5 h-3.5 text-zinc-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.75} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                  <span className="text-[11px] hidden sm:inline">Copy</span>
                </>
              )}
            </button>
          </div>
        )}

        {/* Content Body */}
        {isUser ? (
          <p className="whitespace-pre-wrap text-sm leading-relaxed text-zinc-100">
            {message.content}
          </p>
        ) : (
          <div className="knowledge-prose">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                table: ({ children }) => (
                  <div className="overflow-x-auto my-3 rounded-lg border border-zinc-800">
                    <table className="min-w-full divide-y divide-zinc-800">{children}</table>
                  </div>
                ),
              }}
            >
              {message.content}
            </ReactMarkdown>
          </div>
        )}

        {/* Sources Attribution */}
        {hasSources && <SourceList sources={message.sources!} />}
      </div>
    </article>
  );
};
