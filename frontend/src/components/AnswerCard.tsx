type AnswerCardProps = {
    answer: string;
};

function AnswerCard({ answer }: AnswerCardProps) {

    if (!answer) {
        return null;
    }

    return (
        <div className="mt-8 rounded-2xl border border-gray-800 bg-gray-900 p-6 shadow-lg">

            <h2 className="mb-4 text-xl font-semibold text-green-400">
                Answer
            </h2>

            <p className="whitespace-pre-wrap leading-7 text-gray-200">
                {answer}
            </p>

        </div>
    );
}

export default AnswerCard;