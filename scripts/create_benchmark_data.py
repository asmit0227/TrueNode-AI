import json
from pathlib import Path


# Folders
data_folder = Path("data/sample_documents")
evaluation_folder = Path("evaluation")

data_folder.mkdir(parents=True, exist_ok=True)
evaluation_folder.mkdir(parents=True, exist_ok=True)


# Synthetic company documents

documents = {

    "travel_policy.txt": """
NOVATECH SOLUTIONS
TRAVEL POLICY

1. Travel Booking
Employees must book official travel using the company travel portal.

2. Travel Approval
Employees must obtain manager approval at least 5 business days before travel.

3. Flight Policy
Employees must use economy class for domestic flights.
""",

    "expense_policy.txt": """
NOVATECH SOLUTIONS
EXPENSE REIMBURSEMENT POLICY

1. Expense Submission
Employees must submit expense claims within 10 calendar days of purchase.

2. Receipts
Receipts are mandatory for individual expenses above INR 500.

3. Approval
The Finance team provides final approval for expense reimbursements.
""",

    "onboarding_policy.txt": """
NOVATECH SOLUTIONS
EMPLOYEE ONBOARDING POLICY

1. Identity Verification
New employees must complete identity verification on their first working day.

2. IT Accounts
The IT department provides employee accounts within 1 business day.

3. Orientation
New employees must attend company orientation during their first week.
""",

    "access_policy.txt": """
NOVATECH SOLUTIONS
SYSTEM ACCESS MANAGEMENT POLICY

1. Access Requests
Employees must request restricted system access through the IT ticket portal.

2. Access Approval
Restricted system access requires approval from the reporting manager
and the system owner.

3. Access Revocation
Employee system access must be revoked within 24 hours after departure.
""",

    "incident_response.txt": """
NOVATECH SOLUTIONS
SECURITY INCIDENT RESPONSE POLICY

1. Critical Incident Reporting
Priority 1 (P1) incidents must be reported to the Security Operations Center immediately.

2. Response Time
The incident response team must acknowledge P1 incidents within 15 minutes.

3. Post-Incident Review
An incident postmortem must be completed within 3 business days.
""",

    "procurement_policy.txt": """
NOVATECH SOLUTIONS
PROCUREMENT POLICY

1. Purchase Requests
Employees must submit purchase requests through the procurement portal.

2. Vendor Comparison
Purchases above INR 50000 require comparison of at least 3 vendors.

3. High-Value Approval
Purchases above INR 200000 require CFO approval.
"""
}


# Save documents
for filename, content in documents.items():

    file_path = data_folder / filename

    file_path.write_text(
        content.strip(),
        encoding="utf-8"
    )

    print("Created:", filename)


print("\nTotal New Documents:", len(documents))


# GOLDEN EVALUATION QUESTIONS

questions = [

    # HR Policy
    (
        "How many annual leave days do employees receive?",
        ["hr_leave_policy.txt"],
        "18 days per year"
    ),

    (
        "Can employees work from home?",
        ["hr_leave_policy.txt"],
        "Yes, with manager and HR approval"
    ),

    # IT Support
    (
        "When should employees report lost company laptops?",
        ["it_support.txt"],
        "Within 2 hours"
    ),

    (
        "How can employees reset passwords?",
        ["it_support.txt"],
        "Using the company self-service portal"
    ),

    # Security Policy
    (
        "Can employees share company passwords?",
        ["security_policy.txt"],
        "No, password sharing is prohibited"
    ),

    (
        "Who should employees report security incidents to?",
        ["security_policy.txt"],
        "The IT security team"
    ),

    # Employee Handbook
    (
        "What are the company's office hours?",
        ["employee_handbook.txt"],
        "9 AM to 6 PM"
    ),

    (
        "How should employees mark attendance?",
        ["employee_handbook.txt"],
        "Employees must mark attendance daily"
    ),

    # Travel Policy
    (
        "Where should employees book official travel?",
        ["travel_policy.txt"],
        "Company travel portal"
    ),

    (
        "How many days before travel is manager approval required?",
        ["travel_policy.txt"],
        "At least 5 business days before travel"
    ),

    (
        "Which flight class is allowed for domestic travel?",
        ["travel_policy.txt"],
        "Economy class"
    ),

    # Expense Policy
    (
        "When must employees submit expense claims?",
        ["expense_policy.txt"],
        "Within 10 calendar days of purchase"
    ),

    (
        "Above what amount are expense receipts mandatory?",
        ["expense_policy.txt"],
        "Above INR 500"
    ),

    (
        "Who gives final approval for reimbursements?",
        ["expense_policy.txt"],
        "The Finance team"
    ),

    # Onboarding Policy
    (
        "When must new employees complete identity verification?",
        ["onboarding_policy.txt"],
        "On their first working day"
    ),

    (
        "How quickly does IT provide employee accounts?",
        ["onboarding_policy.txt"],
        "Within 1 business day"
    ),

    (
        "When should employees attend company orientation?",
        ["onboarding_policy.txt"],
        "During their first week"
    ),

    # Access Policy
    (
        "Where should employees request restricted system access?",
        ["access_policy.txt"],
        "Through the IT ticket portal"
    ),

    (
        "Who must approve restricted system access?",
        ["access_policy.txt"],
        "Reporting manager and system owner"
    ),

    (
        "How quickly must access be revoked after an employee leaves?",
        ["access_policy.txt"],
        "Within 24 hours"
    ),

    # Incident Response
    (
        "Where should P1 incidents be reported?",
        ["incident_response.txt"],
        "Security Operations Center"
    ),

    (
        "How quickly must P1 incidents be acknowledged?",
        ["incident_response.txt"],
        "Within 15 minutes"
    ),

    (
        "When must an incident postmortem be completed?",
        ["incident_response.txt"],
        "Within 3 business days"
    ),

    # Procurement
    (
        "Where should employees submit purchase requests?",
        ["procurement_policy.txt"],
        "Procurement portal"
    ),

    (
        "When is vendor comparison required?",
        ["procurement_policy.txt"],
        "For purchases above INR 50000"
    ),

    (
        "Which purchases require CFO approval?",
        ["procurement_policy.txt"],
        "Purchases above INR 200000"
    ),

    # Multi-document Questions
    (
        "Who approves remote work and restricted system access?",
        ["hr_leave_policy.txt", "access_policy.txt"],
        "Remote work requires manager and HR approval. "
        "Restricted access requires reporting manager and system owner approval."
    ),

    (
        "How do employees reset passwords and report security incidents?",
        ["it_support.txt", "security_policy.txt"],
        "Reset passwords through the self-service portal "
        "and report security incidents to the IT security team."
    ),

    # Unanswerable Questions
    (
        "What is the company's maternity leave policy?",
        [],
        "Information unavailable in the documents"
    ),

    (
        "Does the company provide free office transportation?",
        [],
        "Information unavailable in the documents"
    ),

    (
        "Who is the Prime Minister of India?",
        [],
        "Information unavailable in the documents"
    ),

    (
        "Does the company reimburse home internet bills?",
        [],
        "Information unavailable in the documents"
    )
]


# SAVE GOLDEN DATASET

golden_dataset = []

for index, item in enumerate(questions, start=1):

    question = item[0]
    sources = item[1]
    expected_answer = item[2]

    if len(sources) == 0:
        category = "unanswerable"

    elif len(sources) > 1:
        category = "multi_document"

    else:
        category = "single_document"

    # Every fourth question goes into the test set
    if index % 4 == 0:
        split = "test"
    else:
        split = "dev"

    golden_dataset.append({
        "id": index,
        "question": question,
        "expected_answer": expected_answer,
        "expected_sources": sources,
        "answerable": len(sources) > 0,
        "category": category,
        "split": split
    })


output_file = evaluation_folder / "golden_dataset.json"

with open(output_file, "w", encoding="utf-8") as file:

    json.dump(
        golden_dataset,
        file,
        indent=4,
        ensure_ascii=False
    )


print("\nGolden Dataset Created!")

print("Total Questions:", len(golden_dataset))

print(
    "Development Questions:",
    sum(1 for item in golden_dataset if item["split"] == "dev")
)

print(
    "Test Questions:",
    sum(1 for item in golden_dataset if item["split"] == "test")
)