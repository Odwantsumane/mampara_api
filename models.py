from sqlalchemy import JSON, BigInteger, Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
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


class Session(Base):
    __tablename__ = "sessions"

    token: Mapped[str] = mapped_column(String(128), primary_key=True)
    userId: Mapped[str] = mapped_column(String(64), ForeignKey("users.id"))


class Advance(Base):
    __tablename__ = "advances"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    borrower: Mapped[str] = mapped_column(String(255))
    principal: Mapped[str] = mapped_column(String(64))
    fee: Mapped[str] = mapped_column(String(64))
    due: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(64))
    statusIcon: Mapped[str] = mapped_column(String(64))
    statusClass: Mapped[str] = mapped_column(String(32))
    sortOrder: Mapped[int] = mapped_column(BigInteger, default=0)


class KycDocument(Base):
    __tablename__ = "kyc_documents"

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    category: Mapped[str] = mapped_column(String(255))
    fileName: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(64))
    type: Mapped[str] = mapped_column(String(32))
    url: Mapped[str] = mapped_column(Text, default="")


class BillingProfile(Base):
    __tablename__ = "billing_profiles"

    profileType: Mapped[str] = mapped_column(String(32), primary_key=True)
    planName: Mapped[str] = mapped_column(String(255))
    planPrice: Mapped[str] = mapped_column(String(64))
    renewsOn: Mapped[str] = mapped_column(String(255))


class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
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


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    profileType: Mapped[str] = mapped_column(String(32), ForeignKey("billing_profiles.profileType"), index=True)
    date: Mapped[str] = mapped_column(String(64))
    amount: Mapped[str] = mapped_column(String(64))


class PlatformSettings(Base):
    __tablename__ = "platform_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    advanceFeePercent: Mapped[float] = mapped_column(Float, default=15)


class DashboardCopy(Base):
    __tablename__ = "dashboard_copy"

    profileType: Mapped[str] = mapped_column(String(32), primary_key=True)
    copy: Mapped[dict] = mapped_column(JSON)


class ChartData(Base):
    __tablename__ = "chart_data"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)  # 'trend' | 'allocation'
    data: Mapped[dict] = mapped_column(JSON)


class PublicTeaser(Base):
    __tablename__ = "public_teaser"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    data: Mapped[dict] = mapped_column(JSON)


class CreditBureauTemplate(Base):
    __tablename__ = "credit_bureau_template"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    data: Mapped[dict] = mapped_column(JSON)
