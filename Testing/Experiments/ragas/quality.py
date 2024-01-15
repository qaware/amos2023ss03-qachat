import ragas.metrics
from ragas import evaluate

from datasets import Dataset

# answer: produced by chatbot
# ground_truths: best answer for this question
# contexts: retrieved chunks from the search engine on which the answer is based on
single_query_result1 = {
    "question": "How is travelling organized in our company?",
    "answer": "The requested information is not available in the retrieved data. Please try another query or topic.",
    "ground_truths": ["No data available"],
    "contexts": ["The sun is yellow"]
}

single_query_result2 = {
    "question": "What is the weather in munich?",
    "answer": "The temperature in Munich is 10 degrees Celsius",
    "ground_truths": ["The weather is cloudy and the temperature is 10 degrees Celsius"],
    "contexts": ["Munich: Temperature 10°C, cloudy\nStuttgart: Temperature 20°C, sunny", "The sun is yellow."]
}

query_results = {
    "question": [single_query_result2["question"]],
    "answer": [single_query_result2["answer"]],
    "ground_truths": [single_query_result2["ground_truths"]],
    "contexts": [single_query_result2["contexts"]]
}

result = evaluate(
    Dataset.from_dict(query_results),
    metrics=[
        ragas.metrics.context_precision,  # question, context
        ragas.metrics.faithfulness,
        ragas.metrics.context_recall,
        ragas.metrics.context_relevancy,
        ragas.metrics.answer_relevancy,
        ragas.metrics.answer_correctness,  # question, answer, ground_truths
        ragas.metrics.answer_similarity  # answer, ground_truths via embedding
    ],
)

print(result)
# {
#   'answer_correctness': 0.2103,
#   'context_precision': 0.0000,
#   'faithfulness': 0.0000,
#   'answer_relevancy': 0.0000,
#   'context_recall': 1.0000,
#   'context_relevancy': 0.0000,
#   'answer_similarity': 0.8413}

# result.to_pandas().to_csv("result.csv")
