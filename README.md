# DRISHTI AI — Intelligent MLOps & AIOps Observability Platform

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.4%2B-F7931E.svg)](https://scikit-learn.org/)
[![MLflow](https://img.shields.io/badge/MLflow-2.10%2B-0194E2.svg)](https://mlflow.org/)
[![Prometheus Ready](https://img.shields.io/badge/Prometheus-v0.0.4%20Metrics-E6522C.svg)](https://prometheus.io/)

> **"An intelligent observability platform for monitoring machine learning applications through unified telemetry, anomaly detection, and incident management."**

---

## Table of Contents

- [1. Overview & Problem Statement](#1-overview--problem-statement)
- [2. Why DRISHTI AI?](#2-why-drishti-ai)
- [3. Key Features](#3-key-features)
- [4. Platform Architecture & Data Flow](#4-platform-architecture--data-flow)
- [5. Technology Stack](#5-technology-stack)
- [6. Installation & Local Setup](#6-installation--local-setup)
- [7. Environment Configuration](#7-environment-configuration)
- [8. Getting Started: Register Your First ML Project](#8-getting-started-register-your-first-ml-project)
- [9. Integrating an External ML Application](#9-integrating-an-external-ml-application)
- [10. Telemetry Schema Reference](#10-telemetry-schema-reference)
- [11. Supported ML Application Types](#11-supported-ml-application-types)
- [12. Understanding the Dashboard](#12-understanding-the-dashboard)
- [13. Comprehensive API Reference](#13-comprehensive-api-reference)
- [14. Operational Anomaly Detection](#14-operational-anomaly-detection)
- [15. Incident Management & Automated Responses](#15-incident-management--automated-responses)
- [16. Included Example Applications](#16-included-example-applications)
- [17. Troubleshooting & Diagnostics](#17-troubleshooting--diagnostics)
- [18. Security & Data Isolation](#18-security--data-isolation)
- [19. Project Roadmap & Implementation Status](#19-project-roadmap--implementation-status)
- [20. Contributing](#20-contributing)
- [21. License & Acknowledgements](#21-license--acknowledgements)

---

## 1. Overview & Problem Statement

**DRISHTI AI** (from the Sanskrit word *दृष्टि*, meaning *Vision* or *Insight*) is a developer-focused, local-first observability and incident response platform designed to monitor independently developed machine learning applications.

### The Fundamental Problem in Machine Learning Operations
Traditional software systems typically fail fast and loud: an unhandled exception returns an HTTP `500 Internal Server Error`, a database process terminates, or a container crashes.

**Machine Learning applications fail silently.** When an ML model degrades in production, it does not throw an exception. Instead, it continues executing successfully while producing degraded, misleading, or outright incorrect predictions. Furthermore, operational failures—such as feature store timeouts, latency spikes, memory bloat, or corrupted input schemas—often go unnoticed until business KPIs collapse or users report failures.

### The Architectural Role of DRISHTI AI

> [!IMPORTANT]
> **DRISHTI AI does not replace your model.**  
> Your external application continues making its own business predictions using its own framework (PyTorch, TensorFlow, Scikit-learn, XGBoost, or external LLM APIs). DRISHTI AI runs alongside your services as a dedicated telemetry ingestion, operational anomaly detection, and incident remediation engine.

---

## 2. Why DRISHTI AI?

Modern ML engineering teams face critical operational gaps:

1. **Fragmented Monitoring Across Disparate Models:** Teams running multiple models (e.g. fraud detection, house price valuation, customer churn) lack a single operational interface to monitor all applications in one place.
2. **Hidden Inference Latency Degradation:** Slow downstream dependencies (feature stores, embedding lookups, vector databases) gradually degrade inference times without triggering standard uptime health checks.
3. **Log Noise & Alert Fatigue:** When a dependent service hiccups, microservices emit thousands of duplicate error logs, overwhelming on-call engineers.
4. **Lack of Ground-Truth Accuracy Tracking:** Production models often drift from training distributions. Teams need automated Mean Absolute Error (MAE) and Root Mean Squared Error (RMSE) tracking when verified ground-truth labels arrive post-inference.
5. **Infrastructure Burden:** Setting up dedicated clusters of Elasticsearch, Prometheus, Grafana, and PagerDuty for early-stage or internal ML projects requires significant DevOps overhead.

**DRISHTI AI solves these challenges** by providing a lightweight, zero-dependency, self-hosted platform that provides project isolation, standardized telemetry ingestion, automated operational anomaly detection, incident deduplication, and safe automated remediation playbooks right out of the box.

---

## 3. Key Features

- **Multi-Project Management & Strict Isolation:** Register multiple independent ML applications. Each project receives a cryptographically hashed API key, and all telemetry is stored in project-isolated partitions (`data/telemetry/{project_id}.jsonl`).
- **Standardized Telemetry Ingestion:** Submit single or batched inferences, latencies, confidence scores, ground-truth outcomes, and resource metrics via high-throughput REST endpoints.
- **16-Dimensional Adaptive Log Normalization:** Ingests unstructured logs and raw error events, automatically mapping them into a unified 16-dimensional numerical feature space.
- **Unsupervised Operational Anomaly Detection:** Employs an active **Loglizer IsolationForest** model (100 decision trees) to detect anomalous operational patterns, unexpected severity spikes, and severe latency outliers in real time.
- **Intelligent Incident Queue & Deduplication:** Generates project-scoped incidents with MD5 fingerprinting, preventing alert spam by aggregating duplicate occurrences and preserving complete lifecycle audit trails (`OPEN` \(\rightarrow\) `INVESTIGATING` \(\rightarrow\) `MITIGATING` \(\rightarrow\) `RESOLVED` \(\rightarrow\) `CLOSED`).
- **Safe Automated Remediation Engine:** Automatically triggers non-destructive, auditable remediation playbooks (such as simulated connection pool recycling or cache clearing) to demonstrate automated system healing.
- **Ground-Truth Drift & Accuracy Engine:** Computes real-time MAE, RMSE, sample sizes, and health classifications when actual target labels are reported post-prediction.
- **MLOps Lifecycle & Experiment Tracking:** Integrated MLflow tracking with an SQLite backend, tracking training runs, hyperparameters, metrics (RMSE, \(R^2\)), and model registry stage promotions (`Staging` \(\rightarrow\) `Production`).
- **Standards-Compliant Prometheus Exposition:** Real-time `/metrics` endpoint adhering to Prometheus text exposition format (version 0.0.4), tracking log counts, anomaly counts, prediction latencies, and incident lifecycles.
- **Unified Reactive Dark-Themed Dashboard:** A zero-build, single-page React 18 and Tailwind CSS application served directly by FastAPI, featuring an active project selector, live telemetry stream, incident triage, and health diagnostics.
- **Lightweight Python Client SDK (`drishti_sdk`):** A zero-dependency client with non-blocking background thread buffering, ensuring telemetry ingestion never impedes host model execution.

---

## 4. Platform Architecture & Data Flow

```mermaid
flowchart TD
    subgraph External ["External ML Ecosystem"]
        direction TB
        M1["House Price Service\n(Regression / Scikit-Learn)"]
        M2["Fraud Detection Service\n(Binary Classifier / LightGBM)"]
        M3["Custom External App\n(NLP / PyTorch / LLM)"]
        SDK["drishti_sdk / REST Client\n(Non-blocking Thread Buffer)"]
        M1 --> SDK
        M2 --> SDK
        M3 --> SDK
    end

    subgraph Gateway ["DRISHTI AI Ingestion Gateway (FastAPI)"]
        API["POST /telemetry/ingest\nPOST /telemetry/batch"]
        AUTH{"API Key Auth\n(SHA-256 Verification)"}
        SDK -->|HTTP + X-API-Key| API
        API --> AUTH
    end

    subgraph Core ["Telemetry & Anomaly Processing"]
        AUTH -->|Authorized| TELEM["Telemetry Engine\n(integration/telemetry_service.py)"]
        TELEM -->|Partitioned Storage| STORE[("data/telemetry/{project_id}.jsonl")]
        TELEM --> NORM["16-Feature Vector Normalizer\n(Severity, Event Category, Timeout Flags)"]
        NORM --> DETECT["Loglizer IsolationForest\n(models/log_anomaly_detector.joblib)"]
    end

    subgraph AIOps ["AIOps Incident & Remediation Engine"]
        DETECT -->|Score = -1 (Anomaly)| ALERTS["Incident Manager\n(integration/alert_manager.py)"]
        ALERTS --> DEDUP["MD5 Fingerprint Deduplication\n(alerts/incidents.json)"]
        DEDUP --> PLAY["Automated Response Engine\n(integration/response_engine.py)"]
        PLAY --> REM_AUDIT[("alerts/remediation_audit.json")]
        ALERTS --> HIST[("alerts/incident_history.json")]
    end

    subgraph MLOps ["Integrated MLOps Model Lifecycle"]
        DATA["NYC Taxi Dataset"] --> ML_TRAIN["Training Pipeline"]
        ML_TRAIN --> MLF[("mlflow.db SQLite")]
        MLF --> REG["Model Registry & Stage Promotion"]
        REG --> SERVE["Serving Endpoint (POST /mlops/predict)"]
    end

    subgraph Observability ["Observability Interfaces"]
        PROM["Prometheus Exporter\n(GET /metrics)"]
        DASH["React 18 Dark Dashboard\n(GET /dashboard)"]
        TELEM -.-> PROM
        ALERTS -.-> PROM
        TELEM -.-> DASH
        ALERTS -.-> DASH
    end
```

### Architectural Distinction Matrix

| Component | Responsibility | Technology | Where It Runs |
| :--- | :--- | :--- | :--- |
| **Business Prediction Model** | Evaluates real-world inputs (e.g. house valuation, credit card fraud risk) | Host app stack (PyTorch, Scikit-learn, etc.) | External application process |
| **Telemetry Ingestion Gateway** | Ingests inference metrics, latencies, errors, and ground truth | FastAPI, Pydantic, HTTP REST | DRISHTI Core (`integration/api.py`) |
| **Operational Anomaly Detector** | Detects infrastructure and pipeline anomalies from log features | Loglizer IsolationForest (Unsupervised) | DRISHTI Core (`models/log_anomaly_detector.joblib`) |
| **Incident & Remediation Engine** | Deduplicates operational alerts and runs automated playbooks | Local JSON Store / Keep Adapter | DRISHTI Core (`integration/alert_manager.py`) |
| **Experiment Tracking Platform** | Tracks training runs, metrics, and model version promotion | MLflow with SQLite backing | DRISHTI Core (`integration/mlops_service.py`) |

---

## 5. Technology Stack

### Backend & Core Services
- **Python 3.10 – 3.13**: Primary runtime environment.
- **FastAPI**: Asynchronous REST API framework providing strict Pydantic payload validation and automatic OpenAPI docs.
- **Uvicorn**: High-throughput ASGI production server.
- **Joblib**: Fast disk serialization for machine learning artifacts.

### Machine Learning & Anomaly Detection
- **Loglizer (`log-anomaly/`)**: Toolkit developed by CUHK AI researchers, utilizing unsupervised `IsolationForest` on log event matrices.
- **Scikit-Learn**: Powering the operational anomaly detector ensemble (100 estimators, 0.20 contamination threshold) and the demonstration regression models.
- **NumPy & Pandas**: Vector math, numerical feature normalizations, and tabular data manipulation.

### MLOps & Experiment Tracking
- **MLflow (`mlops-platform/ml-flow`)**: Experiment tracking, hyperparameter logging, metric curves (RMSE, \(R^2\)), artifact versioning, and model registry stage promotions (`Staging` \(\rightarrow\) `Production`).
- **SQLite (`mlflow.db`)**: Local embedded relational database storing all MLflow experiment metadata.

### Monitoring, Observability & UI
- **Prometheus Exporter**: Native metrics exposition at `/metrics` implementing the official Prometheus text format v0.0.4.
- **React 18 & Tailwind CSS**: Self-contained, responsive, dark-themed Single Page Application served directly by FastAPI without external Node.js build requirements.
- **Keep Integration Adapter (`incident-management/`)**: Adapter testing connectivity to Keep AIOps orchestrators, with automatic fallback to DRISHTI's local zero-dependency incident management engine.

---

## 6. Installation & Local Setup

### Prerequisites
- **Python**: Version `3.10`, `3.11`, `3.12`, or `3.13`.
- **Git**: Installed and available in your system path.
- **Operating System**: Windows 10/11, macOS, or Linux (Ubuntu 20.04+).

---

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-username/DRISHTI-AI.git
cd DRISHTI-AI
```

---

### Step 2: Create a Python Virtual Environment

#### On Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

#### On Linux / macOS (bash/zsh):
```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### Step 3: Install Core Dependencies
Install the required Python packages into your active virtual environment:
```bash
pip install -r requirements.txt
```

To enable the lightweight Python SDK globally within your environment:
```bash
pip install -e drishti_sdk
```
*(On Windows systems lacking `setuptools`, DRISHTI automatically resolves local imports via `drishti_sdk.pth` or project root path injection).*

---

### Step 4: Configure Environment Variables
Copy the template configuration file to `.env`:

#### On Windows (PowerShell):
```powershell
Copy-Item .env.example .env
```

#### On Linux / macOS:
```bash
cp .env.example .env
```

---

### Step 5: Verify Model Artifacts and Demo Data
Ensure the operational anomaly detector artifact exists at `models/log_anomaly_detector.joblib`. If you need to re-train the anomaly detector on the baseline log dataset:
```bash
python integration/train_anomaly_detector.py
```

To seed initial sample projects, telemetry, and error incidents:
```bash
python scripts/seed_demo_data.py
```

---

### Step 6: Start the DRISHTI AI Platform
Start the FastAPI backend with Uvicorn:

#### On Windows (PowerShell):
```powershell
.\.venv\Scripts\uvicorn.exe integration.api:app --host 127.0.0.1 --port 8000 --reload
```

#### On Linux / macOS:
```bash
uvicorn integration.api:app --host 127.0.0.1 --port 8000 --reload
```

---

### Step 7: Access the Platform

Once started, access the platform endpoints in your browser or HTTP client:

- **Observability Dashboard:** [http://127.0.0.1:8000/dashboard](http://127.0.0.1:8000/dashboard)
- **Interactive Swagger API Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Alternative ReDoc Docs:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Health Check Endpoint:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- **Prometheus Metrics Feed:** [http://127.0.0.1:8000/metrics](http://127.0.0.1:8000/metrics)

---

### Step 8: Run the Automated Verification Suite
To confirm that all platform subsystems (projects, telemetry, incidents, metrics, SDK, and APIs) are operating properly:
```bash
python scripts/run_all_tests.py
```

---

## 7. Environment Configuration

All configuration is managed through environment variables defined in `.env`:

| Variable | Description | Required | Default / Example Value |
| :--- | :--- | :---: | :--- |
| `DRISHTI_HOST` | Network interface binding for FastAPI | No | `127.0.0.1` |
| `DRISHTI_PORT` | Port for the backend API and dashboard | No | `8000` |
| `DRISHTI_LOG_LEVEL` | Logging verbosity (`debug`, `info`, `warning`, `error`) | No | `info` |
| `DRISHTI_MASTER_API_KEY` | Master key allowing administrative telemetry ingestion | No | `dr_live_master_override_key` |
| `MLFLOW_TRACKING_URI` | SQLite database URI for MLflow experiment storage | No | `sqlite:///mlflow.db` |
| `MODEL_NAME` | Identifier for the MLOps demonstration model | No | `taxi_fare_predictor` |
| `RETRAIN_RMSE_THRESHOLD` | Threshold triggering retraining warnings in MLOps demo | No | `0.05` |
| `KEEP_API_URL` | Endpoint for external Keep AIOps orchestrator (if deployed) | No | `http://localhost:8080` |
| `KEEP_API_KEY` | API token for Keep backend authentication | No | *(Empty string)* |

> [!WARNING]
> Never commit `.env` or real API keys to version control. Keep `.env` listed in `.gitignore`.

---

## 8. Getting Started: Register Your First ML Project

Before an external ML application can stream telemetry, it must be registered to obtain a secure API token.

### Registration Endpoint: `POST /projects/register`

#### Request Payload
```json
{
  "project_id": "customer-churn-model",
  "name": "Customer Churn Prediction Engine",
  "description": "Predicts subscription churn probability from user behavioral events.",
  "model_type": "binary_classification",
  "framework": "xgboost",
  "schema_mapping": {
    "latency_field": "latency_ms",
    "prediction_field": "churn_probability",
    "target_field": "actual_churn_status"
  }
}
```

#### cURL Registration Example
```bash
curl -X POST "http://127.0.0.1:8000/projects/register" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "customer-churn-model",
    "name": "Customer Churn Prediction Engine",
    "model_type": "binary_classification",
    "framework": "xgboost"
  }'
```

#### Successful Response (`201 Created`)
```json
{
  "status": "success",
  "project": {
    "project_id": "customer-churn-model",
    "name": "Customer Churn Prediction Engine",
    "description": "Predicts subscription churn probability from user behavioral events.",
    "api_key_prefix": "dr_live_9a4f",
    "api_key_masked": "dr_live_9a4f...",
    "created_at": "2026-11-20T00:30:00+05:30",
    "status": "ACTIVE",
    "model_type": "binary_classification",
    "framework": "xgboost",
    "schema_mapping": {}
  },
  "api_key": "dr_live_9a4f781c9e83a002bc45d0124fe7891a23c4d56e",
  "note": "Save this API key securely. It will not be shown again."
}
```

### Security & Storage Rules
1. **One-Time Key Return:** The full API key is returned **only once** upon registration.
2. **Cryptographic Hashing:** The DRISHTI backend hashes the key with `SHA-256` before storing it in `data/projects.json`.
3. **Storage:** Store the key in your external application's environment variable (e.g. `DRISHTI_API_KEY`).

---

## 9. Integrating an External ML Application

Integrating an existing ML model into DRISHTI AI requires no changes to your model architecture. Your model predicts normally, and you submit an asynchronous telemetry payload.

### Method 1: Using the Python SDK (`drishti_sdk`)

The `drishti_sdk` provides a thread-safe, non-blocking client that buffers events in the background:

```python
import time
from drishti_sdk import DrishtiClient

# 1. Initialize the client
client = DrishtiClient(
    project_id="customer-churn-model",
    api_key="dr_live_9a4f781c9e83a002bc45d0124fe7891a23c4d56e",
    endpoint="http://127.0.0.1:8000",
    batch_size=5,          # Flushes every 5 events or 3 seconds
    silent_errors=True     # Never crashes your host application
)

# 2. Your model performs inference normally
features = {"monthly_charges": 89.50, "tenure_months": 3, "contract": "month-to-month"}
start_time = time.perf_counter()
churn_prediction = 1                       # 1 = Will Churn, 0 = Retained
confidence_score = 0.88                    # Model probability
inference_latency = (time.perf_counter() - start_time) * 1000

# 3. Log the prediction event
client.log_prediction(
    model_name="churn-xgboost-prod",
    model_version="1.4.0",
    inputs=features,
    prediction=churn_prediction,
    confidence=confidence_score,
    latency_ms=inference_latency,
    custom_tags={"user_id": "usr_99182"}
)

# 4. If an operational exception occurs in your service:
try:
    # Simulating a cache or feature store read
    raise TimeoutError("FeatureStore cluster timeout on Redis shard 03")
except Exception as exc:
    client.log_error(
        error_type="FeatureStoreTimeoutError",
        message=str(exc),
        severity="ERROR",
        model_name="churn-xgboost-prod"
    )

# 5. When true ground-truth outcome is verified later:
client.log_ground_truth(
    actual_value=1,
    prediction=churn_prediction,
    model_name="churn-xgboost-prod"
)

# 6. Flush on process termination
client.flush()
client.close()
```

---

### Method 2: Direct HTTP REST Integration (Universal Language Support)

Applications written in Node.js, Go, Java, C#, Ruby, or cURL can submit telemetry directly via standard HTTP requests without installing any SDK.

#### Python `requests` Example:
```python
import time
import requests

API_ENDPOINT = "http://127.0.0.1:8000/telemetry/ingest"
API_KEY = "dr_live_9a4f781c9e83a002bc45d0124fe7891a23c4d56e"

# Execute inference
start_time = time.perf_counter()
predicted_label = 0
latency_ms = (time.perf_counter() - start_time) * 1000

# Construct telemetry payload
payload = {
    "project_id": "customer-churn-model",
    "record": {
        "event_type": "prediction",
        "model_name": "churn-xgboost-prod",
        "model_version": "1.4.0",
        "prediction": predicted_label,
        "confidence": 0.94,
        "latency_ms": latency_ms,
        "ground_truth": 0,
        "inputs": {"monthly_charges": 45.00, "tenure_months": 24},
        "log_message": "Churn inference executed successfully",
        "severity": "INFO"
    }
}

# Submit telemetry with API key header
response = requests.post(
    API_ENDPOINT,
    json=payload,
    headers={"X-API-Key": API_KEY},
    timeout=2.0
)
print("Telemetry status:", response.json().get("status"))
```

---

## 10. Telemetry Schema Reference

The `/telemetry/ingest` and `/telemetry/batch` endpoints accept structured JSON payloads matching the schema below:

| Field Name | Data Type | Required? | Description | Example Value |
| :--- | :--- | :---: | :--- | :--- |
| `project_id` | `string` | **Yes** | Identifier of the registered project | `"fraud-detection-engine"` |
| `record` | `object` | **Yes** | Object containing the telemetry attributes | *See sub-fields below* |
| `record.event_type` | `string` | No | Category (`prediction`, `error`, `ground_truth`, `metrics`) | `"prediction"` |
| `record.timestamp` | `string` | No | ISO-8601 timestamp (auto-generated if omitted) | `"2026-11-20T00:35:12+05:30"` |
| `record.model_name` | `string` | No | Name of the business model emitting telemetry | `"fraud-risk-lightgbm"` |
| `record.model_version` | `string` | No | Semantic version of the running model | `"2.1.0"` |
| `record.prediction` | `any` | No | Output produced by the model (int, float, string) | `1` or `685000.0` |
| `record.confidence` | `float` | No | Confidence score or probability \([0.0, 1.0]\) | `0.965` |
| `record.ground_truth` | `any` | No | Actual outcome label for accuracy verification | `1` or `690000.0` |
| `record.latency_ms` | `float` | No | Inference duration in milliseconds | `18.42` |
| `record.inputs` | `object` | No | Input feature map passed to the model | `{"sqft": 2400, "beds": 4}` |
| `record.error_type` | `string` | No | Exception class or error classification | `"RedisConnectionTimeout"` |
| `record.error_message` | `string` | No | Human-readable error description | `"Connection timed out"` |
| `record.severity` | `string` | No | Event severity: `INFO`, `WARNING`, `ERROR`, `CRITICAL` | `"ERROR"` |
| `record.resource_metrics` | `object` | No | System health metrics (`cpu_percent`, `memory_mb`) | `{"cpu_percent": 42.5}` |
| `record.custom_tags` | `object` | No | Arbitrary key-value metadata for filtering | `{"region": "us-east-1"}` |

> [!NOTE]
> **Ground-Truth Requirements for Drift Analysis:**  
> DRISHTI AI cannot fabricate accuracy calculations without factual labels. Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), and drift detection are computed **only** when `ground_truth` is reported alongside or following predictions.

---

## 11. Supported ML Application Types

DRISHTI AI's universal telemetry contract accommodates diverse machine learning categories:

### 1. Binary & Multiclass Classification (e.g. Fraud Detection, Sepsis Prediction)
```json
{
  "prediction": 1,
  "confidence": 0.985,
  "ground_truth": 1,
  "inputs": {"tx_amount": 2500.00, "foreign_tx": true}
}
```

### 2. Numerical Regression (e.g. Real Estate Valuation, Trip Fare Estimation)
```json
{
  "prediction": 688500.00,
  "confidence": 0.94,
  "ground_truth": 690000.00,
  "inputs": {"sqft": 2400, "bedrooms": 4, "bathrooms": 3}
}
```

### 3. Natural Language Processing & LLMs (e.g. Sentiment, Question Answering)
```json
{
  "prediction": "POSITIVE",
  "confidence": 0.92,
  "latency_ms": 340.5,
  "inputs": {"prompt_tokens": 128, "completion_tokens": 42}
}
```

### 4. Computer Vision (e.g. Object Detection, Defect Classification)
```json
{
  "prediction": "DEFECT_SURFACE_CRACK",
  "confidence": 0.89,
  "latency_ms": 48.2,
  "custom_tags": {"camera_id": "cam_line_04", "resolution": "1920x1080"}
}
```

---

## 12. Understanding the Dashboard

The DRISHTI AI dashboard is available at **`http://127.0.0.1:8000/dashboard`**. It is an interactive, dark-themed Single Page Application built with React 18 and Tailwind CSS:

```
+----------------------------------------------------------------------------------------+
|  🔭 DRISHTI AI                                         [Active Workspace: Project ▾]   |
+-------------------+--------------------------------------------------------------------+
|  📊 Overview      |  KPIs: Ingested: 1,420 | Anomalies: 12 | Latency: 18ms | Open: 1    |
|  📡 Telemetry     |  +--------------------------------+ +----------------------------+ |
|  📑 Logs          |  | Real-Time Quick Diagnostic     | | Project Metadata & Drift   | |
|  🔍 Anomaly Brain |  | Latency: 18.5ms [NORMAL]       | | Samples: 7  MAE: $3,700    | |
|  🚨 Incidents     |  +--------------------------------+ +----------------------------+ |
|  ⚡ Responses     |--------------------------------------------------------------------|
|  🧠 MLOps Runs    |  Recent Audit Timeline:                                            |
|  💚 System Health |  - [STATUS] Incident #1a14cdf6 transitioned to MITIGATING          |
+-------------------+--------------------------------------------------------------------+
```

### Dashboard Tabs & Sections:
1. **Active Workspace Selector (Sidebar Dropdown):** Select between `🌐 All Projects (Platform Wide)` and specific projects (e.g. `📁 House Price Valuation Engine` or `📁 Credit Card Fraud Detection Engine`). All dashboard views filter immediately to the chosen workspace.
2. **Overview Dashboard (Tab 1):** Real-time KPI summary cards (Total Requests, Anomalies Flagged, Mean Latency, Active Incidents), interactive diagnostic tester, and the **Project Metadata & Model Drift Card** displaying live MAE and RMSE metrics.
3. **Project Telemetry (Tab 2):** Live tabular view of all ingested telemetry events showing timestamps, model versions, prediction values, ground-truth labels, latencies, and Loglizer evaluation tags.
4. **Log Monitoring (Tab 3):** Inspects raw log messages, component categories, and historical log records.
5. **Anomaly Detection (Tab 4):** Inspects the Loglizer IsolationForest model parameters (100 estimators, 0.20 contamination) and details the 16-dimensional feature extraction vector.
6. **Incident Management (Tab 5):** Triage project-scoped operational incidents, review occurrence counts, inspect root causes, and transition incident statuses with the **Resolve** action button.
7. **Automated Responses (Tab 6):** Audit log of all automated remediation playbooks executed by the system.
8. **MLOps & Experiments (Tab 7):** Displays MLflow runs, hyperparameter logs, evaluation metrics, and stage promotion controls (`Staging` \(\rightarrow\) `Production`).
9. **System Health (Tab 8):** Subsystem health statuses (API, Anomaly Detector, Incident Manager, Metrics Engine) and Prometheus scrapable statistics.

---

## 13. Comprehensive API Reference

### System & Health Endpoints
- `GET /` — Returns platform root information, active version, and service descriptors.
- `GET /health` — Verifies operational state of all internal subsystems and model artifact loads.
- `GET /dashboard` — Serves the self-contained React 18 / Tailwind CSS dashboard HTML.
- `GET /metrics` — Exposes Prometheus metrics in standard text format (`version=0.0.4`).
- `GET /system/stats` — Provides JSON statistics on total projects, telemetry records, and open incidents.

### Project Management Endpoints
- `POST /projects/register` — Registers a new ML project and generates an API key. (Auth: Public).
- `GET /projects` — Lists all registered projects with masked API keys. (Auth: Public).
- `GET /projects/{project_id}` — Retrieves project metadata, model configurations, and drift statistics.

### Telemetry Ingestion Endpoints
- `POST /telemetry/ingest` — Ingests a single telemetry record and performs real-time anomaly detection. (Auth: `X-API-Key` or `Authorization: Bearer <key>`).
- `POST /telemetry/batch` — Ingests an array of telemetry records in one request. (Auth: `X-API-Key`).
- `GET /telemetry/{project_id}?limit=100` — Retrieves isolated historical telemetry for a project.
- `GET /telemetry/{project_id}/drift` — Computes sample size, MAE, RMSE, and drift health from verified ground truth.

### Operational Anomaly Detection Endpoints
- `POST /predict` — Evaluates a raw log message or 16-feature vector against the IsolationForest detector.
- `POST /logs/batch-predict` — Evaluates multiple log records in batch.

### Incident Management & Remediation Endpoints
- `GET /alerts?project_id={id}&status={status}` — Retrieves filtered incident records.
- `PATCH /alerts/{alert_id}/resolve` — Resolves an incident with operator notes.
- `PATCH /alerts/{alert_id}/status` — Transitions incident state (`OPEN`, `INVESTIGATING`, `MITIGATING`, `RESOLVED`, `CLOSED`).
- `GET /incidents/stats` — Summary counts of incidents grouped by status.
- `GET /incidents/history` — Audit log of all historical state transitions.
- `GET /responses` — Audit log of executed automated remediation actions.
- `POST /responses/trigger/{incident_id}` — Manually executes a remediation playbook.

### MLOps Lifecycle Endpoints
- `GET /mlops/runs` — Lists tracked runs from the local MLflow SQLite store.
- `GET /mlops/model-status` — Shows current production model version and metrics.
- `POST /mlops/train` — Triggers demonstration model training with MLflow parameter tracking.
- `POST /mlops/promote` — Promotes candidate model run to `Production` stage.
- `POST /mlops/predict` — Executes inference against the served demonstration model.

---

## 14. Operational Anomaly Detection

DRISHTI AI uses **Loglizer IsolationForest** for operational log anomaly detection:

### The 16-Dimensional Feature Vector
Incoming logs and telemetry events are mapped into a standardized 16-dimensional numerical vector:
1. `severity_INFO`: Binary flag (1 if event severity is INFO).
2. `severity_WARNING`: Binary flag (1 if WARNING).
3. `severity_ERROR`: Binary flag (1 if ERROR).
4. `severity_CRITICAL`: Binary flag (1 if CRITICAL).
5. `event_database`: Binary flag (Database-related event).
6. `event_prediction`: Binary flag (Model inference event).
7. `event_memory`: Binary flag (Memory consumption event).
8. `event_inference`: Binary flag (Model computation event).
9. `event_latency`: Binary flag (Latency-related event).
10. `event_authentication`: Binary flag (Authentication event).
11. `event_model`: Binary flag (Model lifecycle event).
12. `event_api`: Binary flag (API gateway event).
13. `event_other`: Binary flag (Unclassified category).
14. `is_timeout`: Binary flag (1 if latency > 1,000ms or log indicates timeout).
15. `is_failed`: Binary flag (1 if error keywords or failure flags are detected).
16. `is_high_usage`: Binary flag (1 if CPU > 85%, memory > 1,500MB, or resource spikes).

### How IsolationForest Works
Isolation Forest builds an ensemble of 100 randomized decision trees. Normal events require deep recursive tree splits to isolate, whereas operational anomalies (such as timeouts, error cascades, or severe resource spikes) isolate near the root of the trees in very few splits.

- **Normal Output:** Evaluates to `1` (Normal).
- **Anomalous Output:** Evaluates to `-1` (Anomaly), automatically creating an incident and triggering remediation.

> [!IMPORTANT]
> The anomaly detector inspects **operational infrastructure and log behavior**, not business predictions. It does not predict real estate prices, fraud probability, or customer churn.

---

## 15. Incident Management & Automated Responses

### Incident Deduplication
When an infrastructure failure occurs, services often generate thousands of duplicate errors. DRISHTI AI prevents alert fatigue through **MD5 fingerprinting**:

$$\text{Fingerprint} = \text{MD5}(\text{project\_id} + \text{severity} + \text{category} + \text{error\_type})$$

If an alert matching an active fingerprint arrives, DRISHTI AI increments the existing incident's `occurrences` count and updates its timestamp, rather than creating duplicate alerts.

### Incident Lifecycle
```
[OPEN] ──> [INVESTIGATING] ──> [MITIGATING] ──> [RESOLVED] ──> [CLOSED]
```

### Automated Remediation Playbooks
When an operational anomaly or error is detected, DRISHTI triggers an automated remediation playbook:

| Anomaly Pattern | Automated Playbook | Simulated Action Taken |
| :--- | :--- | :--- |
| **Database Timeout** | `database_timeout` | Recycles connection pool, purges idle connections, switches read-replica |
| **High Memory Spike** | `high_memory_usage` | Executes garbage collection, clears model inference cache, restarts worker |
| **API Latency Spike** | `api_latency_spike` | Enables rate limiting, activates fallback circuit breaker, scales concurrency |
| **Model Error Spike** | `model_inference_failure`| Reloads model weights, runs self-test diagnostics, falls back to baseline |

> [!CAUTION]
> **Simulated Remediation Notice:**  
> Playbook actions are executed safely as simulated operations (`is_simulated: true`) recorded in `alerts/remediation_audit.json`. They do not modify host operating system services or restart physical machines without explicit authorization.

---

## 16. Included Example Applications

DRISHTI AI includes two functional external ML applications in the `examples/` directory to demonstrate real-world integration:

### 1. House Price Valuation Engine (`examples/house_price_service.py`)
- **Category:** Numerical Regression (Scikit-Learn `RandomForestRegressor`).
- **Demonstration:** Evaluates residential properties based on square footage, bedrooms, and bathrooms.
- **Workflow:** Registers `house-price-prediction`, logs predictions, submits actual post-sale ground truth, triggers a simulated `FeatureStoreTimeoutError`, and logs resource metrics.
- **Run Command:**
  ```powershell
  .\.venv\Scripts\python.exe examples\house_price_service.py
  ```

### 2. Credit Card Fraud Detection Engine (`examples/fraud_detection_service.py`)
- **Category:** Binary Classification (Risk scoring model).
- **Demonstration:** Evaluates payment transactions for fraud risk based on amount, foreign origin, and transaction time.
- **Workflow:** Registers `fraud-detection-engine`, logs transaction predictions, verifies chargebacks, triggers a simulated `RedisCacheConnectionTimeout`, and updates Prometheus metrics.
- **Run Command:**
  ```powershell
  .\.venv\Scripts\python.exe examples\fraud_detection_service.py
  ```

---

## 17. Troubleshooting & Diagnostics

### 1. Port 8000 Already in Use
If another service is using port `8000`:
```powershell
# Windows: Identify process on port 8000
netstat -ano | findstr :8000
# Run on an alternate port
.\.venv\Scripts\uvicorn.exe integration.api:app --host 127.0.0.1 --port 8080 --reload
```

### 2. `ModuleNotFoundError: No module named 'mlflow'`
Ensure you are using the virtual environment's Python executable rather than system Python:
```powershell
# Windows
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
# Linux / macOS
./.venv/bin/python -m pip install -r requirements.txt
```

### 3. Missing Anomaly Detection Model Artifact
If `models/log_anomaly_detector.joblib` is missing:
```bash
python integration/train_anomaly_detector.py
```

### 4. Telemetry Returning `401 Unauthorized`
Verify that your request includes the exact API key received during project registration:
- Header: `X-API-Key: dr_live_...`
- Or Header: `Authorization: Bearer dr_live_...`
- Administrative Override: You can pass `DRISHTI_MASTER_API_KEY` configured in `.env`.

---

## 18. Security & Data Isolation

- **Project Data Isolation:** Telemetry records for each project are written exclusively to `data/telemetry/{project_id}.jsonl`. Queries for one project cannot access data from another.
- **Cryptographic Key Hashing:** API keys are generated using `secrets.token_hex(20)`, and only `SHA-256` hashes are retained on disk in `data/projects.json`.
- **Credential Masking:** API keys are masked in the UI, logs, and `GET /projects` outputs (e.g. `dr_live_3f8a...`).
- **Local-First Design:** DRISHTI AI is designed for local development and private internal network deployment. If exposing to public networks, run behind a reverse proxy (e.g. Nginx or Caddy) with TLS/HTTPS termination.

---

## 19. Project Roadmap & Implementation Status

| Feature / Capability | Category | Status | Notes |
| :--- | :--- | :---: | :--- |
| **Multi-Project Ingestion Gateway** | Core Platform | **Implemented** | Project isolation, API key auth, batch & single ingestion |
| **Loglizer IsolationForest Anomaly Engine** | Anomaly Detection | **Implemented** | 16-feature vectorizer, 100-tree unsupervised model |
| **Incident Management & Deduplication** | AIOps | **Implemented** | MD5 fingerprinting, occurrence tracking, lifecycle audits |
| **Ground-Truth Drift & Accuracy Engine** | MLOps | **Implemented** | Computes real-time MAE, RMSE, and health status |
| **Safe Automated Response Engine** | AIOps | **Implemented** | Simulated remediation playbooks with audit logging |
| **Prometheus Exporter (`/metrics`)** | Observability | **Implemented** | Standards-compliant Prometheus format (v0.0.4) |
| **React 18 / Tailwind CSS Dashboard** | Frontend | **Implemented** | Multi-project selector, live telemetry, incident triage |
| **Local Python Client SDK (`drishti_sdk`)** | SDK | **Implemented** | Non-blocking thread buffer, safe key masking |
| **Keep AIOps Integration** | AIOps | **Adapter / Fallback** | Integrates when Keep is running; falls back to local engine |
| **Pre-configured Grafana Dashboard** | Observability | **In Progress** | `monitoring/drishti_grafana_dashboard.json` included |
| **PyPI Distribution of `drishti-sdk`** | Ecosystem | **Planned** | Public package publishing on PyPI |
| **Distributed Message Queue (Kafka/RabbitMQ)**| Scalability | **Planned** | For high-throughput distributed ingestion clusters |

---

## 20. Contributing

Contributions to DRISHTI AI are welcome! Please follow these steps:

1. **Fork the Repository:** Create your feature branch (`git checkout -b feature/amazing-feature`).
2. **Implement Changes:** Ensure clean code following PEP 8 conventions.
3. **Run the Full Test Suite:** All tests must pass with 100% success:
   ```bash
   python scripts/run_all_tests.py
   ```
4. **Commit Your Changes:** Use clear, conventional commit messages (`git commit -m 'feat: add custom metric support'`).
5. **Open a Pull Request:** Describe your changes, operational impact, and test results.

---

## 21. License & Acknowledgements

### License Notice
*This repository does not currently contain a formalized open-source license file. An open-source license (such as Apache 2.0 or MIT) should be selected before public distribution.*

### Third-Party Acknowledgements
DRISHTI AI builds upon the research and open-source contributions of:
- **Loglizer:** Log anomaly detection algorithms developed by CUHK researchers ([logpai/loglizer](https://github.com/logpai/loglizer)).
- **MLflow:** Open-source platform for the machine learning lifecycle ([mlflow.org](https://mlflow.org/)).
- **FastAPI:** Modern, high-performance web framework ([tiangolo/fastapi](https://github.com/tiangolo/fastapi)).
- **Keep:** Open-source AIOps and alert management engine ([keephq/keep](https://github.com/keephq/keep)).
- **Scikit-Learn:** Machine learning tools for data analysis and modeling ([scikit-learn.org](https://scikit-learn.org/)).

---

*DRISHTI AI — Empowering Machine Learning Teams with Complete Operational Observability.*
