from django.utils import timezone


def fmt_usd(n):
    if not n:
        return "$0"
    abs_n = abs(n)
    if abs_n >= 1_000_000:
        return f"${n / 1_000_000:.2f}M"
    if abs_n >= 1_000:
        return f"${n / 1000:.0f}k"
    return f"${n:,.0f}"


def days_until(dt):
    if dt is None:
        return None
    now = timezone.now()
    delta = dt - now
    return round(delta.total_seconds() / 86400)


def add_months(base_date, months_delta):
    month_index = base_date.month - 1 + months_delta
    year = base_date.year + month_index // 12
    month = month_index % 12 + 1
    return base_date.replace(year=year, month=month, day=1)
