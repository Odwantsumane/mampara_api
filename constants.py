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
