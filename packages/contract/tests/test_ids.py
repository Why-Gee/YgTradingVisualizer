from datetime import UTC, datetime, timedelta, timezone

from ygperf.ids import run_id_for


def test_run_id_is_deterministic_and_short():
    ts = datetime(2026, 6, 3, 12, 0, tzinfo=UTC)
    a = run_id_for("deadbeef", "meta_allocation_portfolio", ts)
    b = run_id_for("deadbeef", "meta_allocation_portfolio", ts)
    c = run_id_for("deadbeef", "number_robustness", ts)
    assert a == b  # deterministic
    assert a != c  # varies by eval
    assert len(a) == 16
    assert a.isalnum()


def test_run_id_is_tz_stable():
    ts_utc = datetime(2026, 6, 3, 12, 0, tzinfo=UTC)
    tz_plus3 = timezone(timedelta(hours=3))
    ts_plus3 = datetime(2026, 6, 3, 15, 0, tzinfo=tz_plus3)
    assert run_id_for("deadbeef", "meta_allocation_portfolio", ts_utc) == run_id_for(
        "deadbeef", "meta_allocation_portfolio", ts_plus3
    )
