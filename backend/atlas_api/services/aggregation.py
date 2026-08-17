import math
import random
from datetime import date, datetime, time, timedelta

from django.utils import timezone

from .. import models
from .formatting import add_months, days_until, fmt_usd


def _sum(items, f):
    return sum(f(i) or 0 for i in items)


def _avg(items, f):
    return round(_sum(items, f) / len(items)) if items else 0


def _quarter_bounds(now):
    q_start_month = (now.month - 1) // 3 * 3 + 1
    q_start = date(now.year, q_start_month, 1)
    q_end = add_months(q_start, 3) - timedelta(days=1)
    return q_start, q_end


def _as_aware(d):
    return timezone.make_aware(datetime.combine(d, time.min))


def build_dashboard_v2():
    companies = list(models.Company.objects.all())
    tickets = list(models.Ticket.objects.exclude(status="Resolved"))

    managed_arr = _sum(companies, lambda c: c.arr)
    managed_mrr = _sum(companies, lambda c: c.mrr)
    portfolio_health = _avg(companies, lambda c: c.health)

    now = timezone.now()
    base_arr = managed_arr * 0.78
    months = []
    for i in range(11, -1, -1):
        d = add_months(date(now.year, now.month, 1), -i)
        t = (11 - i) / 11
        arr = round(base_arr * (1 + t * 0.28) + math.sin(i) * 15000)
        expansion = round(arr * 0.024 + random.random() * 5000)
        churn = round(arr * 0.011 + random.random() * 3000)
        contraction = round(arr * 0.007 + random.random() * 2000)
        renewal_rev = round(arr * 0.082)
        months.append({
            "month": d.strftime("%b"), "full": d.strftime("%Y-%m"),
            "arr": arr, "mrr": round(arr / 12), "expansion": expansion,
            "churn": churn, "contraction": contraction, "renewal_rev": renewal_rev,
        })

    start_arr = months[0]["arr"] or 1
    churn_total = _sum(months, lambda m: m["churn"])
    contraction_total = _sum(months, lambda m: m["contraction"])
    expansion_total = _sum(months, lambda m: m["expansion"])
    grr = round(((start_arr - churn_total - contraction_total) / start_arr) * 1000) / 10
    nrr = round(((start_arr - churn_total - contraction_total + expansion_total) / start_arr) * 1000) / 10

    q_start, q_end = _quarter_bounds(now.date())
    q_start_dt, q_end_dt = _as_aware(q_start), _as_aware(q_end) + timedelta(hours=23, minutes=59, seconds=59)
    quarter_progress = round(((now - q_start_dt).total_seconds() / (q_end_dt - q_start_dt).total_seconds()) * 100)

    expansion_goal = 1_200_000
    expansion_current = round(expansion_total / 4)
    expansion_attainment = round((expansion_current / expansion_goal) * 100)

    renewing_q = [c for c in companies if c.renewal_date and q_start_dt <= c.renewal_date <= q_end_dt]
    renewal_q_arr = _sum(renewing_q, lambda c: c.arr)
    renewal_confidence = _avg(renewing_q or companies, lambda c: c.atlas_confidence)

    outlook = "On Track" if portfolio_health >= 75 else "Watch" if portfolio_health >= 60 else "At Risk"

    kpis = [
        {"id": "arr", "label": "Managed ARR", "value": managed_arr, "fmt": "money", "trend": 4.2, "hint": "Sum of net annual recurring revenue across all managed accounts."},
        {"id": "mrr", "label": "Managed MRR", "value": managed_mrr, "fmt": "money", "trend": 3.6, "hint": "Monthly recurring revenue normalized from contracts."},
        {"id": "health", "label": "Portfolio Health", "value": portfolio_health, "fmt": "score", "trend": -2.1, "hint": "Average health score across portfolio."},
        {"id": "grr", "label": "Gross Revenue Retention", "value": grr, "fmt": "pct", "trend": 0.4, "hint": "Trailing 12m: (start − churn − contraction) / start."},
        {"id": "nrr", "label": "Net Revenue Retention", "value": nrr, "fmt": "pct", "trend": 1.8, "hint": "GRR + expansion. >100% = portfolio growing."},
        {"id": "qprog", "label": "Quarter Progress", "value": quarter_progress, "fmt": "pct", "trend": None, "hint": f"{quarter_progress}% through {q_start.strftime('%b')}–{q_end.strftime('%b')}."},
        {"id": "exp", "label": "Expansion Attainment", "value": expansion_attainment, "fmt": "pct", "trend": -11, "hint": f"{fmt_usd(expansion_current)} of {fmt_usd(expansion_goal)} quarterly goal."},
        {"id": "renf", "label": "Renewal Forecast", "value": renewal_confidence, "fmt": "pct", "trend": 0.9, "hint": f"{len(renewing_q)} renewals ({fmt_usd(renewal_q_arr)}) this quarter, weighted by Atlas confidence."},
        {"id": "outlook", "label": "Atlas Outlook", "value": outlook, "fmt": "text", "trend": None, "hint": "Composite of health, renewal pacing and pipeline confidence."},
    ]

    def company_card(c):
        return {"id": c.id, "name": c.name, "logo": c.logo, "health": c.health, "health_label": c.health_label, "arr": c.arr, "renewal_date": c.renewal_date}

    buckets = {
        "healthy": [c for c in companies if c.health >= 80],
        "needs_attention": [c for c in companies if 60 <= c.health < 80],
        "high_risk": [c for c in companies if c.health < 60],
        "expansion_ready": [c for c in companies if (c.current_opportunity or "") and c.health >= 70],
        "exec_escalation": [c for c in companies if "escalat" in (c.primary_risk or "").lower() or c.health < 50 or (c.outstanding_balance or 0) > 0],
        "upcoming_renewals": [c for c in companies if (days_until(c.renewal_date) or 999) <= 45],
    }
    heatmap = [
        {"key": k, "count": len(v), "arr": _sum(v, lambda c: c.arr), "companies": [company_card(c) for c in v]}
        for k, v in buckets.items()
    ]

    def group_by(items, key_fn):
        groups = {}
        for c in items:
            k = key_fn(c)
            g = groups.setdefault(k, {"key": k, "count": 0, "arr": 0})
            g["count"] += 1
            g["arr"] += c.arr
        return list(groups.values())

    seg_industry = group_by(companies, lambda c: c.industry)
    seg_plan = group_by(companies, lambda c: c.plan)
    seg_region = group_by(companies, lambda c: c.region)

    renewal_groups = {}
    for c in companies:
        key = c.renewal_date.strftime("%b %y")
        g = renewal_groups.setdefault(key, {"key": key, "count": 0, "arr": 0, "_sort": c.renewal_date})
        g["count"] += 1
        g["arr"] += c.arr
        g["_sort"] = min(g["_sort"], c.renewal_date)
    seg_renewal = [{"key": g["key"], "count": g["count"], "arr": g["arr"]} for g in sorted(renewal_groups.values(), key=lambda g: g["_sort"])]

    seg_health = [
        {"key": "80–100", "count": len(buckets["healthy"]), "arr": _sum(buckets["healthy"], lambda c: c.arr)},
        {"key": "60–79", "count": len(buckets["needs_attention"]), "arr": _sum(buckets["needs_attention"], lambda c: c.arr)},
        {"key": "<60", "count": len(buckets["high_risk"]), "arr": _sum(buckets["high_risk"], lambda c: c.arr)},
    ]

    attention = []
    at_risk_renewals = sorted(
        [c for c in companies if (days_until(c.renewal_date) or 999) <= 30 and c.atlas_confidence < 85],
        key=lambda c: days_until(c.renewal_date),
    )
    for c in at_risk_renewals[:2]:
        attention.append({
            "kind": "renewal_risk", "tone": "rose", "icon": "🔥",
            "company": {"id": c.id, "name": c.name, "logo": c.logo, "arr": c.arr},
            "headline": f"{fmt_usd(c.arr)} Renewal", "subline": f"{days_until(c.renewal_date)} days remaining",
            "meta": f"Atlas confidence {c.atlas_confidence}%", "action": "Executive meeting recommended",
        })
    for c in [c for c in companies if c.health < 50 or (c.outstanding_balance or 0) > 0][:1]:
        open_count = len([t for t in tickets if t.company_id == c.id])
        attention.append({
            "kind": "escalation", "tone": "amber", "icon": "🟡",
            "company": {"id": c.id, "name": c.name, "logo": c.logo, "arr": c.arr},
            "headline": "Executive escalation", "subline": f"{open_count} open tickets · {fmt_usd(c.outstanding_balance or 0)} overdue",
            "meta": c.primary_risk, "action": "Schedule exec review",
        })
    for c in [c for c in companies if c.health >= 80 and (c.current_opportunity or "")][:2]:
        attention.append({
            "kind": "expansion", "tone": "emerald", "icon": "🟢",
            "company": {"id": c.id, "name": c.name, "logo": c.logo, "arr": c.arr},
            "headline": "Expansion opportunity", "subline": c.current_opportunity,
            "meta": f"Atlas confidence {c.atlas_confidence}%", "action": "Ready for proposal",
        })

    exec_metrics = [
        {"label": "Avg Health Score", "value": portfolio_health, "fmt": "score", "trend": -2.1},
        {"label": "Avg CSAT", "value": 4.4, "fmt": "rating", "trend": 0.1},
        {"label": "Avg Product Adoption", "value": _avg(companies, lambda c: round((c.seats_used / c.seats_purchased) * 100) if c.seats_purchased else 0), "fmt": "pct", "trend": 1.2},
        {"label": "Avg Exec Engagement", "value": 62, "fmt": "pct", "trend": -14},
        {"label": "Avg Renewal Confidence", "value": _avg(companies, lambda c: c.atlas_confidence), "fmt": "pct", "trend": 0.9},
        {"label": "Avg Response Time", "value": 3.2, "fmt": "hours", "trend": -0.4},
        {"label": "Avg Time to Value", "value": 18, "fmt": "days", "trend": -3},
        {"label": "Avg Usage Growth", "value": 8.1, "fmt": "pct", "trend": 2.3},
    ]

    def hours_ago(h):
        return (now - timedelta(hours=h)).isoformat()

    portfolio_timeline = sorted([
        {"kind": "renewal_closed", "icon": "✅", "tone": "emerald", "title": "Largest renewal closed", "detail": "Initech renewed Business plan for $180k", "when": hours_ago(7 * 24)},
        {"kind": "churn_risk", "icon": "⚠️", "tone": "rose", "title": "Biggest churn risk surfaced", "detail": "Globex champion departed; 3 P1 tickets open", "when": hours_ago(14 * 24)},
        {"kind": "sponsor_change", "icon": "👤", "tone": "amber", "title": "Executive sponsor changed", "detail": "Hooli CIO replaced; relationship cold", "when": hours_ago(42 * 24)},
        {"kind": "health_spike", "icon": "📈", "tone": "emerald", "title": "Health score spike", "detail": "Acme rose +12 after workflow launch", "when": hours_ago(21 * 24)},
        {"kind": "adoption_jump", "icon": "🚀", "tone": "indigo", "title": "Major adoption increase", "detail": "Umbrella AI Agents adoption +22 over 60d", "when": hours_ago(35 * 24)},
    ], key=lambda e: e["when"], reverse=True)

    adoption_pct = _avg(companies, lambda c: round((c.seats_used / c.seats_purchased) * 100) if c.seats_purchased else 0)
    goals = [
        {"id": "expansion", "label": "Expansion (Q)", "target": expansion_goal, "current": expansion_current, "fmt": "money",
         "pacing": expansion_attainment - quarter_progress,
         "explainer": "Ahead of pacing — keep momentum on Acme & Umbrella expansion." if expansion_attainment - quarter_progress >= 0 else f"{abs(expansion_attainment - quarter_progress)}% behind pacing. Acme + Umbrella deals must close in the next 30 days."},
        {"id": "renewal", "label": "Renewal (Q)", "target": renewal_q_arr, "current": round(renewal_q_arr * (renewal_confidence / 100)), "fmt": "money",
         "pacing": renewal_confidence - 90,
         "explainer": f"{len(renewing_q)} renewals in this quarter; weighted forecast at {renewal_confidence}%. " + ("Hooli is the swing factor." if renewal_confidence < 85 else "Tracking strong.")},
        {"id": "health", "label": "Avg Health", "target": 80, "current": portfolio_health, "fmt": "score",
         "pacing": portfolio_health - 80,
         "explainer": "On target." if portfolio_health >= 80 else "Globex (34) and Umbrella (55) are dragging the average. Recovery on both adds ~9 points."},
        {"id": "adoption", "label": "Adoption %", "target": 75, "current": adoption_pct, "fmt": "pct", "pacing": 0,
         "explainer": "Seat utilization across all accounts. Hooli reorg + Globex departure are the two pulls."},
    ]

    sources_used = ["Salesforce", "Stripe", "Chargebee", "Zendesk", "Mixpanel", "Amplitude", "Slack", "Meeting Notes"]

    return {
        "greeting": {"user": "Subash"},
        "kpis": kpis,
        "revenue_chart": months,
        "goals": goals,
        "heatmap": heatmap,
        "segments": {"industry": seg_industry, "plan": seg_plan, "region": seg_region, "renewal": seg_renewal, "health": seg_health},
        "exec_metrics": exec_metrics,
        "portfolio_timeline": portfolio_timeline,
        "attention": attention,
        "renewing_quarter": {"count": len(renewing_q), "arr": renewal_q_arr},
        "sources_used": sources_used,
    }


def build_dashboard_legacy():
    companies = list(models.Company.objects.all())
    meetings_all = list(models.Meeting.objects.order_by("scheduled_at"))
    now = timezone.now()
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = now.replace(hour=23, minute=59, second=59, microsecond=999000)
    todays = [m for m in meetings_all if start <= m.scheduled_at <= end]
    upcoming = [m for m in meetings_all if m.scheduled_at > end][:5]
    high_risk = sorted([c for c in companies if c.health < 70], key=lambda c: c.health)
    emails = list(models.EmailMessage.objects.order_by("-timestamp")[:8])
    tickets = list(models.Ticket.objects.exclude(status="Resolved").order_by("-opened")[:8])
    comp_map = {c.id: c for c in companies}

    def company_brief(c):
        if not c:
            return None
        return {"id": c.id, "name": c.name, "logo": c.logo, "health": c.health, "health_label": c.health_label}

    def meeting_dict(m):
        return {
            "id": m.id, "company_id": m.company_id, "title": m.title, "attendees": m.attendees,
            "scheduled_at": m.scheduled_at.isoformat(), "duration_min": m.duration_min, "type": m.type,
            "location": m.location, "company": company_brief(comp_map.get(m.company_id)),
        }

    today_meetings = [meeting_dict(m) for m in todays]
    upcoming_meetings = [meeting_dict(m) for m in upcoming]

    recent_activity = sorted(
        [
            {"type": "email", "title": f"Email from {e.from_name}", "detail": e.subject, "at": e.timestamp.isoformat(), "company": company_brief(comp_map.get(e.company_id))}
            for e in list(emails)[:5]
        ] + [
            {"type": "ticket", "title": f"{t.priority} • {t.subject}", "detail": t.status, "at": t.opened.isoformat(), "company": company_brief(comp_map.get(t.company_id))}
            for t in list(tickets)[:3]
        ],
        key=lambda a: a["at"], reverse=True,
    )[:8]

    return {
        "todayMeetings": today_meetings,
        "upcomingMeetings": upcoming_meetings,
        "highRisk": [{"id": c.id, "name": c.name, "logo": c.logo, "health": c.health, "health_label": c.health_label, "arr": c.arr} for c in high_risk],
        "recentActivity": recent_activity,
        "totals": {"companies": len(companies), "openTickets": len(tickets)},
    }
