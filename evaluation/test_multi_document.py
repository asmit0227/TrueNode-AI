from backend.core.resources import rag


questions = [
    "Who approves remote work and restricted system access?",

    "How do employees reset passwords and report security incidents?"
]


try:

    for question in questions:

        print("\n" + "=" * 60)

        print("QUESTION:")
        print(question)

        response = rag.ask(
            question,
            include_context=True
        )

        print("\nRETRIEVED CONTEXT:")
        print(response.get("context", ""))

        print("\nANSWER:")
        print(response["answer"])

        print("\nSOURCES:")
        print(response["sources"])

finally:

    rag.close()