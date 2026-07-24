"""
Request body models. Field names intentionally match the JSON shapes the
frontend already sends (camelCase) so the API is a drop-in replacement for
the old client-side mock — no frontend payload shapes need to change.
"""

from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str


class SignupRequest(BaseModel):
    name: str
    email: str
    password: str
    phone: str = ""


class UpdateProfileRequest(BaseModel):
    userId: str
    fields: dict


class ChangePasswordRequest(BaseModel):
    userId: str
    currentPassword: str
    newPassword: str


class CreateAdvanceRequest(BaseModel):
    borrowerId: str
    principal: float
    feePercent: float
    termDays: int


class AdvanceDecisionRequest(BaseModel):
    id: str


class AddPaymentMethodRequest(BaseModel):
    profileType: str
    cardholderName: str
    cardNumber: str
    expiry: str
    debitDate: str


class UpdatePaymentMethodRequest(BaseModel):
    profileType: str
    cardholderName: str
    cardNumber: str
    expiry: str
    debitDate: str


class CreditCheckRequest(BaseModel):
    name: str = ""
    idNumber: str = ""
    bureau: str = ""


class UpdateSettingsRequest(BaseModel):
    advanceFeePercent: float | None = None
    universalAdvanceLimit: float | None = None


class InitializePaymentRequest(BaseModel):
    advanceId: str
    borrowerId: str
