from datetime import datetime, timezone

from ygperf.ids import run_id_for


def test_run_id_is_deterministic_and_short():
    ts = datetime(2026, 6, 3, 12, 0, tzinfo=timezone.utc)
    a = run_id_for("deadbeef", "meta_allocation_portfolio", ts)
    b = run_id_for("deadbeef", "meta_allocation_portfolio", ts)
    c = run_id_for("deadbeef", "number_robustness", ts)
    assert a == b  # deterministic
    assert a != c  # varies by eval
    assert len(a) == 16 and a.isalnum()
