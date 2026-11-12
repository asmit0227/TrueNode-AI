import re

from backend.core.resources import rag


# Evaluation questions and expected citations
questions = [

    {
        "question": "Who approves remote work and restricted system access?",

        "facts": [
            {
                "name": "Remote Work Approval",
                "keywords": ["remote work", "manager", "HR"],
                "source": "hr_leave_policy.txt"
            },
            {
                "name": "Restricted Access Approval",
                "keywords": ["restricted system access", "system owner"],
                "source": "access_policy.txt"
            }
        ]
    },

    {
        "question": "How do employees reset passwords and report security incidents?",

        "facts": [
            {
                "name": "Password Reset",
                "keywords": ["passwords", "self service portal"],
                "source": "it_support.txt"
            },
            {
                "name": "Security Incident Reporting",
                "keywords": ["security incidents", "IT security team"],
                "source": "security_policy.txt"
            },
            {
                "name": "P1 Incident Reporting",
                "keywords": ["priority 1", "security operations center"],
                "source": "incident_response.txt",
                "optional": True
            }
        ]
    }
]


# Normalize text
def normalize(text):

    text = text.lower()

    text = re.sub(r"[^\w]+", " ", text)

    return " ".join(text.split())


# Check keywords
def contains_keywords(text, keywords):

    text = normalize(text)

    for keyword in keywords:

        if normalize(keyword) not in text:
            return False

    return True


# Run evaluation
total = 0
correct = 0


try:

    for item in questions:

        question = item["question"]

        print("\n" + "=" * 60)
        print("QUESTION:", question)

        response = rag.ask(
            question,
            include_context=True
        )

        answer = response["answer"]
        context = response.get("context", "")

        print("\nANSWER:")
        print(answer)

        # Extract source ID mappings
        source_pairs = re.findall(
            r"\[(S\d+)\]\s*Source:\s*([^\n]+)",
            context
        )

        source_map = dict(source_pairs)

        print("\nSOURCE MAP:", source_map)

        # Split answer into sentences
        sentences = re.split(
            r"(?<=[.!?])\s+|\n+",
            answer
        )

        for fact in item["facts"]:

            # Optional P1 fact: test only when mentioned
            if fact.get("optional"):

                normalized_answer = normalize(answer)

                if (
                    "priority 1" not in normalized_answer
                    and "p1" not in normalized_answer
                ):
                    continue

            total += 1

            matched_sentence = None

            # Find sentence containing expected facts
            for sentence in sentences:

                if contains_keywords(
                    sentence,
                    fact["keywords"]
                ):
                    matched_sentence = sentence
                    break

            if matched_sentence is None:

                print(fact["name"], "-> FAIL (Fact missing)")
                continue

            # Extract citations from matching sentence
            cited_ids = re.findall(
                r"\[\s*(S\d+)\s*\]",
                matched_sentence,
                flags=re.IGNORECASE
            )

            # Check whether expected source is cited
            passed = False

            for citation_id in cited_ids:

                source = source_map.get(
                    citation_id.upper()
                )

                if source == fact["source"]:
                    passed = True

            if passed:
                correct += 1

            print(
                fact["name"],
                "->",
                "PASS" if passed else "FAIL"
            )

finally:

    rag.close()


# Final results
print("\n========== CITATION EVALUATION ==========")

print("Total Fact Checks:", total)

print("Correct Source Citations:", correct)

print(
    "Citation Match Rate:",
    round(correct / total, 4) if total else 0
)