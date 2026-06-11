"""Tests for Mexican banking holidays calculation."""

from __future__ import annotations

from datetime import date

import pytest

from mp_banxico.holidays import (
    banxico_holidays,
    is_business_day,
    previous_business_day,
)


# ---------- fixed holidays ----------


def test_new_year_is_holiday() -> None:
    assert date(2026, 1, 1) in banxico_holidays(2026)


def test_independence_day_is_holiday() -> None:
    assert date(2026, 9, 16) in banxico_holidays(2026)


def test_guadalupe_is_holiday() -> None:
    assert date(2026, 12, 12) in banxico_holidays(2026)


def test_christmas_is_holiday() -> None:
    assert date(2026, 12, 25) in banxico_holidays(2026)


# ---------- movable holidays ----------


def test_constitucion_is_first_monday_february() -> None:
    # 2026: 1er lunes febrero = lunes 2 feb
    holidays_2026 = banxico_holidays(2026)
    assert date(2026, 2, 2) in holidays_2026


def test_juarez_is_third_monday_march() -> None:
    # 2026: 3er lunes marzo = lunes 16 mar
    holidays_2026 = banxico_holidays(2026)
    assert date(2026, 3, 16) in holidays_2026


def test_revolucion_is_third_monday_november() -> None:
    # 2026: 3er lunes nov = lunes 16 nov
    holidays_2026 = banxico_holidays(2026)
    assert date(2026, 11, 16) in holidays_2026


# ---------- easter-based holidays ----------


def test_easter_holidays_in_2026() -> None:
    # Easter 2026 = April 5 → Holy Thursday Apr 2, Good Friday Apr 3
    holidays = banxico_holidays(2026)
    assert date(2026, 4, 2) in holidays  # Jueves Santo
    assert date(2026, 4, 3) in holidays  # Viernes Santo


def test_easter_holidays_in_2025() -> None:
    # Easter 2025 = April 20 → Holy Thursday Apr 17, Good Friday Apr 18
    holidays = banxico_holidays(2025)
    assert date(2025, 4, 17) in holidays
    assert date(2025, 4, 18) in holidays


# ---------- business day logic ----------


def test_monday_is_business_day_when_not_holiday() -> None:
    # Monday Feb 16, 2026 — not the constitution holiday (which is Feb 2)
    assert is_business_day(date(2026, 2, 16)) is True


def test_saturday_is_not_business_day() -> None:
    assert is_business_day(date(2026, 2, 7)) is False  # Saturday


def test_sunday_is_not_business_day() -> None:
    assert is_business_day(date(2026, 2, 8)) is False  # Sunday


def test_holiday_is_not_business_day() -> None:
    assert is_business_day(date(2026, 1, 1)) is False
    assert is_business_day(date(2026, 9, 16)) is False


def test_previous_business_day_from_monday() -> None:
    # Monday Feb 16, 2026 → Friday Feb 13, 2026
    assert previous_business_day(date(2026, 2, 16)) == date(2026, 2, 13)


def test_previous_business_day_from_saturday() -> None:
    # Saturday Feb 14, 2026 → Friday Feb 13
    assert previous_business_day(date(2026, 2, 14)) == date(2026, 2, 13)


def test_previous_business_day_skips_holiday() -> None:
    # Tuesday Feb 3, 2026 → previous business day = Friday Jan 30
    # because Monday Feb 2 is Constitución
    assert previous_business_day(date(2026, 2, 3)) == date(2026, 1, 30)


def test_previous_business_day_chain_through_new_year() -> None:
    # Friday Jan 2, 2026 → previous business day = Wednesday Dec 31, 2025
    # because Jan 1 is holiday
    assert previous_business_day(date(2026, 1, 2)) == date(2025, 12, 31)


def test_previous_business_day_is_strictly_before() -> None:
    # The function returns the day BEFORE its input — never the input itself
    # even when input is a business day
    monday = date(2026, 2, 16)
    prev = previous_business_day(monday)
    assert prev < monday
