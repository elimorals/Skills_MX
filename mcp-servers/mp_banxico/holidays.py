"""Mexican bank holidays for business-day calculation.

Banxico does NOT publish TC on bank holidays. For CFDI, we need the last
business day's rate, so we have to skip Sat/Sun + Mexican feriados.

This is a curated calendar — fixed observances + approximated movable ones.
For absolute precision, integrate with workalendar or similar lib.

⚠ This list reflects training-time knowledge; verify against
https://www.banco.org.mx for the current year before production.
"""

from __future__ import annotations

from datetime import date


def _easter_sunday(year: int) -> date:
    """Compute Easter Sunday for a given year (Gregorian, Anonymous Gauss algo).

    Used to derive Holy Thursday & Good Friday, which are Banxico holidays.
    """
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def banxico_holidays(year: int) -> set[date]:
    """Return the set of Banxico bank holidays for a given year.

    Includes:
    - Fixed: Jan 1, Feb 1st-Monday (Constitución), Mar 3rd-Monday (Natalicio
      de Juárez), Sep 16 (Independencia), Nov 3rd-Monday (Revolución),
      Dec 12 (Guadalupe), Dec 25 (Navidad)
    - Easter: Holy Thursday + Good Friday
    """
    holidays: set[date] = set()

    holidays.add(date(year, 1, 1))  # Año Nuevo
    holidays.add(_nth_weekday(year, 2, 0, 1))  # 1er lunes de febrero
    holidays.add(_nth_weekday(year, 3, 0, 3))  # 3er lunes de marzo
    holidays.add(date(year, 9, 16))  # Independencia
    holidays.add(_nth_weekday(year, 11, 0, 3))  # 3er lunes de noviembre
    holidays.add(date(year, 12, 12))  # Día de la Virgen
    holidays.add(date(year, 12, 25))  # Navidad

    # Semana Santa: Jueves y Viernes Santo
    easter = _easter_sunday(year)
    from datetime import timedelta

    holidays.add(easter - timedelta(days=3))  # Jueves Santo
    holidays.add(easter - timedelta(days=2))  # Viernes Santo

    return holidays


def _nth_weekday(year: int, month: int, weekday: int, n: int) -> date:
    """Return the date of the n-th `weekday` in month/year.

    weekday: 0=Monday, 6=Sunday (matches date.weekday()).
    """
    first = date(year, month, 1)
    # How many days to add to reach the first occurrence of `weekday`
    offset = (weekday - first.weekday()) % 7
    day = 1 + offset + (n - 1) * 7
    return date(year, month, day)


def is_business_day(d: date) -> bool:
    """True if d is Mon-Fri AND not a Banxico holiday."""
    if d.weekday() >= 5:  # 5=Sat, 6=Sun
        return False
    return d not in banxico_holidays(d.year)


def previous_business_day(d: date) -> date:
    """Return the most recent business day strictly before `d`."""
    from datetime import timedelta

    candidate = d - timedelta(days=1)
    while not is_business_day(candidate):
        candidate -= timedelta(days=1)
    return candidate
