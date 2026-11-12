import json
import csv

from backend.core.resources import rag


# Step 1: Load Golden Dataset

with open(
    "evaluation/golden_dataset.json",
    "r",
    encoding="utf-8"
) as file:

    questions = json.load(file)


# Step 2: Initialize Counters

total = len(questions)

correct = 0

answerable_total = 0
answerable_correct = 0

unanswerable_total = 0
unanswerable_correct = 0

results = []


# Step 3: Evaluate Questions

try:

    for item in questions:

        question = item["question"]

        expected_answerable = item["answerable"]

        print("\n" + "=" * 60)
        print("Question:", question)

        # Generate RAG answer
        response = rag.ask(question)

        answer = response["answer"]
        sources = response.get("sources", [])

        print("Answer:", answer)
        print("Sources:", sources)

        # Check whether AI refused
        refusal = (
            "i could not find this information"
            in answer.lower()
            or "no relevant documents found"
            in answer.lower()
        )

        # Step 4: Check Answerability

        if expected_answerable:

            answerable_total += 1

            # Answerable question should not be refused
            passed = not refusal

            if passed:
                answerable_correct += 1

        else:

            unanswerable_total += 1

            # Unanswerable question should be refused
            # and no supporting sources should be shown
            passed = refusal and len(sources) == 0

            if passed:
                unanswerable_correct += 1

        if passed:
            correct += 1

        print("Expected Answerable:", expected_answerable)
        print("Test Passed:", passed)

        results.append({
            "question": question,
            "split": item["split"],
            "expected_answerable": expected_answerable,
            "answer": answer,
            "sources": ", ".join(sources),
            "passed": passed
        })

finally:

    rag.close()


# Step 5: Calculate Final Metrics

accuracy = correct / total if total else 0

answerable_rate = (
    answerable_correct / answerable_total
    if answerable_total else 0
)

refusal_rate = (
    unanswerable_correct / unanswerable_total
    if unanswerable_total else 0
)


print("\n========== FINAL ANSWERABILITY EVALUATION ==========")

print("Total Questions:", total)

print("Answerable Questions:", answerable_total)

print("Unanswerable Questions:", unanswerable_total)

print("Answerability Detection Rate:", round(accuracy, 4))

print("Answerable Response Rate:", round(answerable_rate, 4))

print("Correct Refusal Rate:", round(refusal_rate, 4))


# Step 6: Save Results

with open(
    "evaluation/answerability_results.csv",
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=[
            "question",
            "split",
            "expected_answerable",
            "answer",
            "sources",
            "passed"
        ]
    )

    writer.writeheader()
    writer.writerows(results)


print("\nEvaluation results saved successfully!")