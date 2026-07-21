"""
In-memory "database" for the Mampara API.

No real database yet — everything lives in plain Python lists/dicts at module
scope, seeded with dummy data, and mutated directly by the routers. Restarting
the server resets everything back to the seed state. Swap these functions for
real persistence later without changing any router code.
"""

import random
import time

# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

users: list[dict] = [
    {
        "id": "usr_admin_1",
        "email": "sarah.jenkins@mampara.co.za",
        "password": "admin123",
        "profileType": "admin",
        "name": "Sarah Jenkins",
        "role": "Credit Manager",
        "badgeIcon": "bi-patch-check-fill",
        "badgeText": "Verified Lender Admin",
        "tier": "Enterprise Lender",
        "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&h=150&fit=crop&crop=faces",
        "inputNames": "Sarah",
        "inputSurnames": "Jenkins",
        "inputIdNumber": "9204125890081",
        "inputPhone": "+27 (0)82 382 9011",
        "inputResidency": "12 Fredman Drive, Sandton, Johannesburg, 2196",
    },
    {
        "id": "usr_borrower_1",
        "email": "sipho.dlamini@gmail.com",
        "password": "borrower123",
        "profileType": "borrower",
        "name": "Sipho Dlamini",
        "role": "Borrower Account",
        "badgeIcon": "bi-person-check-fill",
        "badgeText": "Verified Borrower",
        "tier": "Standard Borrower Tier",
        "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=faces",
        "inputNames": "Sipho",
        "inputSurnames": "Dlamini",
        "inputIdNumber": "8805125890082",
        "inputPhone": "+27 (0)71 492 8812",
        "inputResidency": "45 Vilakazi Street, Orlando West, Soweto, 1804",
    },
]

# token -> user id
sessions: dict[str, str] = {}


def find_user_by_email(email: str) -> dict | None:
    return next((u for u in users if u["email"].lower() == email.lower()), None)


def find_user_by_id(user_id: str) -> dict | None:
    return next((u for u in users if u["id"] == user_id), None)


def to_public_user(user: dict) -> dict:
    return {k: v for k, v in user.items() if k != "password"}


def make_token(user_id: str) -> str:
    return f"mampara.{user_id}.{random.randint(10 ** 9, 10 ** 10 - 1):x}"


# ---------------------------------------------------------------------------
# Dashboard copy
# ---------------------------------------------------------------------------

dashboard_copy: dict = {
    "admin": {
        "dashboardTitle": "Dashboard Overview",
        "dashboardSubtitle": "Welcome back to Mampara, here is your payday advance book performance.",
        "card1Title": "Total Active Advances",
        "card1Value": "R 86,400",
        "card1SubIcon": "bi-arrow-up-right",
        "card1SubText": "+8.4% from last month",
        "card1SubClass": "text-success",
        "card1ValueClass": "text-success",
        "card2Title": "Pending Approvals",
        "card2Value": "R 6,200",
        "card2Sub": "14 applications awaiting sign-off",
        "card3Title": "Portfolio Default Rate",
        "card3Value": "2.1%",
        "card3ValueClass": "text-danger",
        "card3SubIcon": "bi-arrow-down-right",
        "card3SubText": "-0.4% risk reduction",
        "card3SubClass": "text-success",
        "chartTitle": "Disbursement & Collections Trend",
        "sideTitle": "Advance Book Breakdown",
        "navLoanBook": "Advance Book",
        "navBorrowers": "Borrowers",
        "navCollections": "Collections",
        "calcBtnIcon": "bi-file-earmark-plus",
        "calcBtnText": "Create Advance From Simulation",
        "loanBookHeaderTitle": "Active Advance Book & Portfolio",
    },
    "borrower": {
        "dashboardTitle": "Borrower Portal Overview",
        "dashboardSubtitle": "Welcome back {name}, monitor your active advance and repayment date.",
        "card1Title": "Active Advance Balance",
        "card1Value": "R 650",
        "card1SubText": "Repayment due Aug 1, 2026 (payday)",
        "card1SubClass": "text-muted",
        "card1ValueClass": "",
        "card2Title": "Available Advance Limit",
        "card2Value": "R 1,000",
        "card2Sub": "Pre-approved based on credit score",
        "card3Title": "Credit Score Rating",
        "card3Value": "685",
        "card3ValueClass": "",
        "card3SubHtml": '<span class="text-success fw-semibold"><i class="bi bi-shield-check"></i> Good Standing</span>',
        "chartTitle": "Repayment History & Schedule",
        "sideTitle": "Advance Allocation",
        "navLoanBook": "My Advances",
        "navBorrowers": "My Profile",
        "navCollections": "Repayments",
        "calcBtnIcon": "bi-send-check",
        "calcBtnText": "Request This Advance",
        "loanBookHeaderTitle": "My Advance History",
    },
}

trend_chart_data: dict = {
    "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"],
    "values": [3200, 4100, 3800, 4600, 5200, 4900, 5600],
    "label": "Weekly Disbursement Volume (R)",
}

allocation_chart_data: dict = {
    "labels": ["New Advances", "Repeat Borrowers", "Rolled Over", "Settled Early"],
    "values": [45, 30, 15, 10],
}

public_teaser: dict = {
    "headline": "Get up to R 1,000 before payday — approved in minutes.",
    "sub": "Sign in or create a free account to see your personal advance offer, repayment date, and credit score.",
    "sampleAdvance": "R 500",
    "sampleFee": "R 75.00 (15%)",
    "sampleRepayment": "Repaid in 10 days, on your next payday",
    "stat1": {"label": "Advances funded this month", "value": "2,481"},
    "stat2": {"label": "Average approval time", "value": "4 minutes"},
    "stat3": {"label": "Max advance available", "value": "R 1,000"},
    "allocationLabels": ["New Advances", "Repeat Borrowers", "Rolled Over", "Settled Early"],
    "allocationValues": [45, 30, 15, 10],
}

# ---------------------------------------------------------------------------
# Advances (payday advance book)
# ---------------------------------------------------------------------------

advances: list[dict] = [
    {
        "id": "#ADV-2026-892", "borrower": "Sipho Dlamini", "principal": "R 650.00", "fee": "15% (R 97.50)",
        "due": "Due in 9 days", "status": "Performing", "statusIcon": "bi-check-circle-fill", "statusClass": "success",
    },
    {
        "id": "#ADV-2026-884", "borrower": "Nomusa Khumalo", "principal": "R 900.00", "fee": "20% (R 180.00)",
        "due": "Due in 4 days", "status": "Performing", "statusIcon": "bi-check-circle-fill", "statusClass": "success",
    },
    {
        "id": "#ADV-2026-851", "borrower": "Pieter van der Merwe", "principal": "R 500.00", "fee": "25% (R 125.00)",
        "due": "Overdue 6 days", "status": "Late", "statusIcon": "bi-exclamation-triangle-fill", "statusClass": "warning",
    },
    {
        "id": "#ADV-2026-810", "borrower": "Zanele Mokoena", "principal": "R 300.00", "fee": "30% (R 90.00)",
        "due": "Overdue 21 days", "status": "Defaulted", "statusIcon": "bi-x-octagon-fill", "statusClass": "danger",
    },
    {
        "id": "#ADV-2026-905", "borrower": "Kavesh Naidoo", "principal": "R 1,000.00", "fee": "15% (R 150.00)",
        "due": "Awaiting sign-off", "status": "Pending Approval", "statusIcon": "bi-hourglass-split", "statusClass": "secondary",
    },
]


def next_advance_id() -> str:
    return f"#ADV-2026-{random.randint(100, 999)}"


# ---------------------------------------------------------------------------
# KYC queue
# ---------------------------------------------------------------------------

kyc_queue: list[dict] = [
    {
        "key": "id_mock",
        "category": "South African ID Document",
        "fileName": "Sipho_Dlamini_SmartID.pdf",
        "status": "Verified",
        "type": "image",
        "url": "https://images.unsplash.com/photo-1554774853-aae0a22c8aa4?w=600&h=450&fit=crop",
    },
    {
        "key": "doc_mock",
        "category": "Proof of Residence",
        "fileName": "City_Power_Bill_May2026.pdf",
        "status": "Pending Review",
        "type": "pdf",
        "url": "",
    },
]


def next_kyc_key() -> str:
    return f"runtime_{int(time.time() * 1000)}"


# ---------------------------------------------------------------------------
# Billing (plans, payment methods, invoices)
# ---------------------------------------------------------------------------

billing: dict = {
    "admin": {
        "planName": "Growth Tier",
        "planPrice": "R 249/mo",
        "renewsOn": "August 15, 2026",
        "paymentMethods": [
            {
                "id": "pm_seed_admin_card", "type": "card", "brand": "Mastercard", "last4": "4892",
                "cardNumber": "5412750035478892", "cardholderName": "Sarah Jenkins", "expiry": "12/28",
                "debitDate": "1", "isPrimary": True,
            },
            {"id": "pm_seed_admin_paypal", "type": "paypal", "label": "PayPal (sarah.j@mampara.co.za)", "isPrimary": False},
        ],
        "invoices": [
            {"id": "#INV-2026-07", "date": "Jul 15, 2026", "amount": "R 249.00"},
            {"id": "#INV-2026-06", "date": "Jun 15, 2026", "amount": "R 249.00"},
            {"id": "#INV-2026-05", "date": "May 15, 2026", "amount": "R 249.00"},
        ],
    },
    "borrower": {
        "planName": "Standard Borrower Tier",
        "planPrice": "R 0/mo",
        "renewsOn": "No recurring platform fee",
        "paymentMethods": [
            {
                "id": "pm_seed_borrower_card", "type": "card", "brand": "Mastercard", "last4": "4892",
                "cardNumber": "5412750035478892", "cardholderName": "Sipho Dlamini", "expiry": "12/28",
                "debitDate": "25", "isPrimary": True,
            },
            {"id": "pm_seed_borrower_paypal", "type": "paypal", "label": "PayPal (linked account)", "isPrimary": False},
        ],
        "invoices": [
            {"id": "#ADV-2026-892", "date": "Jul 15, 2026", "amount": "R 97.50"},
            {"id": "#ADV-2026-760", "date": "Jun 18, 2026", "amount": "R 60.00"},
            {"id": "#ADV-2026-611", "date": "May 22, 2026", "amount": "R 45.00"},
        ],
    },
}


def next_payment_method_id() -> str:
    return f"pm_{int(time.time() * 1000)}"


def detect_card_brand(card_number: str) -> str:
    digits = "".join(ch for ch in str(card_number) if ch.isdigit())
    if digits.startswith("4"):
        return "Visa"
    if digits[:2] in {"51", "52", "53", "54", "55"}:
        return "Mastercard"
    if digits[:2] in {"34", "37"}:
        return "Amex"
    return "Card"


# ---------------------------------------------------------------------------
# Credit bureau
# ---------------------------------------------------------------------------

credit_bureau_result: dict = {
    "name": "Sipho Dlamini",
    "idNumber": "8805125890082",
    "riskLabel": "Low Risk",
    "score": 685,
    "scoreScaleLabel": "Scale: 0 - 999 (Good Standing)",
    "defaultJudgements": "None Recorded",
    "openFacilities": "2 Active Accounts (R 480 exposure)",
    "affordability": "Approved (R 350/pay-cycle headroom)",
    "recommendedMaxAdvance": "R 1,000.00",
}

# ---------------------------------------------------------------------------
# Platform settings
# ---------------------------------------------------------------------------

settings: dict = {"advanceFeePercent": 15}
