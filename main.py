import pathlib

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import models
from db import SessionLocal, engine
from routers import advances, auth, billing, borrowers, credit_bureau, dashboard, kyc, payments, profile, settings
from seed import seed_if_empty

models.Base.metadata.create_all(bind=engine)

UPLOAD_DIR = pathlib.Path("uploads")
(UPLOAD_DIR / "approval").mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Mampara API", version="0.2.0")

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

# Serves uploaded KYC documents back to the frontend, e.g.
# /uploads/approval/<borrowerId>/<file>.pdf
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


@app.on_event("startup")
def on_startup():
    db = SessionLocal()
    try:
        seed_if_empty(db)
    finally:
        db.close()


app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(advances.router)
app.include_router(profile.router)
app.include_router(kyc.router)
app.include_router(borrowers.router)
app.include_router(billing.router)
app.include_router(credit_bureau.router)
app.include_router(payments.router)
app.include_router(settings.router)


@app.get("/api/health")
def health():
    return {"ok": True}
