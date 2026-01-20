from processing.parser import load_csv
from processing.validator import validate_schema
from processing.schema import LABEVENTS_SCHEMA

df = load_csv("data/raw/labevents.csv")
validate_schema(df, LABEVENTS_SCHEMA, "labevents")

print("labevents schema validated")
