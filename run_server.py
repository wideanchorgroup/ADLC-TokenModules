"""Server entry point for ADLC FinOps & Governance Control Plane."""

import uvicorn
from adlc_finops.config import settings

def main():
    print(f"🚀 Starting ADLC FinOps Platform on http://{settings.host}:{settings.port}")
    print(f"📚 OpenAPI Documentation available on http://{settings.host}:{settings.port}/docs")
    print(f"🧭 Consuming Compass: {settings.compass_api_url}")
    print(f"⚡ Consuming Distil:  {settings.distil_api_url}")
    print(f"📡 Consuming Halos:   {settings.halos_api_url}")
    uvicorn.run("adlc_finops.server:app", host=settings.host, port=settings.port, reload=False)

if __name__ == "__main__":
    main()
