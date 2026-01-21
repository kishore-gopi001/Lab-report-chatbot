from processing.parser import load_csv
from processing.joins import join_labevents_with_metadata
from processing.lab_canonical_map import LAB_CANONICAL_MAP
from rules.rules_engine import evaluate_lab
from rules.thresholds import LAB_THRESHOLDS


def canonicalize_lab_name(name):
    return LAB_CANONICAL_MAP.get(name)


# Load CSVs
labevents_df = load_csv("data/raw/labevents.csv")
d_labitems_df = load_csv("data/raw/d_labitems.csv")
patients_df = load_csv("data/raw/patients.csv")
admissions_df = load_csv("data/raw/admissions.csv")

# Day 4 join
df = join_labevents_with_metadata(
    labevents_df,
    d_labitems_df,
    patients_df,
    admissions_df
)

# Canonical mapping
df["canonical_test_name"] = df["test_name"].apply(canonicalize_lab_name)

# Day 5 rules (NO assign hack)
df["rule_result"] = df.apply(
    lambda row: evaluate_lab(row, LAB_THRESHOLDS),
    axis=1
)

print(
    df[
        ["test_name", "canonical_test_name", "valuenum", "gender", "rule_result"]
    ].head(15)
)
