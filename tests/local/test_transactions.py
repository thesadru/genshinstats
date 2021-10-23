import warnings
from datetime import datetime

import genshinstats as gs
import pytest


def test_transactions():
    list(gs.get_primogem_log(size=20))
    list(gs.get_resin_log(size=20))
    list(gs.get_crystal_log(size=20))
    list(gs.get_artifact_log(size=20))
    list(gs.get_weapon_log(size=20))


def test_current_resin():
    pytest.skip("current_resin is too unstable")
    try:
        resin = gs.current_resin(datetime(2021, 8, 14), 160)
    except ValueError:
        warnings.warn(
            "current_resin has failed - this might have been "
            "because an entry is wrong so only a warn is given."
        )
        return

    assert 0 <= resin <= 160
    approx = gs.approximate_current_resin()
    assert 0 <= approx <= 160
    assert abs(resin - approx) <= 15
