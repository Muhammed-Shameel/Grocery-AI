import React from 'react';

export const LoadingIndicator: React.FC = () => {
  return (
    <div className="flex items-center gap-1 p-4">
      <div className="w-2 h-2 bg-gray-500 rounded-full animate-pulse"></div>
      <div className="w-2 h-2 bg-gray-500 rounded-full animate-pulse delay-150"></div>
      <div className="w-2 h-2 bg-gray-500 rounded-full animate-pulse delay-300"></div>
    </div>
  );
};
