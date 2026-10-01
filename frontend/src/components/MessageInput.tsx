import React, { useState, useRef, useId } from 'react';
import { SubjectSelector } from './SubjectSelector';

interface Props {
  onSend: (message: string, imageFile?: File | null) => void;
  isLoading: boolean;
  selectedSubject: string;
  onSelectSubject: (subject: string) => void;
  subjects: string[];
  isSubjectsLoading?: boolean;
}

const MAX_FILE_SIZE_MB = 10;
const ACCEPTED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/heic', 'image/gif'];

export const MessageInput: React.FC<Props> = ({
  onSend,
  isLoading,
  selectedSubject,
  onSelectSubject,
  subjects,
  isSubjectsLoading = false,
}) => {
  const [input, setInput] = useState('');
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreviewUrl, setImagePreviewUrl] = useState<string | null>(null);
  const [imageError, setImageError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const inputId = useId();

  const handleSend = () => {
    if ((input.trim() || selectedImage) && !isLoading) {
      onSend(input, selectedImage);
      setInput('');
      clearImage();
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const validateAndSetImage = (file: File) => {
    setImageError(null);

    if (!ACCEPTED_IMAGE_TYPES.includes(file.type) && !file.name.match(/\.(jpg|jpeg|png|webp|heic|gif)$/i)) {
      setImageError('Unsupported image format. Please select a JPG, PNG, WEBP, or HEIC image.');
      return;
    }

    if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
      setImageError(`Image size exceeds ${MAX_FILE_SIZE_MB}MB limit. Please choose a smaller file.`);
      return;
    }

    setSelectedImage(file);
    const objectUrl = URL.createObjectURL(file);
    setImagePreviewUrl(objectUrl);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetImage(e.target.files[0]);
    }
    e.target.value = '';
  };

  const clearImage = () => {
    if (imagePreviewUrl) {
      URL.revokeObjectURL(imagePreviewUrl);
    }
    setSelectedImage(null);
    setImagePreviewUrl(null);
    setImageError(null);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetImage(e.dataTransfer.files[0]);
    }
  };

  const handleTextareaInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = `${Math.min(e.target.scrollHeight, 160)}px`;
  };

  return (
    <footer className="p-3 sm:p-4 bg-[#09090b]/95 border-t border-zinc-800/80 backdrop-blur-md sticky bottom-0 z-20">
      <div className="max-w-4xl mx-auto">
        {/* Error notification for image validation */}
        {imageError && (
          <div
            role="alert"
            className="mb-2 p-2 px-3 rounded-lg bg-zinc-900 border border-zinc-700 text-zinc-300 text-xs flex items-center justify-between animate-in fade-in duration-100"
          >
            <span>{imageError}</span>
            <button
              type="button"
              onClick={() => setImageError(null)}
              className="text-zinc-400 hover:text-white font-bold ml-2"
              aria-label="Dismiss image error"
            >
              ×
            </button>
          </div>
        )}

        {/* Composer Box */}
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`flex flex-col bg-[#121215] border rounded-xl p-3 sm:p-3.5 shadow-lg transition-all ${
            isDragging
              ? 'border-zinc-500 bg-[#18181c] ring-1 ring-zinc-500'
              : 'border-zinc-800/90 focus-within:border-zinc-700'
          }`}
        >
          {/* Active Context Chips Header (Subject & Image Preview) */}
          {(selectedSubject || selectedImage) && (
            <div className="flex items-center gap-2 mb-2 pb-2 border-b border-zinc-800/80 flex-wrap text-xs">
              {/* Active Subject Chip */}
              {selectedSubject && (
                <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-zinc-800 border border-zinc-700 text-zinc-200 font-medium text-xs">
                  <span className="text-zinc-500 text-[10px] uppercase tracking-wider">Topic:</span>
                  <span>{selectedSubject}</span>
                  <button
                    type="button"
                    onClick={() => onSelectSubject('')}
                    className="text-zinc-400 hover:text-white ml-0.5 font-bold transition-colors"
                    title="Remove subject focus"
                    aria-label={`Remove subject ${selectedSubject}`}
                  >
                    ×
                  </button>
                </div>
              )}

              {/* Active Image Thumbnail Chip */}
              {selectedImage && imagePreviewUrl && (
                <div className="inline-flex items-center gap-2 p-1 pr-2 rounded-md bg-zinc-900 border border-zinc-800 text-zinc-300 text-xs">
                  <img
                    src={imagePreviewUrl}
                    alt="Preview"
                    className="w-6 h-6 rounded object-cover border border-zinc-800"
                  />
                  <span className="max-w-[120px] sm:max-w-[180px] truncate text-[11px]">
                    {selectedImage.name}
                  </span>
                  <span className="text-[10px] text-zinc-500">
                    ({(selectedImage.size / (1024 * 1024)).toFixed(1)}MB)
                  </span>
                  <button
                    type="button"
                    onClick={clearImage}
                    className="text-zinc-400 hover:text-white font-bold ml-0.5 transition-colors"
                    title="Remove attached image"
                    aria-label="Remove image"
                  >
                    ×
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Question Text Input Area */}
          <label htmlFor={inputId} className="sr-only">
            Ask a nutrition, storage, or grocery question
          </label>
          <textarea
            id={inputId}
            ref={textareaRef}
            value={input}
            onChange={handleTextareaInput}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            rows={1}
            placeholder={
              selectedSubject
                ? `Ask about ${selectedSubject.toLowerCase()} (nutrition, storage, safety)...`
                : 'Ask a question or compare foods...'
            }
            className="w-full bg-transparent text-zinc-100 placeholder-zinc-500 focus:outline-none resize-none text-sm sm:text-base px-1 max-h-40 min-h-[38px] leading-relaxed"
          />

          {/* Action Toolbar */}
          <div className="flex items-center justify-between pt-2 border-t border-zinc-800/80 mt-1 gap-2">
            <div className="flex items-center gap-1.5 sm:gap-2">
              {/* Subject Selector dropdown */}
              <SubjectSelector
                selectedSubject={selectedSubject}
                onSelectSubject={onSelectSubject}
                subjects={subjects}
                isLoading={isSubjectsLoading}
                dropUp={true}
              />

              {/* Hidden File Input for Image Upload / Camera */}
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileChange}
                accept="image/*"
                className="hidden"
                aria-label="Upload image"
              />

              {/* Camera / Image Button */}
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                disabled={isLoading}
                title="Attach food photo or product label"
                aria-label="Attach photo"
                className={`p-2 rounded-lg border text-xs font-medium transition-all focus:outline-none focus-visible:ring-1 focus-visible:ring-zinc-400 flex items-center gap-1.5 ${
                  selectedImage
                    ? 'bg-zinc-800 border-zinc-600 text-white'
                    : 'bg-zinc-900 border-zinc-800 text-zinc-400 hover:text-zinc-200 hover:border-zinc-700'
                }`}
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-4 w-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.75}
                    d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"
                  />
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.75}
                    d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                </svg>
                <span className="hidden md:inline text-xs">
                  {selectedImage ? 'Image Ready' : 'Add Photo'}
                </span>
              </button>
            </div>

            {/* High-Craft Minimalist Send Button (Solid White on Black) */}
            <button
              type="button"
              onClick={handleSend}
              disabled={isLoading || (!input.trim() && !selectedImage)}
              aria-label="Send question"
              className="inline-flex items-center justify-center gap-1.5 px-4 sm:px-5 py-2 rounded-lg bg-white hover:bg-zinc-200 active:scale-95 text-zinc-950 font-medium text-xs sm:text-sm disabled:bg-zinc-900 disabled:text-zinc-600 disabled:cursor-not-allowed transition-all shadow-sm focus:outline-none focus-visible:ring-1 focus-visible:ring-white"
            >
              {isLoading ? (
                <>
                  <span className="w-3.5 h-3.5 border-2 border-zinc-950/30 border-t-zinc-950 rounded-full animate-spin"></span>
                  <span className="hidden sm:inline">Processing</span>
                </>
              ) : (
                <>
                  <span>Send</span>
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-3.5 w-3.5"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    aria-hidden="true"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M5 10l7-7m0 0l7 7m-7-7v18"
                    />
                  </svg>
                </>
              )}
            </button>
          </div>
        </div>

        <p className="mt-2 text-center text-[11px] text-zinc-600">
          Knowledge answers strictly grounded in the Grocery AI vector database.
        </p>
      </div>
    </footer>
  );
};
