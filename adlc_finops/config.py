"""Configuration settings for ADLC FinOps platform."""

import os
from dataclasses import dataclass
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

@dataclass
class Settings:
    # Server configuration
    host: str = os.getenv("ADLC_HOST", "0.0.0.0")
    port: int = int(os.getenv("ADLC_PORT", "8000"))
    environment: str = os.getenv("ADLC_ENV", "development")
    db_path: str = os.getenv("ADLC_DB_PATH", str(BASE_DIR / "adlc_finops.db"))

    # Compass Service Config
    compass_api_url: str = os.getenv("COMPASS_API_URL", "http://localhost:8081")
    compass_api_key: str = os.getenv("COMPASS_API_KEY", "cmp-enterprise-token")
    compass_max_usd_default: float = float(os.getenv("COMPASS_MAX_USD_DEFAULT", "5.00"))

    # Distil Service Config
    distil_api_url: str = os.getenv("DISTIL_API_URL", "http://localhost:8082")
    distil_api_key: str = os.getenv("DISTIL_API_KEY", "dst-enterprise-token")
    distil_default_mode: str = os.getenv("DISTIL_DEFAULT_MODE", "lossless")

    # Halos Service Config
    halos_api_url: str = os.getenv("HALOS_API_URL", "http://localhost:8083")
    halos_api_key: str = os.getenv("HALOS_API_KEY", "hls-enterprise-token")
    halos_fleet_ring_default: str = os.getenv("HALOS_FLEET_RING_DEFAULT", "canary_5")

    # FinOps Enterprise Thresholds
    monthly_budget_hard_cap: float = float(os.getenv("FINOPS_MONTHLY_BUDGET_CAP", "50000.00"))
    task_cost_alert_threshold: float = float(os.getenv("FINOPS_TASK_ALERT_THRESHOLD", "15.00"))
    kill_switch_active: bool = os.getenv("FINOPS_KILL_SWITCH", "false").lower() == "true"

    # Simulation mode (allows running without live compass/distil/halos servers)
    mock_mode: bool = os.getenv("ADLC_MOCK_MODE", "true").lower() == "true"

settings = Settings()
