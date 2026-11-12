import csv
import time

from backend.core.resources import rag


# Step 1: Evaluation Dataset

questions = [
    {
        "question": "How many annual leave days do employees receive?",
        "expected": ["18", "annual leave"],
        "source": "hr_leave_policy.txt"
    },
    {
        "question": "How many sick leave days do employees receive?",
        "expected": ["10", "sick leave"],
        "source": "hr_leave_policy.txt"
    },
    {
        "question": "Can employees work from home?",
        "expected": ["manager", "HR"],
        "source": "hr_leave_policy.txt"
    },
    {
        "question": "How can employees reset passwords?",
        "expected": ["self", "service", "portal"],
        "source": "it_support.txt"
    },
    {
        "question": "Can employees share company passwords?",
        "expected": ["not", "share"],
        "source": "security_policy.txt"
    },
    {
        "question": "What are the company's office hours?",
        "expected": ["9", "6"],
        "source": "employee_handbook.txt"
    },
    {
        "question": "What is the company's maternity leave policy?",
        "expected": ["could not find"],
        "source": None
    },
    {
        "question": "Who is the Prime Minister of India?",
        "expected": ["could not find"],
        "source": None
    }
]


# Step 2: Evaluate Answers

results = []

try:

    for item in questions:

        question = item["question"]

        print("\nQuestion:", question)

        start_time = time.perf_counter()

        response = rag.ask(question)

        end_time = time.perf_counter()

        answer = response["answer"]

        sources = response["sources"]

        latency = round(end_time - start_time, 2)

        # Check expected keywords
        answer_correct = all(
            word.lower() in answer.lower()
            for word in item["expected"]
        )

        # Check supporting source
        if item["source"] is None:
            source_correct = len(sources) == 0

        else:
            source_correct = item["source"] in sources

        print("Answer:", answer)
        print("Sources:", sources)

        print("Answer Check:", answer_correct)
        print("Source Check:", source_correct)

        print("Latency:", latency, "seconds")

        results.append({
            "question": question,
            "answer": answer,
            "answer_check": answer_correct,
            "source_check": source_correct,
            "latency": latency
        })


    # Step 3: Calculate Final Metrics

    total = len(results)

    correct_answers = sum(
        result["answer_check"]
        for result in results
    )

    correct_sources = sum(
        result["source_check"]
        for result in results
    )

    total_latency = sum(
        result["latency"]
        for result in results
    )

    answer_score = correct_answers / total

    source_score = correct_sources / total

    avg_latency = total_latency / total

    print("\n========== FINAL EVALUATION ==========")

    print("Total Questions:", total)

    print("Answer Check Rate:", round(answer_score, 4))

    print("Source Match Rate:", round(source_score, 4))

    print("Average Latency:", round(avg_latency, 2), "seconds")


    # Step 4: Save Results

    with open(
        "evaluation/answer_results.csv",
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "question",
                "answer",
                "answer_check",
                "source_check",
                "latency"
            ]
        )

        writer.writeheader()

        writer.writerows(results)

    print("\nResults saved to evaluation/answer_results.csv")

finally:

    rag.close()