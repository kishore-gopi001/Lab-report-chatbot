from datetime import datetime

from processing.parser import load_csv
from processing.joins import join_labevents_with_metadata
from processing.lab_canonical_map import LAB_CANONICAL_MAP
from rules.rules_engine import evaluate_lab
from rules.thresholds import LAB_THRESHOLDS

from database.models import create_tables
from database.repository import (
    insert_lab_results_bulk,
    clear_lab_interpretations
)


def canonicalize(name):
    return LAB_CANONICAL_MAP.get(name)


def main():
    # Step 1: Ensure DB + tables exist
    create_tables()

    # ✅ IMPORTANT: Clear old data to make ingestion idempotent (DEV MODE)
    clear_lab_interpretations()

    # Step 2: Load CSVs
    labevents_df = load_csv("data/raw/labevents.csv")
    d_labitems_df = load_csv("data/raw/d_labitems.csv")
    patients_df = load_csv("data/raw/patients.csv")
    admissions_df = load_csv("data/raw/admissions.csv")

    # OPTIONAL (recommended during development)
    # labevents_df = labevents_df.sample(30000, random_state=42)

    # Step 3: Join (Day 4)
    df = join_labevents_with_metadata(
        labevents_df,
        d_labitems_df,
        patients_df,
        admissions_df
    )

    # Step 4: Canonical lab names
    df["canonical_test_name"] = df["test_name"].apply(canonicalize)

    # Step 5: Apply rules (Day 5)
    df["rule_result"] = df.apply(
        lambda row: evaluate_lab(row, LAB_THRESHOLDS),
        axis=1
    )

    # Step 6: Persist results (BATCH INSERT)
    records = []
    BATCH_SIZE = 1000
    total = len(df)

    for idx, row in df.iterrows():
        if row["canonical_test_name"] is None:
            continue

        result = row["rule_result"]

        records.append((
            row["subject_id"],
            row["hadm_id"],
            row["canonical_test_name"],
            row["valuenum"],
            row.get("valueuom"),
            row["gender"],
            result["status"],
            result["reason"],
            datetime.utcnow().isoformat(),
            0
        ))

        # Insert in batches
        if len(records) >= BATCH_SIZE:
            insert_lab_results_bulk(records)
            records.clear()

            if idx % 10000 == 0:
                print(f"Inserted {idx}/{total} rows...")

    # Insert any remaining records
    if records:
        insert_lab_results_bulk(records)

    print("✅ Lab interpretations stored successfully (bulk insert, idempotent).")


if __name__ == "__main__":
    main()
