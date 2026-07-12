import { Header } from './components/Header';
import { ChatWindow } from './components/ChatWindow';
import { MessageInput } from './components/MessageInput';
import { useChat } from './hooks/useChat';
import './App.css';

function App() {
  const { messages, sendMessage, isLoading, error } = useChat();

  return (
    <div className="flex flex-col h-screen bg-black text-gray-100 font-sans">
      <div className="fixed inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-gray-900/20 via-black to-black -z-10" />
      <Header />
      <ChatWindow messages={messages} isLoading={isLoading} />
      {error && <div className="text-red-400 text-center p-3 text-sm bg-red-950/20 border-t border-red-900/50">{error}</div>}
      <MessageInput onSend={sendMessage} isLoading={isLoading} />
    </div>
  );
}

export default App;
