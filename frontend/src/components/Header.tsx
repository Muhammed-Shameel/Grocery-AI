import React from 'react';

export const Header: React.FC = () => {
  return (
    <header className="p-6 pb-2 text-center border-b border-gray-800/50">
      <h1 className="text-3xl font-extrabold text-white mb-1 tracking-tight"> Grocery AI</h1>
      <p className="text-sm text-green-400 font-semibold uppercase tracking-wider">Nutrition Knowledge Assistant</p>
    </header>
  );
};

