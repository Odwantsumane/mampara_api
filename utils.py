import random
import time


def make_token(user_id: str) -> str:
    return f"mampara.{user_id}.{random.randint(10 ** 9, 10 ** 10 - 1):x}"


def next_advance_id() -> str:
    return f"#ADV-2026-{random.randint(100, 999)}"


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
