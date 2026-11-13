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
- **Algorithmic Evaluation:** Implements deterministic, multi-factor risk scoring incorporating 24-hour cumulative precipitation, river gauge flood danger marks, and terrain susceptibility multipliers.
- **Calibrated Operational Modes:**
  - `🌐 Live Real-Time`: Ingests active meteorological ground truth for Dhemaji directly via Open-Meteo APIs, dynamically adjusting flood risk indices.
  - `🟢 Normal Baseline`: Low-risk safe state (score 0.0), silent ambient monitoring.
  - `🟡 Monsoon Watch`: Moderate-risk watch state with procedural, multi-stage thunderbolt audio synthesis (lightning snap and deep rolling reverberation) without false siren triggers.
  - `🔴 Embankment Breach`: Critical emergency state triggering dual-oscillator piercing evacuation sirens, interactive evacuation modals, and fast-path tactical map switching.
- **Stale Data Guarding:** Observations older than the statutory 12-hour freshness window are automatically flagged as `STALE DATA / DATA UNAVAILABLE` to prevent false confidence during communication blackouts.

### 2. Dual-Viewport GIS Visualization
- **3D WebGL Earth Globe:** Built on Three.js with realistic atmospheric scattering, elevation bumps, directional sunlight simulation, coordinate-accurate targeting, and smooth orbital flight transitions.
- **Tactical Flood Grid Map:** High-resolution Leaflet map displaying:
  - CWC river gauge stations with live flood-stage status.
  - IMD rainfall measurement stations.
  - Digitized flood inundation hazard polygons (Subansiri Corridor, Gai River Flash Flood Spillway, Jiadhal Fan).
  - High-visibility vector tactical pins with radar pulse animation, draggable repositioning, and double-click / context-menu instant deletion.

### 3. Incident Management & Zero-PII Victim Privacy
- **Statutory Workflow State Machine:** Incidents enter strictly as `UNVERIFIED` and require verified operator authentication to progress (`UNDER REVIEW` $\to$ `VERIFIED` $\to$ `ASSIGNED` $\to$ `IN PROGRESS` $\to$ `RESOLVED` $\to$ `CLOSED`).
- **Privacy Sanitization:** Cryptographically and programmatically scrubs confidential reporter contact details, phone numbers, and identifying data from public endpoints.
- **Immutable Audit Trail:** System actions, resource allocations, and operator transitions are recorded in an append-only audit ledger with SHA-256 integrity hash verification.

### 4. Zero-Internet / Offline-First Resilience
- **Decoupled Architecture:** Runs entirely on-device or on a local battery-powered node (e.g., Raspberry Pi or local field laptop) binding to `0.0.0.0:8000` over local Wi-Fi.
- **Browser-Native Audio Synthesis:** All siren warbles and thunderbolt sounds are synthesized on the fly via the browser Web Audio API—requiring zero external audio downloads or CDN assets.
- **P2P Mesh Integration:** In-browser BitChat mesh protocol using BroadcastChannel, localStorage synchronization, and Web Bluetooth (BLE) peripheral pairing for message relay during complete ISP blackouts.

---

## Technical Stack

- **Backend:** Python 3.10+, FastAPI (ASGI architecture on Uvicorn)
- **Database:** SQLite via SQLAlchemy ORM (thread-isolated session dependencies)
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
│   ├── auth.py                         # JWT token authentication & bcrypt password hashing
│   ├── data_validation.py              # Boundary & schema validation
│   ├── notification_service.py         # Resilient alert dispatch service
│   ├── risk_engine.py                  # Core hydrological risk scoring algorithms
│   ├── security.py                     # Rate limiting & security middleware
│   └── trend_predictor.py              # Telemetry trend modeling
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

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ayusharma1601/disaster-app.git
   cd disaster-app
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize sample telemetry:**
   ```bash
   python load_demo.py
   ```

5. **Start the platform:**
   ```bash
   python -m uvicorn main:app --host 0.0.0.0 --port 8000
   ```
   Or simply execute `start.bat` on Windows.

6. **Access the application:**
   - Web Platform: [http://localhost:8000](http://localhost:8000)
   - Interactive API Docs (OpenAPI/Swagger): [http://localhost:8000/docs](http://localhost:8000/docs)
   - LAN / Mobile Access: `http://<YOUR_LOCAL_IP>:8000`

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
