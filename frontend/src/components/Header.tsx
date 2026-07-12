import React from 'react';

export const Header: React.FC = () => {
  return (
    <header className="p-6 text-center">
      <h1 className="text-4xl font-bold text-white mb-2">🥦 Grocery AI</h1>
      <p className="text-xl text-gray-400 font-medium">Nutrition Knowledge Assistant</p>
      <p className="text-sm text-gray-500 mt-2">
        Ask questions about nutrition, food storage, protein, fruits, vegetables, and grocery products.
      </p>
    </header>
  );
};
