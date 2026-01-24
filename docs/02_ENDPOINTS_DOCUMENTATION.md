# API Endpoints Documentation

## Overview

The system provides **19 endpoints** across 3 categories:
- **2 Dashboard Pages** (HTML templates)
- **7 Report Endpoints** (Lab statistics & insights)
- **7 Chat Endpoints** (Chatbot & AI summaries)
- **3 Prediction Endpoints** (ML risk scoring)

---

## 1. DASHBOARD PAGES

### 1.1 General Lab Reports Dashboard
**Route:** `GET /dashboard`
- **Purpose:** Display lab statistics, trends, and reporting insights
- **Returns:** HTML page with charts and tables
- **Used:** ✅ YES
- **Frontend File:** `app/templates/dashboard.html`

**Components:**
- 5 summary cards (Total, Normal, Abnormal, Critical, Unknown labs)
- Bar chart - Lab tests affected
- Pie chart - Gender distribution
- Doughnut chart - Overall lab status
- Table - Top affected tests
- Critical alerts section

---

### 1.2 ML Risk Prediction Dashboard
**Route:** `GET /ml-dashboard`
- **Purpose:** Display patient risk predictions and ML-based insights
- **Returns:** HTML page with ML dashboards and tables
- **Used:** ✅ YES
- **Frontend File:** `app/templates/ml-dashboard.html`

**Components:**
- 5 KPI cards (0 Normal, 47 Abnormal, 53 Critical, Unreviewed count, High-risk count)
- Doughnut chart - Patient risk distribution
- Horizontal bar chart - Recent critical activity
- Table - High-risk patients with pagination (20 per page)
- Simple pagination (no filters)

---

## 2. REPORT ENDPOINTS (Lab Statistics & Insights)

### 2.1 Lab Summary Report
**Route:** `GET /reports/summary`
- **Purpose:** Get count of labs by status (NORMAL, ABNORMAL, CRITICAL, UNKNOWN)
- **Used:** ✅ YES (Dashboard + ML Dashboard)
- **Request:** None
- **Response:**
```json
[
  {"status": "NORMAL", "count": 1234},
  {"status": "ABNORMAL", "count": 2456},
  {"status": "CRITICAL", "count": 3421},
  {"status": "UNKNOWN", "count": 267}
]
```

**Frontend Usage:**
- `dashboard.js` → `loadSummary()` - Display 5 summary cards
- `dashboard.js` → `loadStatusChart()` - Doughnut chart

---

### 2.2 Lab by Test Report
**Route:** `GET /reports/by-lab`
- **Purpose:** Get patient count affected by each lab test
- **Used:** ✅ YES (Dashboard)
- **Request:** None
- **Response:**
```json
[
  {"test_name": "Glucose", "patient_count": 234},
  {"test_name": "Creatinine", "patient_count": 198},
  {"test_name": "WBC", "patient_count": 156}
]
```

**Frontend Usage:**
- `dashboard.js` → `loadLabChart()` - Bar chart of affected tests
- `dashboard.js` → `loadTopTestsTable()` - Table of top 10 tests

---

### 2.3 Lab by Gender Report
**Route:** `GET /reports/by-gender`
- **Purpose:** Get patient count by gender
- **Used:** ✅ YES (Dashboard)
- **Request:** None
- **Response:**
```json
[
  {"gender": "M", "patient_count": 3456},
  {"gender": "F", "patient_count": 2876},
  {"gender": "Unknown", "patient_count": 45}
]
```

**Frontend Usage:**
- `dashboard.js` → `loadGenderChart()` - Pie chart

---

### 2.4 Unreviewed Critical Alerts
**Route:** `GET /reports/unreviewed-critical`
- **Purpose:** Get list of unreviewed critical lab records
- **Used:** ✅ YES (Dashboard)
- **Request:** None
- **Response:**
```json
[
  {
    "subject_id": 123,
    "test_name": "Glucose",
    "value": 450,
    "status": "CRITICAL",
    "processed_time": "2024-01-20T10:30:00"
  }
]
```

**Frontend Usage:**
- `dashboard.js` → `loadCriticalAlerts()` - Display critical alert items

---

### 2.5 Unreviewed Critical Summary
**Route:** `GET /reports/unreviewed-critical-summary`
- **Purpose:** Get count of unreviewed critical records
- **Used:** ✅ YES (ML Dashboard)
- **Request:** None
- **Response:**
```json
{
  "total_unreviewed": 54,
  "affected_patients": 32
}
```

**Frontend Usage:**
- `ml-dashboard.js` → `loadUnreviewedCriticalSummary()` - Display summary cards

---

### 2.6 Recent Critical Activity
**Route:** `GET /reports/recent-critical`
- **Purpose:** Get recent critical lab cases by test name
- **Used:** ✅ YES (ML Dashboard)
- **Request:** None
- **Response:**
```json
[
  {"test_name": "Glucose", "count": 12},
  {"test_name": "Creatinine", "count": 8},
  {"test_name": "WBC", "count": 6}
]
```

**Frontend Usage:**
- `ml-dashboard.js` → `loadRecentCriticalChart()` - Horizontal bar chart

---

### 2.7 Patient Risk Distribution (Report)
**Route:** `GET /reports/patient-risk`
- **Purpose:** Get count of patients by risk classification
- **Used:** ✅ YES (ML Dashboard)
- **Request:** None
- **Response:**
```json
{
  "NORMAL": 0,
  "ABNORMAL": 47,
  "CRITICAL": 53
}
```

**Frontend Usage:**
- `ml-dashboard.js` → `loadPatientRiskChart()` - Doughnut chart

---

### 2.8 High-Risk Patients Count
**Route:** `GET /reports/high-risk-patients`
- **Purpose:** Count of patients with at least one CRITICAL lab
- **Used:** ✅ YES (ML Dashboard)
- **Request:** None
- **Response:**
```json
{
  "critical_patients": 54
}
```

**Frontend Usage:**
- `ml-dashboard.js` → `loadHighRiskPatientCount()` - KPI card

**Note:** Returns 54 (database count), not 53 (ML prediction count)

---

## 3. CHAT ENDPOINTS (Chatbot & AI Services)

### 3.1 Patient Basic Labs
**Route:** `GET /chat/patient/{subject_id}`
- **Purpose:** Get all lab records for a specific patient
- **Used:** ❌ NO (API exists but not called in UI)
- **Request:** 
  - `subject_id` (path parameter): Patient ID
- **Response:**
```json
[
  {"test_name": "Glucose", "value": 125, "status": "ABNORMAL"},
  {"test_name": "Creatinine", "value": 1.2, "status": "NORMAL"}
]
```

---

### 3.2 Patient Abnormal Labs
**Route:** `GET /chat/patient/{subject_id}/abnormal`
- **Purpose:** Get only abnormal lab records for a patient
- **Used:** ❌ NO (API exists but not called in UI)
- **Request:**
  - `subject_id` (path parameter): Patient ID
- **Response:**
```json
[
  {"test_name": "Glucose", "value": 450, "status": "ABNORMAL"},
  {"test_name": "WBC", "value": 2.1, "status": "ABNORMAL"}
]
```

---

### 3.3 Patient Critical Labs
**Route:** `GET /chat/patient/{subject_id}/critical`
- **Purpose:** Get only critical lab records for a patient
- **Used:** ❌ NO (API exists but not called in UI)
- **Request:**
  - `subject_id` (path parameter): Patient ID
- **Response:**
```json
[
  {"test_name": "Glucose", "value": 550, "status": "CRITICAL"}
]
```

---

### 3.4 AI Summary Generation
**Route:** `GET /chat/patient/{subject_id}/ai-summary`
- **Purpose:** Generate AI summary of patient's lab data (background task)
- **Used:** ❌ NO (API exists but not called in current UI)
- **Request:**
  - `subject_id` (path parameter): Patient ID
- **Response (While Generating):**
```json
{
  "message": "Generating AI summary. This may take a few seconds. Please refresh shortly."
}
```
- **Response (When Ready):**
```json
{
  "subject_id": 123,
  "summary": "Patient has multiple abnormal lab values including...",
  "generated_at": "2024-01-20T10:30:00"
}
```

---

### 3.5 Chat with Patient Data
**Route:** `POST /chat/patient/{subject_id}/ask`
- **Purpose:** Ask questions about a patient's lab data (rule-based Q&A)
- **Used:** ❌ NO (API exists but not called in current UI)
- **Request:**
```json
{
  "question": "What are the critical labs for this patient?"
}
```
- **Response:**
```json
{
  "subject_id": 123,
  "question": "What are the critical labs for this patient?",
  "answer": "The patient has critical Glucose (550), Creatinine (2.8)...",
  "confidence_score": 0.95
}
```

**Confidence Scoring:**
- Critical labs mentioned: 0.95
- Abnormal labs mentioned: 0.90
- Default: 0.85
- Disclaimer included: 0.30

---

## 4. PREDICTION ENDPOINTS (ML Risk Scoring)

### 4.1 Predict Patient Risk (Individual)
**Route:** `GET /predict/patient/{subject_id}/risk`
- **Purpose:** Predict risk score for a specific patient using ML model
- **Used:** ❌ NO (API exists but not called in UI)
- **Request:**
  - `subject_id` (path parameter): Patient ID
- **Response:**
```json
{
  "subject_id": 123,
  "risk_level": 2,
  "risk_label": "CRITICAL",
  "confidence": 0.92,
  "probabilities": {
    "NORMAL": 0.05,
    "ABNORMAL": 0.03,
    "CRITICAL": 0.92
  }
}
```

---

### 4.2 Risk Distribution
**Route:** `GET /predict/risk-distribution`
- **Purpose:** Get distribution of all patients across risk levels (based on 100 samples)
- **Used:** ✅ YES (ML Dashboard)
- **Request:** None
- **Response:**
```json
{
  "NORMAL": 0,
  "ABNORMAL": 47,
  "CRITICAL": 53,
  "total": 100
}
```

**Frontend Usage:**
- `ml-dashboard.js` → `loadRiskDistribution()` - Display 3 KPI cards

---

### 4.3 High-Risk Patients (ML Predictions)
**Route:** `GET /predict/high-risk?risk_level=2&limit=100`
- **Purpose:** Get patients predicted as high-risk by ML model with pagination
- **Used:** ✅ YES (ML Dashboard)
- **Query Parameters:**
  - `risk_level` (default: 2) → 1 = ABNORMAL or higher, 2 = CRITICAL only
  - `limit` (default: 50) → How many patients to analyze
- **Response:**
```json
{
  "risk_level": 2,
  "total": 53,
  "limit": 100,
  "patients": [
    {
      "subject_id": 456,
      "risk_level": 2,
      "risk_label": "CRITICAL",
      "confidence": 0.96,
      "probability_normal": 0.02,
      "probability_abnormal": 0.02,
      "probability_critical": 0.96
    }
  ]
}
```

**Frontend Usage:**
- `ml-dashboard.js` → `loadHighRiskPatients()` - Table with pagination
- Initial load: `loadHighRiskPatients(2, 100)` → 53 critical patients shown 20 per page

---

### 4.4 All Patients Risk Scores
**Route:** `GET /predict/all-patients?limit=100`
- **Purpose:** Get risk scores for all patients (paginated export)
- **Used:** ❌ NO (API exists but not called in UI)
- **Query Parameters:**
  - `limit` (default: 100) → How many patients to fetch
- **Response:**
```json
[
  {
    "subject_id": 123,
    "risk_level": 1,
    "risk_label": "ABNORMAL",
    "confidence": 0.85
  },
  {
    "subject_id": 124,
    "risk_level": 2,
    "risk_label": "CRITICAL",
    "confidence": 0.92
  }
]
```

---

## Summary Table

| Category | Endpoint | Used | Purpose |
|----------|----------|------|---------|
| **Dashboard** | `/dashboard` | ✅ | General lab reports |
| **Dashboard** | `/ml-dashboard` | ✅ | ML predictions |
| **Report** | `/reports/summary` | ✅ | Lab status counts |
| **Report** | `/reports/by-lab` | ✅ | Lab test stats |
| **Report** | `/reports/by-gender` | ✅ | Gender distribution |
| **Report** | `/reports/unreviewed-critical` | ✅ | Critical alerts list |
| **Report** | `/reports/unreviewed-critical-summary` | ✅ | Critical counts |
| **Report** | `/reports/recent-critical` | ✅ | Recent critical cases |
| **Report** | `/reports/patient-risk` | ✅ | Risk distribution (report) |
| **Report** | `/reports/high-risk-patients` | ✅ | High-risk count (DB) |
| **Chat** | `/chat/patient/{id}` | ❌ | Get patient labs |
| **Chat** | `/chat/patient/{id}/abnormal` | ❌ | Get abnormal labs |
| **Chat** | `/chat/patient/{id}/critical` | ❌ | Get critical labs |
| **Chat** | `/chat/patient/{id}/ai-summary` | ❌ | AI summary (background) |
| **Chat** | `/chat/patient/{id}/ask` | ❌ | Chat with patient data |
| **Predict** | `/predict/patient/{id}/risk` | ❌ | Individual patient risk |
| **Predict** | `/predict/risk-distribution` | ✅ | Risk distribution (ML) |
| **Predict** | `/predict/high-risk` | ✅ | High-risk patients (ML) |
| **Predict** | `/predict/all-patients` | ❌ | All patients risk scores |

**Active Endpoints: 14/19 (74%)**

---

## Usage Statistics

**General Dashboard (/dashboard)**
- Endpoints: 6
- All endpoints: ✅ USED

**ML Dashboard (/ml-dashboard)**
- Endpoints: 6
- All endpoints: ✅ USED

**Chat/Chatbot**
- Endpoints: 5
- Used: ❌ NONE (Reserved for future chatbot UI)

**Available Unused**
- Individual patient risk prediction
- All patients export
- Basic chat endpoints

