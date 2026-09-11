import os

from hypothesis import settings

import strata

PROFILE_EXAMPLES = {"dev": 200, "ci": 1000}


def test_smoke() -> None:
    assert strata.__name__ == "strata"
    profile = os.environ.get("HYPOTHESIS_PROFILE", "dev")
    assert settings().max_examples == PROFILE_EXAMPLES[profile]
