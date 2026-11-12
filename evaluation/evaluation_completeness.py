import json
import re

from backend.core.resources import rag


# Step 1: Load Golden Dataset

with open(
    "evaluation/golden_dataset.json",
    "r",
    encoding="utf-8"
) as file:

    questions = json.load(file)


# Step 2: Expected facts for multi-document questions

expected_facts = {

    "Who approves remote work and restricted system access?": [

        {
            "name": "Remote Work Approval",
            "keywords": [
                "remote work",
                "manager",
                "HR"
            ]
        },

        {
            "name": "System Access Approval",
            "keywords": [
                "restricted system access",
                "reporting manager",
                "system owner"
            ]
        }
    ],

    "How do employees reset passwords and report security incidents?": [

        {
            "name": "Password Reset",
            "keywords": [
                "reset",
                "self-service portal"
            ]
        },

        {
            "name": "Security Incident Reporting",
            "keywords": [
                "security incidents",
                "IT security team"
            ]
        }
    ]
}


# Step 3: Normalize text

def normalize(text):

    text = text.lower()

    # Replace punctuation and hyphens with spaces
    text = re.sub(r"[^\w]+", " ", text)

    text = " ".join(text.split())

    return " " + text + " "


# Step 4: Check expected keywords

def check_fact(answer, keywords):

    answer = normalize(answer)

    for keyword in keywords:

        keyword = normalize(keyword)

        if keyword not in answer:
            return False

    return True


# Step 5: Run Evaluation

total_questions = 0
complete_answers = 0

total_facts = 0
correct_facts = 0


try:

    for item in questions:

        if item["category"] != "multi_document":
            continue

        question = item["question"]

        facts = expected_facts[question]

        total_questions += 1

        print("\n" + "=" * 60)

        print("QUESTION:", question)

        # Generate RAG answer
        response = rag.ask(
            question,
            include_context=True
        )

        answer = response["answer"]
        sources = response["sources"]
        context = response.get("context", "")

        print("\nANSWER:")
        print(answer)

        print("\nFACT VERIFICATION:")

        matched_facts = 0

        for fact in facts:

            passed = check_fact(
                answer,
                fact["keywords"]
            )

            total_facts += 1

            if passed:
                matched_facts += 1
                correct_facts += 1

            print(
                fact["name"],
                "->",
                "PASS" if passed else "FAIL"
            )

        # Check expected source documents in context
        expected_sources = item["expected_sources"]

        missing_sources = []

        for source in expected_sources:

            if f"Source: {source}" not in context:
                missing_sources.append(source)

        print("\nExpected Sources:", expected_sources)
        print("Returned Sources:", sources)
        print("Missing Context Sources:", missing_sources)

        # Calculate completeness
        completeness = matched_facts / len(facts)

        print("\nAnswer Completeness:", round(completeness, 4))

        if completeness == 1 and not missing_sources:
            complete_answers += 1


finally:

    rag.close()


# Step 6: Final Metrics

print("\n========== COMPLETENESS EVALUATION ==========")

question_completeness = (
    complete_answers / total_questions
    if total_questions else 0
)

fact_coverage = (
    correct_facts / total_facts
    if total_facts else 0
)

print("Total Multi-document Questions:", total_questions)

print("Complete Answers:", complete_answers)

print("Question Completeness Rate:", round(question_completeness, 4))

print("Required Fact Coverage:", round(fact_coverage, 4))