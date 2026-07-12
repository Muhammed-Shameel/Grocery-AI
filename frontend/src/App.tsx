import { Header } from './components/Header';
import { ChatWindow } from './components/ChatWindow';
import { MessageInput } from './components/MessageInput';
import { LoadingIndicator } from './components/LoadingIndicator';
import { useChat } from './hooks/useChat';
import './App.css';

function App() {
  const { messages, sendMessage, isLoading, error } = useChat();

  return (
    <div className="flex flex-col h-screen bg-black text-gray-100">
      <Header />
      <ChatWindow messages={messages} />
      {isLoading && <LoadingIndicator />}
      {error && <div className="text-red-500 text-center p-2">{error}</div>}
      <MessageInput onSend={sendMessage} isLoading={isLoading} />
    </div>
  );
}

export default App;
