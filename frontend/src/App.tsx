import { Header } from './components/Header';
import { ChatWindow } from './components/ChatWindow';
import { MessageInput } from './components/MessageInput';
import { useChat } from './hooks/useChat';

function App() {
  const {
    messages,
    sendMessage,
    clearMessages,
    isLoading,
    loadingStage,
    error,
    selectedSubject,
    setSelectedSubject,
    availableSubjects,
    isSubjectsLoading,
  } = useChat();

  return (
    <div className="flex flex-col h-screen text-zinc-100 bg-[#09090b] selection:bg-zinc-800 selection:text-white">
      {/* Header Bar */}
      <Header
        subjectCount={availableSubjects.length}
        hasMessages={messages.length > 0}
        onClearHistory={clearMessages}
        selectedSubject={selectedSubject}
        onSelectSubject={setSelectedSubject}
      />

      {/* Global Error Banner */}
      {error && (
        <div
          role="alert"
          className="mx-auto max-w-3xl my-2 px-4 py-2.5 rounded-lg bg-zinc-900 border border-zinc-700 text-zinc-300 text-xs sm:text-sm flex items-center justify-between shadow-lg animate-in fade-in duration-100 w-[92%]"
        >
          <div className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-zinc-400"></span>
            <span>{error}</span>
          </div>
        </div>
      )}

      {/* Main Conversation & Knowledge Area */}
      <ChatWindow
        messages={messages}
        isLoading={isLoading}
        loadingStage={loadingStage}
        onSelectSuggestion={(prompt) => sendMessage(prompt)}
        subjects={availableSubjects}
        selectedSubject={selectedSubject}
        onSelectSubject={setSelectedSubject}
        isSubjectsLoading={isSubjectsLoading}
      />

      {/* Multimodal Knowledge Composer */}
      <MessageInput
        onSend={sendMessage}
        isLoading={isLoading}
        selectedSubject={selectedSubject}
        onSelectSubject={setSelectedSubject}
        subjects={availableSubjects}
        isSubjectsLoading={isSubjectsLoading}
      />
    </div>
  );
}

export default App;
