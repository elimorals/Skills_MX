import os

import pytest


def pytest_collection_modifyitems(config, items):
    # Tests @pytest.mark.live golpean el upstream real: solo con PLUGINS_MX_LIVE=1.
    if os.environ.get("PLUGINS_MX_LIVE") == "1":
        return
    skip = pytest.mark.skip(reason="test live: exporta PLUGINS_MX_LIVE=1")
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip)
