import pandas as pd # type: ignore

def enrich_with_omr(
    labs_df: pd.DataFrame,
    omr_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Enrich labs with baseline vitals like BMI or eGFR (optional).
    """

    if omr_df is None or omr_df.empty:
        return labs_df

    enriched = labs_df.merge(
        omr_df[["subject_id", "result_name", "result_value"]],
        on="subject_id",
        how="left"
    )

    return enriched
