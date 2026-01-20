from processing.parser import load_csv
from processing.joins import join_labevents_with_metadata

labevents_df = load_csv("data/raw/labevents.csv")
d_labitems_df = load_csv("data/raw/d_labitems.csv")
patients_df = load_csv("data/raw/patients.csv")
admissions_df = load_csv("data/raw/admissions.csv")

df = join_labevents_with_metadata(
    labevents_df,
    d_labitems_df,
    patients_df,
    admissions_df
)

print(df[[
    "subject_id",
    "valuenum",
    "valueuom",
    "age",
    "gender",
    "admittime"
]].head())

