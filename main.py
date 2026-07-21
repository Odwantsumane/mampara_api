from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import advances, auth, billing, credit_bureau, dashboard, kyc, profile, settings

app = FastAPI(title="Mampara API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5180",
        "http://127.0.0.1:5180",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(advances.router)
app.include_router(profile.router)
app.include_router(kyc.router)
app.include_router(billing.router)
app.include_router(credit_bureau.router)
app.include_router(settings.router)


@app.get("/api/health")
def health():
    return {"ok": True}
