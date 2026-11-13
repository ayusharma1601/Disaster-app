# Disaster Intelligence & Tactical Flood Response Platform

An offline-first, local-first hydrological intelligence and community crisis coordination platform designed for disaster-prone river basins (deployed and tested for the Dhemaji District, Subansiri & Gai River basin in Assam, India).

The platform integrates real-time meteorological observations with edge-computed risk scoring, dual-viewport GIS (continuous 3D WebGL Earth to high-resolution 2D tactical maps), offline P2P mesh chat, and community incident reporting with zero PII leakage.

---

> ### ⚠️ Prototype & Operational Status Notice
> **This software is an evolution prototype.**
> 
> While the platform supports **live, real-time meteorological telemetry ingestion** (fetching live precipitation, temperature, humidity, and wind telemetry from Open-Meteo WMO stations for Dhemaji coordinates at 27.48°N, 94.58°E), it is currently designed and deployed as a **proof-of-concept and decision-support prototype**.
>
> 1. **Statutory Precedence:** In live disaster situations, official statutory alerts, water level classifications, and evacuation directives issued by the **Assam State Disaster Management Authority (ASDMA)**, **Central Water Commission (CWC)**, and **India Meteorological Department (IMD)** take statutory precedence over automated algorithm evaluations.
> 2. **Emergency Numbers:** This platform does not replace emergency dispatch services. In life-threatening emergencies, dial national emergency response (`112`) or state disaster management helpline (`1070`).
> 3. **Validation & Field Trials:** Sensor telemetry calibrations and offline radio mesh bridges (LoRaWAN/Bluetooth LE) are configured for demonstration, stress-testing, and field evaluation.

---

## Key Capabilities

### 1. Multi-Tier Telemetry & Risk Assessment Engine
- **Rule-Based Risk Assessment:** Implements deterministic, explainable multi-factor risk scoring incorporating 24-hour cumulative precipitation, river gauge warning/danger marks, and basin susceptibility multipliers.
- **Operational Data Modes:**
  - `🌐 Live Hybrid`: Ingests active meteorological ground truth for Dhemaji HQ directly via Open-Meteo APIs, combined with simulated rainfall multipliers for surrounding circles and baseline river gauges.
  - `🟢 Normal Baseline`: Low-risk safe state (score 0.0), ambient monitoring with sample data.
  - `🟡 Monsoon Watch`: Moderate-risk watch state with procedural, multi-stage thunderbolt audio synthesis without false siren triggers.
  - `🔴 Embankment Breach`: Emergency state triggering dual-oscillator evacuation sirens, interactive warning modals, and fast-path tactical map switching.
- **Stale Data Guarding:** Observations older than the statutory 12-hour freshness window are automatically flagged as `STALE DATA / DATA UNAVAILABLE` to prevent false confidence during communication blackouts.

### 2. Dual-Viewport GIS Visualization
- **3D WebGL Earth Globe:** Built on Three.js with atmospheric scattering, elevation contours, directional sunlight simulation, coordinate targeting, and orbital flight transitions.
- **Tactical Flood Grid Map:** High-resolution Leaflet map displaying:
  - CWC river gauge stations with flood-stage markers (sample historical telemetry).
  - IMD rainfall measurement stations (live Open-Meteo weather + simulated stations).
  - Hazard polygons for vulnerable corridors (Subansiri Corridor, Gai River Flash Flood Spillway, Jiadhal Fan).
  - Interactive tactical pins with radar pulse animation, draggable repositioning, and deletion.

### 3. Incident Management, NLP Triage & Victim Privacy
- **NLP Incident Triage:** On-device lexical NLP classifier (`services/ai_triage.py`) analyzes incoming SOS descriptions, calculating a threat score (0.00 to 1.00), urgency tier, and recommending matching response resources (Rescue Boats, Medical Units, Relief Camps, SDRF Squads).
- **Statutory Workflow State Machine:** Incidents enter strictly as `UNVERIFIED` and require verified operator authentication to progress (`UNDER REVIEW` $\to$ `VERIFIED` $\to$ `ASSIGNED` $\to$ `IN PROGRESS` $\to$ `RESOLVED` $\to$ `CLOSED`).
- **Privacy Sanitization:** Programmatically scrubs confidential reporter contact details and phone numbers from public endpoints.
- **Audit Logging:** System actions, resource allocations, and operator transitions are recorded in an append-only database audit log table for accountability.

### 4. Experimental Rainfall-Runoff Prediction
- **Dynamic Telemetry & Sample Forecast Ingestion:** Aggregates active station rainfall, baseline river gauges, and sample 48-hour IMD rainfall projections.
- **Empirical Logistic Curve Modeling:** Uses a parameterised logistic regression curve combined with nearest-neighbour matching against historical ASDMA monsoon flood cases (2020–2024 Dhemaji records) to estimate flood crest lead time, surge margin, and evacuation advisories.

### 5. Experimental Offline Communication Interface
- **Decoupled Architecture:** Runs locally on-device or on a local battery-powered node (e.g., Raspberry Pi or field laptop) binding to `0.0.0.0:8000` over local Wi-Fi.
- **Browser-Native Audio Synthesis:** Siren warbles and thunder sounds are synthesized on the fly via the browser Web Audio API—requiring zero external audio assets.
- **Experimental Offline Mesh Interface:** Prototype offline communication using `BroadcastChannel` and `localStorage` synchronization across browser tabs/windows on the same node, with Web Bluetooth (BLE) peripheral pairing demonstration UI for radio packet bridge evaluation.

---

## Prototype Intelligence & Data Architecture

The platform combines explainable rules, lexical NLP, and empirical statistical formulas engineered to operate locally without external cloud dependencies:

### 1. NLP-Based Incident Triage (`services/ai_triage.py`)
- **Method:** Lexical Bag-of-Words & Semantic Urgency Scoring.
- **Threat Index ($0.00$ to $1.00$):** Scans incoming citizen SOS descriptions for weighted distress keywords (`marooned`, `stranded`, `water rising fast`, `infant`, `breached`) and calculates an explainable threat score.
- **Urgency Classification:** Classifies reports into standardized emergency tiers (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) to assist operators in prioritizing rapid response.
- **Targeted Resource Recommendations:** Suggests disaster response assets based on semantic patterns:
  - *Submerged / Stranded / Water Influx* $\to$ `Rescue Boat`
  - *Casualties / Trauma / Medical Distress* $\to$ `Medical Unit`
  - *Displaced Residents / Homelessness* $\to$ `Relief Camp`
  - *Embankment Collapse / Road Cutoff* $\to$ `SDRF Squad`
  - *Drinking Water Shortages* $\to$ `Water Tanker`
- **Explainable Rationale:** Automatically generates human-auditable rationale notes stored with the incident for dispatch coordinators.

### 2. Experimental Rainfall-Runoff Prediction (`services/trend_predictor.py`)
- **Method:** Parameterised Logistic (Sigmoid) Curve & Nearest-Neighbour Historical Analogue Matching.
- **Dynamic Ingestion:** Ingests live Dhemaji weather observations alongside sample station telemetry and IMD rainfall estimates.
- **Empirical Crest Probability Function:**
  $$\text{Prob}(\text{Flood}) = \frac{1}{1 + e^{-k \cdot (\text{Rainfall}_{72\text{h}} - x_0) - (\text{WaterMargin} \cdot \alpha)}}$$
  where $x_0 = 175\text{ mm}$ (historical basin saturation threshold), $k = 0.022$ (steepness coefficient), and $\text{WaterMargin}$ is the river water level relative to the danger mark ($86.00\text{ m}$).
- **Historical Analogue Matching:** Matches current precipitation loads with ASDMA Dhemaji flood archives (2020–2024 records) to estimate flood peak lead times (12h, 18h, 24h, 36h).

### 3. Data Transparency & Operational Disclosure
- **Live Meteorological Data:** Real-time ground precipitation, temperature, humidity, and wind speed fetched live from Open-Meteo for Dhemaji coordinates (27.48°N, 94.58°E).
- **Simulated Station Multipliers:** Surrounding circle stations (Jonai, Silapathar, Gogamukh) apply scaled multipliers ($0.8\times$ to $1.1\times$) to demonstrate multi-station telemetry ingestion.
- **Sample Datasets:** River gauge levels and government forecast bulletins (`cwc_flood_forecast.json`, `imd_weather_forecast.json`) use calibrated historical baseline samples.
- **Offline Mesh Status:** Uses browser-level `BroadcastChannel` and `localStorage` between open tabs/windows on the same node, with an experimental Web Bluetooth (BLE) UI demonstration.

---

## Technical Stack

- **Backend:** Python 3.10+, FastAPI (ASGI architecture on Uvicorn)
- **AI & Predictive Modeling:** On-device NLP Bag-of-Words & Semantic Triage Classifier, Calibrated Hydrological Logistic Flood Regressor
- **Database:** SQLite via SQLAlchemy ORM (thread-isolated session dependencies, serverless /tmp auto-routing)
- **Frontend:** Vanilla JavaScript (ES6+), HTML5, CSS3 (Light & True-Black Dark themes)
- **3D Graphics & Maps:** Three.js, OrbitControls, Leaflet.js
- **Audio Engine:** HTML5 Web Audio API (procedural audio synthesis)
- **Security:** HTTP Security Headers (CSP, X-Frame-Options, X-Content-Type-Options), custom sliding-window IP rate limiters, input sanitization

---

## Project Structure

```text
disaster-app/
├── data/
│   └── sample/
│       ├── cwc_flood_forecast.json     # Sample CWC river gauge bulletin
│       ├── dhemaji_telemetry.csv       # Sample hydrological observation dataset
│       └── imd_weather_forecast.json   # Sample IMD 5-day weather bulletin
├── services/
│   ├── ai_triage.py                    # NLP triage classifier & emergency resource dispatch model
│   ├── auth.py                         # JWT token authentication & password hashing
│   ├── data_validation.py              # Boundary & schema validation
│   ├── notification_service.py         # Resilient alert dispatch service
│   ├── risk_engine.py                  # Core hydrological risk scoring algorithms
│   ├── security.py                     # Rate limiting & security middleware
│   └── trend_predictor.py              # Dynamic hydrological flood prediction engine
├── static/
│   ├── data/                           # TopoJSON geography models
│   ├── icons/                          # PWA application icons
│   ├── textures/                       # 8K Earth day and cloud textures
│   ├── vendor/                         # Local JS/CSS dependencies (Leaflet, Three.js)
│   ├── manifest.json                   # Web app manifest
│   └── service-worker.js               # Offline caching worker
├── templates/
│   ├── index.html                      # Main platform interface & tactical HUD
│   └── terms.html                      # Statutory terms of service & safety disclosures
├── tests/
│   ├── test_core.py                    # Core bounds & data ingestion tests
│   ├── test_comprehensive.py           # Threshold boundaries & risk engine tests
│   ├── test_gate4.py                   # Incident state machine & privacy tests
│   ├── test_gate5.py                   # Resource registry & shelter freshness tests
│   └── test_gate7.py                   # Security headers, rate limiting & XSS tests
├── database.py                         # SQLAlchemy database engine configuration
├── main.py                             # FastAPI application endpoints & routing
├── models.py                           # SQLAlchemy database models
├── requirements.txt                    # Project Python dependencies
├── run_all_tests.py                    # Master test runner (6 verification suites)
├── simulate_demo_cycle.py              # End-to-end incident lifecycle test script
└── start.bat                           # Local startup batch script
```

---

## Getting Started

### Prerequisites
- Python 3.10 or higher
- Git

### Installation & Quick Start

#### Method A: Instant One-Click Startup (Windows)
Run the automated launcher script from PowerShell or Command Prompt:
```cmd
cd disaster-app
start.bat
```
*(This automatically creates the virtual environment, installs dependencies, loads baseline telemetry, and opens the local server).*

---

#### Method B: Step-by-Step Manual Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ayusharma1601/disaster-app.git
   cd disaster-app
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - **On Windows (PowerShell):**
     ```powershell
     # If script execution is blocked, allow it for this session:
     Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
     .\venv\Scripts\Activate.ps1
     ```
     *Alternatively, in Windows Command Prompt (cmd.exe):*
     ```cmd
     venv\Scripts\activate.bat
     ```
   - **On Linux / macOS:**
     ```bash
     source venv/bin/activate
     ```

4. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Seed demo hydrological telemetry & database:**
   ```bash
   python load_demo.py
   ```

6. **Start the local ASGI web server:**
   ```bash
   python -m uvicorn main:app --host 0.0.0.0 --port 8000
   ```

---

## How to Access the Website Locally

Once the server is running (`Uvicorn running on http://0.0.0.0:8000`), open your web browser to any of the following URLs:

| View / Tool | Local URL | Description |
|---|---|---|
| **Main Tactical Dashboard** | [http://localhost:8000](http://localhost:8000) or [http://127.0.0.1:8000](http://127.0.0.1:8000) | Full 3D WebGL Earth globe, 2D tactical flood map, live telemetry, and community incident feed. |
| **Mobile / LAN Access** | `http://<YOUR_LOCAL_IP>:8000` | Access the platform from smartphones, tablets, or other laptops on the same Wi-Fi network (find your IP via `ipconfig` on Windows or `ifconfig` on Linux/Mac). |
| **Interactive API Documentation** | [http://localhost:8000/docs](http://localhost:8000/docs) | Interactive Swagger UI to inspect and test all REST API endpoints. |
| **Alternative API Docs** | [http://localhost:8000/redoc](http://localhost:8000/redoc) | Clean ReDoc API documentation format. |
| **Terms & Safety Disclosures** | [http://localhost:8000/terms](http://localhost:8000/terms) | Statutory compliance disclosures and offline safety guidelines. |

### Default Operator Credentials (For Triage & Resource Allocation)
To test responder workflows (assigning boats, changing incident statuses, reviewing audit logs), click **Operator Login** in the top navigation bar:
- **Admin Role:** Username: `admin` | Password: `admin123`
- **Field Responder Role:** Username: `operator` | Password: `operator123`

---

## Running the Automated Test Suite

The platform includes full automated quality verification covering ingestion, boundary conditions, privacy guarantees, security headers, and an end-to-end incident resolution cycle:

```bash
python run_all_tests.py
```

Expected output:
```text
======================================================================
RUNNING ALL PLATFORM TEST SUITES & QUALITY GATES
======================================================================
>> Running: Core Bounds & Ingestion (tests/test_core.py)...
   [PASS] Core Bounds & Ingestion
>> Running: Comprehensive Boundaries & Quality Flags (tests/test_comprehensive.py)...
   [PASS] Comprehensive Boundaries & Quality Flags
>> Running: Gate 4: Incident State Machine & Privacy (tests/test_gate4.py)...
   [PASS] Gate 4: Incident State Machine & Privacy
>> Running: Gate 5: Resource Registry & Shelter Freshness (tests/test_gate5.py)...
   [PASS] Gate 5: Resource Registry & Shelter Freshness
>> Running: Gate 7: Security Headers, XSS & Rate Limiting (tests/test_gate7.py)...
   [PASS] Gate 7: Security Headers, XSS & Rate Limiting
>> Running: Phase 6: End-to-End Operational Simulation (simulate_demo_cycle.py)...
   [PASS] Phase 6: End-to-End Operational Simulation
======================================================================
ALL TESTS COMPLETED: 6/6 SUITES PASSED (100% PASS RATE)
======================================================================
```

---

## License

This project is licensed under the MIT License.
