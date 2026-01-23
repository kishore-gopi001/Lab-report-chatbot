from app.vector.vector_store import add_document

def seed_vectors():
    add_document(
        "What tests were done for the patient",
        intent="LIST_TESTS"
    )
    add_document(
        "Which lab results are abnormal",
        intent="ABNORMAL_LABS"
    )
    add_document(
        "Any critical lab values",
        intent="CRITICAL_LABS"
    )
    add_document(
        "What is the value of hemoglobin",
        intent="SPECIFIC_TEST"
    )
    add_document(
        "Explain abnormal lab findings",
        intent="AI_SUMMARY"
    )
