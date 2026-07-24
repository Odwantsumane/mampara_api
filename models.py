import uuid
from datetime import date, datetime

from sqlalchemy import JSON, BigInteger, Boolean, Date, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from db import Base


def new_uuid() -> str:
    return str(uuid.uuid4())


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class UpdatedAtMixin:
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class User(Base, TimestampMixin, UpdatedAtMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))
    profileType: Mapped[str] = mapped_column(String(32))
    name: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(255))
    badgeIcon: Mapped[str] = mapped_column(String(64))
    badgeText: Mapped[str] = mapped_column(String(255))
    tier: Mapped[str] = mapped_column(String(255))
    avatar: Mapped[str] = mapped_column(String(500))
    inputNames: Mapped[str] = mapped_column(String(255), default="")
    inputSurnames: Mapped[str] = mapped_column(String(255), default="")
    inputIdNumber: Mapped[str] = mapped_column(String(32), default="")
    inputPhone: Mapped[str] = mapped_column(String(64), default="")
    inputResidency: Mapped[str] = mapped_column(String(500), default="")
    notifyEmail: Mapped[bool] = mapped_column(Boolean, default=True)
    notifyPush: Mapped[bool] = mapped_column(Boolean, default=True)
    notifySms: Mapped[bool] = mapped_column(Boolean, default=False)
    notifyNewsletter: Mapped[bool] = mapped_column(Boolean, default=False)
    loginAlerts: Mapped[bool] = mapped_column(Boolean, default=True)


class Advance(Base, TimestampMixin, UpdatedAtMixin):
    __tablename__ = "advances"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    # every advance belongs to a real registered borrower — the FK is what
    # actually enforces that, rather than just trusting a free-text name
    borrowerId: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    borrower: Mapped[str] = mapped_column(String(255))  # denormalized display name, set from the user at creation
    principal: Mapped[str] = mapped_column(String(64))
    fee: Mapped[str] = mapped_column(String(64))
    dueDate: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(64))
    statusIcon: Mapped[str] = mapped_column(String(64))
    statusClass: Mapped[str] = mapped_column(String(32))
    sortOrder: Mapped[int] = mapped_column(BigInteger, default=0)


class Payment(Base, TimestampMixin, UpdatedAtMixin):
    """One row per Paystack (or mock) checkout attempt against an advance's
    repayment — the reference is the gateway's own transaction reference."""

    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    reference: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    advanceId: Mapped[str] = mapped_column(String(32), ForeignKey("advances.id"), index=True)
    borrowerId: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    amount: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(32), default="Pending")  # Pending | Success | Failed
    authorizationUrl: Mapped[str] = mapped_column(String(500), default="")


class KycDocument(Base, TimestampMixin, UpdatedAtMixin):
    __tablename__ = "kyc_documents"

    key: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    userId: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    category: Mapped[str] = mapped_column(String(64))  # machine key: id_document, proof_of_residence, ...
    categoryLabel: Mapped[str] = mapped_column(String(255))
    fileName: Mapped[str] = mapped_column(String(255))
    # relative path under uploads/ (e.g. "approval/<userId>/<uuid>.pdf"), or a
    # bare http(s) URL for the seed rows that don't have a real file on disk
    filePath: Mapped[str] = mapped_column(String(500), default="")
    type: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(32), default="Pending Review")


class BillingProfile(Base, TimestampMixin, UpdatedAtMixin):
    """Parent row payment methods hang off of (one per profileType)."""

    __tablename__ = "billing_profiles"

    profileType: Mapped[str] = mapped_column(String(32), primary_key=True)


class PaymentMethod(Base, TimestampMixin, UpdatedAtMixin):
    __tablename__ = "payment_methods"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    profileType: Mapped[str] = mapped_column(String(32), ForeignKey("billing_profiles.profileType"), index=True)
    type: Mapped[str] = mapped_column(String(16))  # 'card' | 'paypal'
    brand: Mapped[str | None] = mapped_column(String(32), nullable=True)
    last4: Mapped[str | None] = mapped_column(String(4), nullable=True)
    cardNumber: Mapped[str | None] = mapped_column(String(32), nullable=True)
    cardholderName: Mapped[str | None] = mapped_column(String(255), nullable=True)
    expiry: Mapped[str | None] = mapped_column(String(16), nullable=True)
    debitDate: Mapped[str | None] = mapped_column(String(16), nullable=True)
    label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    isPrimary: Mapped[bool] = mapped_column(Boolean, default=False)


class PortfolioSnapshot(Base, TimestampMixin, UpdatedAtMixin):
    """One row per calendar day, upserted whenever the admin dashboard is
    loaded — a real, organically-accumulating history the trend indicators
    are computed from. No row for a given day means we simply don't have
    data for that day; there's nothing to fabricate."""

    __tablename__ = "portfolio_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    snapshotDate: Mapped[date] = mapped_column(Date, unique=True, index=True)
    activeTotal: Mapped[float] = mapped_column(Float)
    pendingTotal: Mapped[float] = mapped_column(Float)
    defaultRatePercent: Mapped[float] = mapped_column(Float)


class PlatformSettings(Base, TimestampMixin, UpdatedAtMixin):
    __tablename__ = "platform_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    advanceFeePercent: Mapped[float] = mapped_column(Float, default=15)
    universalAdvanceLimit: Mapped[float] = mapped_column(Float, default=1000)


class DashboardCopy(Base, TimestampMixin):
    __tablename__ = "dashboard_copy"

    profileType: Mapped[str] = mapped_column(String(32), primary_key=True)
    copy: Mapped[dict] = mapped_column(JSON)


class ChartData(Base, TimestampMixin):
    __tablename__ = "chart_data"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)  # 'trend' | 'allocation'
    data: Mapped[dict] = mapped_column(JSON)


class PublicTeaser(Base, TimestampMixin):
    __tablename__ = "public_teaser"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    data: Mapped[dict] = mapped_column(JSON)


class CreditScoreRecord(Base, TimestampMixin):
    __tablename__ = "credit_score_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    # nullable: an admin can look up someone by name/ID who isn't a
    # registered borrower yet — linked automatically when the ID number
    # matches an existing user.
    borrowerId: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    idNumber: Mapped[str] = mapped_column(String(32))
    bureau: Mapped[str] = mapped_column(String(32))
    score: Mapped[int] = mapped_column(Integer)
    scoreScaleLabel: Mapped[str] = mapped_column(String(255))
    riskLabel: Mapped[str] = mapped_column(String(64))
    defaultJudgements: Mapped[str] = mapped_column(String(255))
    openFacilities: Mapped[str] = mapped_column(String(255))
    affordability: Mapped[str] = mapped_column(String(255))
    recommendedMaxAdvance: Mapped[str] = mapped_column(String(64))
