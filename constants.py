"""External service URLs, kept in one place so they're easy to find and swap."""

import os

# Credit bureau lookup endpoint used by crud/credit_bureau.py::run_bureau_lookup.
# Defaults to this API's own mock bureau route (routers/credit_bureau.py
# ::mock_bureau_lookup) so credit checks work out of the box in dev/demo.
# Point this at a real bureau (TransUnion/XDS/Compuscan/etc.) via the
# CREDIT_BUREAU_API_URL env var once real credentials are available — a real
# bureau will likely need its own auth headers and may return a different
# response shape, which run_bureau_lookup() would need to adapt to.
CREDIT_BUREAU_API_URL = os.environ.get(
    "CREDIT_BUREAU_API_URL", "http://localhost:8000/api/credit-bureau/mock-lookup"
)

# Paystack payment gateway. Defaults to this API's own mock gateway routes
# (routers/payments.py's "/mock-paystack/..." endpoints) so advance repayment
# works out of the box in dev/demo. Point PAYSTACK_BASE_URL at Paystack's real
# API (https://api.paystack.co) and set real PAYSTACK_SECRET_KEY /
# PAYSTACK_PUBLIC_KEY env vars once you have a real Paystack account —
# request/response shapes already mirror Paystack's actual API.
PAYSTACK_BASE_URL = os.environ.get("PAYSTACK_BASE_URL", "http://localhost:8000/api/payments/mock-paystack")
PAYSTACK_SECRET_KEY = os.environ.get("PAYSTACK_SECRET_KEY", "sk_test_mock_not_a_real_key")
PAYSTACK_PUBLIC_KEY = os.environ.get("PAYSTACK_PUBLIC_KEY", "pk_test_mock_not_a_real_key")
# Where the gateway redirects the browser back to after checkout completes.
PAYSTACK_CALLBACK_URL = os.environ.get("PAYSTACK_CALLBACK_URL", "http://localhost:5173")
