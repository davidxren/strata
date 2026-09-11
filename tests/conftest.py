import os

from hypothesis import settings

BASE = settings.get_profile("default")

settings.register_profile(
    "dev", parent=BASE, max_examples=200, derandomize=False, deadline=None, print_blob=True
)
settings.register_profile(
    "ci", parent=BASE, max_examples=1000, derandomize=False, deadline=None, print_blob=True
)
settings.load_profile(os.environ.get("HYPOTHESIS_PROFILE", "dev"))
