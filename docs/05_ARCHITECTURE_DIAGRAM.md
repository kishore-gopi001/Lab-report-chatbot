# Lab Report Interpretation System - Architecture

## System Architecture Diagram

```
╔═════════════════════════════════════════════════════════════════════════════╗
║                         PRESENTATION LAYER                                 ║
║                                                                             ║
║  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────────┐ ║
║  │   Dashboard UI   │  │ ML Dashboard UI  │  │   Chart Visualizations   │ ║
║  │  (HTML/Jinja2)   │  │  (HTML/Jinja2)   │  │      (Chart.js)          │ ║
║  │  • Lab stats     │  │  • Risk scores   │  │  • Distribution charts   │ ║
║  │  • Patient list  │  │  • Predictions   │  │  • Status indicators     │ ║
║  │  • Lab values    │  │  • Alerts        │  │  • Trend analysis        │ ║
║  └────────┬─────────┘  └────────┬─────────┘  └──────────┬────────────────┘ ║
║           │                     │                       │                   ║
║           └─────────────────────┼───────────────────────┘                   ║
║                                 │ HTTP/REST (fetch)                         ║
║                                 ▼                                           ║
╠═════════════════════════════════════════════════════════════════════════════╣
║                         API GATEWAY LAYER                                   ║
║                                                                             ║
║                    ┌─────────────────────────┐                             ║
║                    │  FastAPI Server         │                             ║
║                    │  (app/main.py)          │                             ║
║                    │                         │                             ║
║                    │  19 REST Endpoints:     │                             ║
║                    │  ├─ /dashboard          │                             ║
║                    │  ├─ /ml-dashboard       │                             ║
║                    │  ├─ /reports/* (8)      │                             ║
║                    │  ├─ /chat/* (5)         │                             ║
║                    │  └─ /predict/* (4)      │                             ║
║                    │                         │                             ║
║                    │  Request Routing        │                             ║
║                    │  Validation (Pydantic)  │                             ║
║                    │  Response Serialization │                             ║
║                    └────────────┬────────────┘                             ║
║                                 │                                           ║
╠═════════════════════════════════════════════════════════════════════════════╣
║                       SERVICE ORCHESTRATION LAYER                           ║
║                                                                             ║
║  ┌──────────────────────┐  ┌──────────────────┐  ┌───────────────────┐   ║
║  │  ReportService       │  │  ChatService     │  │  RiskService      │   ║
║  │  (report_service.py) │  │ (chatbot_svc.py) │  │ (risk_service.py) │   ║
║  │                      │  │                  │  │                   │   ║
║  │  • summary()         │  │ • patient_labs() │  │ • risk_score()    │   ║
║  │  • by_lab()          │  │ • ai_summary()   │  │ • high_risk()     │   ║
║  │  • by_gender()       │  │ • answer_q()     │  │ • distribution()  │   ║
║  │  • critical_alerts() │  │ • llm_client     │  │ • export()        │   ║
║  │  • recent_activity() │  │   integration    │  │                   │   ║
║  └────────┬─────────────┘  └────────┬─────────┘  └─────────┬─────────┘   ║
║           │                         │                      │               ║
║           └─────────────────────────┼──────────────────────┘               ║
║                                     │                                      ║
║                                     ▼                                      ║
║                        ┌────────────────────────┐                          ║
║                        │  Data Access Layer    │                          ║
║                        │  (app/db.py)          │                          ║
║                        │                       │                          ║
║                        │  • get_db()           │                          ║
║                        │  • Connection Pool    │                          ║
║                        │  • Query Executor     │                          ║
║                        └────────────┬──────────┘                          ║
║                                     │                                      ║
╠═════════════════════════════════════════════════════════════════════════════╣
║                       PROCESSING & LOGIC LAYERS                             ║
║                                                                             ║
║  ┌──────────────────────────┐         ┌──────────────────────────────┐    ║
║  │  RULES ENGINE            │         │  ML ANALYTICS LAYER          │    ║
║  │  (rules/rules_engine.py) │         │  (ai/risk_model.py)          │    ║
║  │                          │         │                              │    ║
║  │  • Lab thresholds        │         │  Random Forest Classifier    │    ║
║  │  • Severity mapping:     │         │  • Model: 100 trees          │    ║
║  │    NORMAL (0)            │         │  • Max depth: 10             │    ║
║  │    ABNORMAL (1)          │         │  • Class weight: balanced    │    ║
║  │    CRITICAL (2)          │         │                              │    ║
║  │                          │         │  Feature Engineering:        │    ║
║  │  • Canonical mapping     │         │  • Lab test values (pivot)   │    ║
║  │  • Processing pipeline   │         │  • Lab status distribution   │    ║
║  └──────────┬───────────────┘         │  • Patient aggregation       │    ║
║             │                         │                              │    ║
║             │  ┌──────────────────────┤  Training Flow:              │    ║
║             │  │                      │  • prepare_training_data()   │    ║
║             │  │                      │  • train_risk_model()        │    ║
║             │  │                      │  • StandardScaler            │    ║
║             │  │                      │  • Train/test split (80/20)  │    ║
║             │  │                      │                              │    ║
║             │  │                      │  Inference Flow:             │    ║
║             │  │                      │  • predict_patient_risk()    │    ║
║             │  │                      │  • confidence scoring        │    ║
║             │  │                      │  • probability distribution  │    ║
║             │  │                      └──────────────┬───────────────┘    ║
║             │  │                                     │                    ║
║             └──┼─────────────────────────────────────┘                    ║
║                │                                                           ║
║  ┌─────────────▼────────────────┐         ┌────────────────────────────┐ ║
║  │  DATA PARSING & VALIDATION   │         │  AI/RAG LAYER (Future)     │ ║
║  │  (processing/)               │         │  (ai/llm_client.py)        │ ║
║  │                              │         │                            │ ║
║  │  • CSV parser                │         │  • Embedding Service       │ ║
║  │  • Schema validation         │         │  • LLM Integration         │ ║
║  │  • Data enrichment           │         │  • RAG Pipeline            │ ║
║  │  • Canonical mapping         │         │  • Vector Similarity       │ ║
║  │  • Join operations           │         │  • Summary Generation      │ ║
║  │  • Error handling            │         │  (Non-diagnostic only)     │ ║
║  └──────────┬────────────────────┘        └────────────────────────────┘ ║
║             │                                                             ║
╠═════════════════════════════════════════════════════════════════════════════╣
║                         STORAGE & PERSISTENCE LAYER                         ║
║                                                                             ║
║  ┌────────────────────────────────┐  ┌──────────────────────────────┐     ║
║  │   SQLite Database              │  │   Vector Database (Future)   │     ║
║  │   (lab_report_chatbot.db)       │  │   (FAISS/Chroma)            │     ║
║  │                                │  │                              │     ║
║  │   Table: lab_interpretations   │  │   Embeddings:                │     ║
║  │   • subject_id (FK)            │  │   • Lab interpretation texts │     ║
║  │   • test_name (INDEX)          │  │   • Semantic patterns        │     ║
║  │   • value (REAL)               │  │   • Similar case retrieval   │     ║
║  │   • status (CRITICAL/ABNORMAL) │  │   • Context for RAG          │     ║
║  │   • unit                       │  │   • Similarity search        │     ║
║  │   • processed_time             │  │                              │     ║
║  │                                │  │   Vector DB Operations:      │     ║
║  │   Records: 32,378              │  │   • Index building           │     ║
║  │   Patients: 100+               │  │   • Query by similarity      │     ║
║  │   Indexed: (subject_id,        │  │   • KNN retrieval            │     ║
║  │             test_name, status) │  │                              │     ║
║  └────────────────────────────────┘  └──────────────────────────────┘     ║
║                                                                             ║
║  ┌────────────────────────────────┐  ┌──────────────────────────────┐     ║
║  │   ML Models (Serialized)        │  │   Feature Store              │     ║
║  │   (ai/models/)                  │  │   (Computed Features)        │     ║
║  │                                │  │                              │     ║
║  │   • risk_model.pkl             │  │   Cache:                     │     ║
║  │     RandomForest (100 trees)    │  │   • Aggregated lab status    │     ║
║  │   • scaler.pkl                 │  │   • Severity ratios          │     ║
║  │     StandardScaler              │  │   • Patient risk scores      │     ║
║  │   • metadata                   │  │   • Recent computations      │     ║
║  │                                │  │                              │     ║
║  │   Accuracy Metrics:            │  │   TTL: 24 hours              │     ║
║  │   • Train: 100%                │  │   Refresh: On data update    │     ║
║  │   • Test: ~70%                 │  │                              │     ║
║  └────────────────────────────────┘  └──────────────────────────────┘     ║
║                                                                             ║
╚═════════════════════════════════════════════════════════════════════════════╝
```

## Data Flow Diagram

```
Input Data Source
    │
    ├─ CSV Files (labevents, patients, diagnoses)
    ├─ Parsed Lab Reports (if available)
    │
    ▼
┌─────────────────────────────────────┐
│  Data Ingestion Pipeline            │
│  (scripts/persist_results.py)        │
│                                     │
│  1. Load & Parse CSV                │
│  2. Validate Schema                 │
│  3. Join with metadata              │
│  4. Canonical mapping               │
│  5. Rules evaluation                │
│  6. Severity classification         │
│  7. Store in SQLite                 │
└────────────────┬────────────────────┘
                 │
                 ▼
         ┌──────────────────┐
         │  SQLite Database │
         │ (32,378 records) │
         └────────┬─────────┘
                  │
         ┌────────┴─────────┐
         │                  │
         ▼                  ▼
    ┌──────────────┐   ┌────────────────────┐
    │ Dashboard    │   │ ML Training        │
    │ Analytics    │   │                    │
    │              │   │ • Feature engineering
    │ ReportService│   │ • Data preparation
    │ • Summary    │   │ • Train/test split
    │ • By Lab     │   │ • Random Forest
    │ • By Gender  │   │ • Scaling
    │              │   │ • Model serialization
    └──────────────┘   └─────────┬──────────┘
         │                       │
         │                       ▼
         │              ┌──────────────────┐
         │              │  ML Models (PKL) │
         │              │ • risk_model.pkl │
         │              │ • scaler.pkl     │
         │              └─────────┬────────┘
         │                        │
         └────────────┬───────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │ Inference & Scoring    │
         │                        │
         │ RiskService:           │
         │ • Risk scoring         │
         │ • High-risk filtering  │
         │ • Distribution calc    │
         └────────────┬───────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │ API Responses (JSON)   │
         └────────────┬───────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │ Frontend Rendering     │
         │ • Charts               │
         │ • Tables               │
         │ • KPI Cards            │
         │ • Alerts               │
         └────────────────────────┘
```

## Key Components

### Frontend Layer
- **dashboard.html** - Lab reports UI (Jinja2 template)
- **ml-dashboard.html** - Risk predictions UI (Jinja2 template)  
- **dashboard.js** - Lab dashboard logic (6 functions, parallel fetch)
- **ml-dashboard.js** - ML dashboard logic (6 functions, pagination)
- **style.css** - Responsive styling

### API Gateway Layer
- **app/main.py** - FastAPI server with 19 endpoints
- Request validation (Pydantic models)
- Response serialization (JSON)
- CORS & security headers

### Service Layer
- **ReportService** - Lab statistics & aggregations
- **ChatService** - AI summaries & Q&A (LLM integration)
- **RiskService** - ML predictions & scoring

### Processing Layers
- **Rules Engine** - Severity classification, threshold mapping
- **ML Analytics** - Random Forest risk prediction
- **Data Pipeline** - Parsing, validation, enrichment
- **RAG/AI Layer** - LLM integration (future), embeddings

### Storage Layer
- **SQLite** - Primary data store (lab_interpretations)
- **Vector DB** - Embeddings & similarity search (future)
- **ML Models** - Serialized RandomForest + StandardScaler
- **Feature Cache** - Precomputed aggregations
