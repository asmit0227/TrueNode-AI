import csv


# Step 1: Read evaluation results

with open(
    "evaluation/faithfulness_results.csv",
    "r",
    encoding="utf-8"
) as file:

    reader = csv.DictReader(file)

    results = list(reader)


# Step 2: Available human verdicts

labels = {
    "1": "SUPPORTED",
    "2": "UNSUPPORTED",
    "3": "CORRECT_REFUSAL",
    "4": "INCORRECT_REFUSAL",
    "5": "NEEDS_REVIEW"
}


# Step 3: Review answers

human_results = []

for item in results:

    print("\n" + "=" * 60)

    print("QUESTION:")
    print(item["question"])

    print("\nRETRIEVED CONTEXT:")
    print(item["context"])

    print("\nAI ANSWER:")
    print(item["answer"])

    print("\nLLM JUDGE:", item["verdict"])

    print("\nSelect Human Verdict:")

    for key, value in labels.items():
        print(key, value)

    while True:

        choice = input("\nEnter choice (1-5): ")

        if choice in labels:
            break

        print("Invalid choice. Enter 1 to 5.")

    human_verdict = labels[choice]

    human_results.append({
        "question": item["question"],
        "answer": item["answer"],
        "llm_verdict": item["verdict"],
        "human_verdict": human_verdict
    })


# Step 4: Save human evaluation

with open(
    "evaluation/human_review_results.csv",
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=[
            "question",
            "answer",
            "llm_verdict",
            "human_verdict"
        ]
    )

    writer.writeheader()

    writer.writerows(human_results)


# Step 5: Calculate agreement

total = len(human_results)

agreements = 0

for item in human_results:

    if item["llm_verdict"] == item["human_verdict"]:
        agreements += 1

agreement_rate = agreements / total if total else 0

print("\n========== HUMAN EVALUATION ==========")

print("Total Reviews:", total)

print("Judge-Human Agreements:", agreements)

print("Agreement Rate:", round(agreement_rate, 4))

print("\nHuman review results saved successfully!")