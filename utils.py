import random
import time
from datetime import date


def make_token(user_id: str) -> str:
    return f"mampara.{user_id}.{random.randint(10 ** 9, 10 ** 10 - 1):x}"


def next_advance_id() -> str:
    return f"#ADV-{date.today().year}-{random.randint(100, 999)}"


def format_due_text(due_date: date | None) -> str:
    """Renders an advance's dueDate relative to today, so it stays accurate
    on every request instead of freezing whatever text was true at creation."""
    if due_date is None:
        return ""
    delta = (due_date - date.today()).days
    if delta > 0:
        return f"Due in {delta} day{'s' if delta != 1 else ''}"
    if delta == 0:
        return "Due today"
    overdue = abs(delta)
    return f"Overdue {overdue} day{'s' if overdue != 1 else ''}"


def format_calendar_date(d: date) -> str:
    """'August 15, 2026' — avoids the platform-specific %-d / %#d strftime
    flags needed to drop a leading zero from the day."""
    return f"{d.strftime('%B')} {d.day}, {d.year}"




def parse_currency(value: str) -> float:
    """'R 1,000.00' -> 1000.0 — reverses the display formatting stored on
    Advance.principal so it can be re-aggregated for dashboard KPIs."""
    cleaned = value.replace("R", "").replace(",", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def format_rand_whole(value: float) -> str:
    return f"R {round(value):,}"


def percent_change(old: float, new: float) -> float | None:
    """None when there's no meaningful baseline to compare against (old==0)
    rather than returning a nonsensical or infinite percentage."""
    if old == 0:
        return None
    return (new - old) / old * 100


def next_kyc_key() -> str:
    return f"runtime_{int(time.time() * 1000)}"


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
