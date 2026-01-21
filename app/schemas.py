from typing import List
from pydantic import BaseModel # type: ignore


class LabResult(BaseModel):
    subject_id: int
    hadm_id: int
    test_name: str
    value: float
    unit: str | None
    gender: str
    status: str
    reason: str


class ReportItem(BaseModel):
    test_name: str
    status: str
    patient_count: int
