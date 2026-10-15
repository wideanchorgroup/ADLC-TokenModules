# Deployment & Operations Guide

> **Document Version**: 1.0.0  
> **Platform**: Python 3.10+ • FastAPI • SQLite / PostgreSQL

---

## 1. Quick Local Execution

### 1.1 Prerequisites
- Python 3.10+
- Virtual environment tool (`venv` or `uv`)

### 1.2 Running Standalone
```bash
# Clone the repository
git clone https://github.com/wideanchorgroup/ADLC-TokenModules.git
cd ADLC-TokenModules

# Create virtualenv and install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run the server and interactive dashboard
python run_server.py
```

Open your browser to:
- **Interactive Dashboard**: `http://localhost:8000/`
- **Swagger / OpenAPI Documentation**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/api/health`

---

## 2. CLI Tool Usage (`adlc-finops`)

The platform includes a CLI tool for automation and terminal operation:

```bash
# Activate virtual environment
source .venv/bin/activate

# View overall FinOps summary
python -m adlc_finops.cli finops summary

# Update global monthly budget cap
python -m adlc_finops.cli finops budget --cap 60000.0 --scope global

# Trigger emergency kill switch
python -m adlc_finops.cli finops kill-switch --activate --reason "Runaway loop detected"

# Assess repository qualification scorecard
python -m adlc_finops.cli qualify --repo wideanchorgroup/payments --owner payments-team

# Inspect fleet nodes and drift status
python -m adlc_finops.cli fleet

# Onboard a new developer + repository
python -m adlc_finops.cli onboard --developer dev_jane --repo wideanchorgroup/payments --budget 750.0 --ring canary_5

# Launch golden-path task
python -m adlc_finops.cli task --template task-unit-bug --repo wideanchorgroup/ADLC-TokenModules --prompt "Fix null pointer in config parser"
```

---

## 3. Configuration & Environment Variables

All settings can be configured via environment variables or a `.env` file:

| Variable | Default Value | Description |
|---|---|---|
| `ADLC_HOST` | `0.0.0.0` | Server bind IP address |
| `ADLC_PORT` | `8000` | Server bind port |
| `ADLC_ENV` | `development` | Environment name (development/staging/production) |
| `ADLC_DB_PATH` | `./adlc_finops.db` | Path to persistent SQLite database |
| `ADLC_MOCK_MODE` | `true` | Set to `false` in production to use live Compass/Distil/Halos services |
| `COMPASS_API_URL` | `http://localhost:8081` | Compass guardrails and review/test/fix API endpoint |
| `COMPASS_API_KEY` | `cmp-enterprise-token` | Compass authentication token |
| `COMPASS_MAX_USD_DEFAULT`| `5.00` | Default per-session budget ceiling |
| `DISTIL_API_URL` | `http://localhost:8082` | Distil compression & savings receipt endpoint |
| `DISTIL_API_KEY` | `dst-enterprise-token` | Distil authentication token |
| `DISTIL_DEFAULT_MODE` | `lossless` | Context compression mode (`lossless` or `aggressive`) |
| `HALOS_API_URL` | `http://localhost:8083` | Halos control plane & signed releases endpoint |
| `HALOS_API_KEY` | `hls-enterprise-token` | Halos authentication token |
| `FINOPS_MONTHLY_BUDGET_CAP` | `50000.00` | Global monthly spend ceiling across all agents |

---

## 4. Production Deployment

### 4.1 Production systemd Service
Create `/etc/systemd/system/adlc-finops.service`:
```ini
[Unit]
Description=ADLC FinOps & Governance Control Plane
After=network.target

[Service]
User=adlc-runner
WorkingDirectory=/opt/adlc-finops
ExecStart=/opt/adlc-finops/.venv/bin/uvicorn adlc_finops.server:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=5
Environment=ADLC_ENV=production
Environment=ADLC_MOCK_MODE=false
Environment=COMPASS_API_URL=https://compass.internal.wideanchor.net
Environment=DISTIL_API_URL=https://distil.internal.wideanchor.net
Environment=HALOS_API_URL=https://halos.internal.wideanchor.net

[Install]
WantedBy=multi-user.target
```

### 4.2 Docker Container
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "adlc_finops.server:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 5. Health Checks & Telemetry

- **Readiness / Liveness Probe**: `GET /api/health`
  - Returns `200 OK` and status of integrated Compass, Distil, and Halos connections.
- **Audit Verification**:
  - `GET /api/v1/evidence/records` supplies tamper-evident task histories for compliance audits (SOC2, ISO 27001).
