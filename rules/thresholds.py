"""
Synthetic / illustrative clinical thresholds.

NOTE:
- These simulate reference ranges
- Designed to be replaceable by LIS / FHIR in production
- NOT medical advice
"""

LAB_THRESHOLDS = {
    "Hemoglobin": {
        "M": {"min": 13.0, "max": 17.0, "critical_min": 7.0},
        "F": {"min": 12.0, "max": 15.0, "critical_min": 7.0}
    },

    "WBC": {
        "ALL": {"min": 4.0, "max": 11.0, "critical_max": 20.0}
    },

    "Platelets": {
        "ALL": {"min": 150.0, "max": 450.0, "critical_min": 50.0}
    },

    "Sodium": {
        "ALL": {"min": 135.0, "max": 145.0, "critical_min": 120.0, "critical_max": 160.0}
    },

    "Potassium": {
        "ALL": {"min": 3.5, "max": 5.0, "critical_min": 2.5, "critical_max": 6.5}
    },

    "Creatinine": {
        "M": {"min": 0.7, "max": 1.3, "critical_max": 5.0},
        "F": {"min": 0.6, "max": 1.1, "critical_max": 5.0}
    },

    "Blood Urea Nitrogen": {
        "ALL": {"min": 7.0, "max": 20.0, "critical_max": 100.0}
    },

    "Glucose": {
        "ALL": {"min": 70.0, "max": 140.0, "critical_min": 40.0, "critical_max": 400.0}
    },

    "Chloride": {
        "ALL": {"min": 98.0, "max": 107.0, "critical_min": 80.0, "critical_max": 120.0}
    },

    "Hematocrit": {
        "M": {"min": 41.0, "max": 50.0, "critical_min": 21.0, "critical_max": 60.0},
        "F": {"min": 36.0, "max": 44.0, "critical_min": 21.0, "critical_max": 60.0}
    },

    "Bicarbonate": {
        "ALL": {"min": 22.0, "max": 28.0, "critical_min": 10.0, "critical_max": 40.0}
    },

    "RBC": {
        "M": {"min": 4.7, "max": 6.1, "critical_min": 3.0},
        "F": {"min": 4.2, "max": 5.4, "critical_min": 3.0}
    }
}
# Additional lab tests and their thresholds can be added here as needed.