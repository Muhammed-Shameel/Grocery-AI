type SearchBoxProps = {
    question: string;
    setQuestion: React.Dispatch<React.SetStateAction<string>>;
    askQuestion: () => void;
    isLoading: boolean;
};

function SearchBox({
    question,
    setQuestion,
    askQuestion,
    isLoading,
}: SearchBoxProps) {
    return (
        <div className="flex flex-col gap-4">

            <input
                type="text"
                placeholder="Ask anything about food or nutrition..."
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={(e) => {
                    if (e.key === "Enter" && !isLoading) {
                        askQuestion();
                    }
                }}
                disabled={isLoading}
                className="
                    w-full
                    rounded-xl
                    border
                    border-gray-700
                    bg-gray-900
                    px-5
                    py-4
                    text-white
                    placeholder:text-gray-500
                    focus:border-green-500
                    focus:outline-none
                    disabled:opacity-50
                "
            />

            <button
                onClick={askQuestion}
                disabled={isLoading}
                className="
                    rounded-xl
                    bg-green-600
                    py-4
                    font-semibold
                    text-white
                    transition
                    hover:bg-green-700
                    active:scale-95
                    disabled:opacity-50
                    disabled:cursor-not-allowed
                "
            >
                {isLoading ? 'Thinking...' : 'Ask Question'}
            </button>

        </div>
    );
}

export default SearchBox;