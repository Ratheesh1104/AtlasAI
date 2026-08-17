"""Demo/mock data builders — a straight port of the seed data that used to
live in app/api/[[...path]]/route.js. Pure functions, no DB access, so they're
easy to unit test and reuse from the seed_atlas management command.
"""
import math
import random
from datetime import date, timedelta

from django.utils import timezone


def days_from_now(d):
    return timezone.now() + timedelta(days=d)


def hours_ago(h):
    return timezone.now() - timedelta(hours=h)


def build_companies():
    return [
        {
            "id": "co-acme", "name": "Acme Corp", "industry": "SaaS Analytics", "logo": "AC",
            "arr": 240000, "plan": "Enterprise", "employees": 1200, "region": "North America",
            "csm": "You", "health": 87, "health_label": "Healthy", "health_trend": "+4",
            "renewal_date": days_from_now(45), "renewal_status": "On Track",
            "product_usage_summary": "Daily active usage up 18% QoQ. Strong adoption of Dashboards and Alerts modules. Recently enabled SSO and SCIM for two new business units.",
            "strategic_notes": "Champion: Sarah Chen (VP Data). Expansion path into Marketing org identified.",
        },
        {
            "id": "co-hooli", "name": "Hooli", "industry": "Technology", "logo": "HO",
            "arr": 1200000, "plan": "Enterprise Plus", "employees": 9500, "region": "Global",
            "csm": "You", "health": 62, "health_label": "Watch", "health_trend": "-6",
            "renewal_date": days_from_now(18), "renewal_status": "At Risk",
            "product_usage_summary": "Seat utilization 71% (down from 84%). Two power-user teams paused workflows during recent reorg. API usage stable.",
            "strategic_notes": "New CIO Gavin Belson reviewing all vendor spend. Multi-thread to procurement and finance ASAP.",
        },
        {
            "id": "co-globex", "name": "Globex Inc", "industry": "Manufacturing", "logo": "GL",
            "arr": 450000, "plan": "Business", "employees": 3400, "region": "EMEA",
            "csm": "You", "health": 34, "health_label": "High Risk", "health_trend": "-22",
            "renewal_date": days_from_now(12), "renewal_status": "High Risk",
            "product_usage_summary": "Active users dropped 41% over 60 days. Critical integration to SAP failing intermittently. 3 P1 tickets open.",
            "strategic_notes": "Champion left the company (Jacques Pernod). New stakeholder unidentified. Executive sponsor escalation required.",
        },
        {
            "id": "co-initech", "name": "Initech", "industry": "Financial Services", "logo": "IN",
            "arr": 180000, "plan": "Business", "employees": 800, "region": "North America",
            "csm": "You", "health": 91, "health_label": "Healthy", "health_trend": "+2",
            "renewal_date": days_from_now(90), "renewal_status": "On Track",
            "product_usage_summary": "Power users across Finance team. NPS 9 from last survey. Asked about advanced compliance reporting (potential upsell).",
            "strategic_notes": "Bill Lumbergh is exec sponsor. Strong reference customer; willing to do case study.",
        },
        {
            "id": "co-umbrella", "name": "Umbrella Corp", "industry": "Pharmaceuticals", "logo": "UM",
            "arr": 680000, "plan": "Enterprise", "employees": 5200, "region": "Global",
            "csm": "You", "health": 55, "health_label": "Watch", "health_trend": "-3",
            "renewal_date": days_from_now(30), "renewal_status": "Watch",
            "product_usage_summary": "Compliance module under review. Security team raised SOC2 documentation request. Usage in R&D team excellent.",
            "strategic_notes": "Albert Wesker is decision maker but rarely available. CISO Ada Wong is gatekeeper for security review.",
        },
    ]


def build_contacts():
    return [
        {"id": "ct-1", "company_id": "co-acme", "name": "Sarah Chen", "title": "VP Data", "email": "sarah.chen@acme.com", "role": "Champion"},
        {"id": "ct-2", "company_id": "co-acme", "name": "Marcus Webb", "title": "Director of Analytics", "email": "marcus@acme.com", "role": "User"},
        {"id": "ct-3", "company_id": "co-hooli", "name": "Gavin Belson", "title": "CIO", "email": "gavin@hooli.com", "role": "Economic Buyer"},
        {"id": "ct-4", "company_id": "co-hooli", "name": "Jared Dunn", "title": "COO", "email": "jared@hooli.com", "role": "Champion"},
        {"id": "ct-5", "company_id": "co-hooli", "name": "Monica Hall", "title": "VP Procurement", "email": "monica@hooli.com", "role": "Procurement"},
        {"id": "ct-6", "company_id": "co-globex", "name": "Marie Laurent", "title": "Head of IT", "email": "m.laurent@globex.eu", "role": "New Stakeholder"},
        {"id": "ct-7", "company_id": "co-globex", "name": "Hans Gruber", "title": "CTO", "email": "h.gruber@globex.eu", "role": "Decision Maker"},
        {"id": "ct-8", "company_id": "co-initech", "name": "Bill Lumbergh", "title": "VP Finance", "email": "bill@initech.com", "role": "Exec Sponsor"},
        {"id": "ct-9", "company_id": "co-initech", "name": "Peter Gibbons", "title": "Senior Analyst", "email": "peter@initech.com", "role": "Power User"},
        {"id": "ct-10", "company_id": "co-umbrella", "name": "Albert Wesker", "title": "Chief Research Officer", "email": "a.wesker@umbrella.com", "role": "Decision Maker"},
        {"id": "ct-11", "company_id": "co-umbrella", "name": "Ada Wong", "title": "CISO", "email": "a.wong@umbrella.com", "role": "Security Gatekeeper"},
    ]


def build_emails():
    return [
        {"id": "em-1", "company_id": "co-acme", "from_name": "Sarah Chen", "subject": "Re: Q3 expansion proposal", "snippet": "This looks great. Can we get Marketing team access by mid-month? We want to pilot dashboards with them.", "sentiment": "positive", "timestamp": hours_ago(20)},
        {"id": "em-2", "company_id": "co-acme", "from_name": "Marcus Webb", "subject": "Alert config question", "snippet": "How do I configure thresholds for the new revenue alert? Our previous setup did not migrate cleanly.", "sentiment": "neutral", "timestamp": hours_ago(46)},
        {"id": "em-3", "company_id": "co-acme", "from_name": "Sarah Chen", "subject": "Thanks for the demo", "snippet": "The team loved the workflow automation walkthrough. Sending you our use cases by Friday.", "sentiment": "positive", "timestamp": hours_ago(72)},

        {"id": "em-4", "company_id": "co-hooli", "from_name": "Gavin Belson", "subject": "Vendor consolidation review", "snippet": "As part of our vendor consolidation, I need full ROI breakdown by EOW. Schedule with my EA.", "sentiment": "tense", "timestamp": hours_ago(8)},
        {"id": "em-5", "company_id": "co-hooli", "from_name": "Monica Hall", "subject": "Procurement docs needed", "snippet": "Need updated MSA, SOC2, and pricing tiers. We are reviewing 9 vendors this quarter.", "sentiment": "neutral", "timestamp": hours_ago(28)},
        {"id": "em-6", "company_id": "co-hooli", "from_name": "Jared Dunn", "subject": "Re: workflow paused", "snippet": "Yes we paused the data ops workflow during the reorg. Should resume in 2 weeks once new team is staffed.", "sentiment": "neutral", "timestamp": hours_ago(50)},

        {"id": "em-7", "company_id": "co-globex", "from_name": "Marie Laurent", "subject": "SAP integration broken AGAIN", "snippet": "This is the 3rd outage this month. We cannot run month-end close. Need escalation.", "sentiment": "angry", "timestamp": hours_ago(4)},
        {"id": "em-8", "company_id": "co-globex", "from_name": "Hans Gruber", "subject": "Renewal conversation", "snippet": "Before we discuss renewal, I need to see a remediation plan for the SAP issues. We are evaluating alternatives.", "sentiment": "negative", "timestamp": hours_ago(30)},
        {"id": "em-9", "company_id": "co-globex", "from_name": "Marie Laurent", "subject": "Jacques transition", "snippet": "FYI Jacques left last week. I am now your primary contact but I am still ramping up.", "sentiment": "neutral", "timestamp": hours_ago(120)},

        {"id": "em-10", "company_id": "co-initech", "from_name": "Bill Lumbergh", "subject": "Reference call - yeahhh", "snippet": "Yeah, if you could go ahead and use us as a reference for the financial vertical, that would be greatttt.", "sentiment": "positive", "timestamp": hours_ago(36)},
        {"id": "em-11", "company_id": "co-initech", "from_name": "Peter Gibbons", "subject": "Compliance reporting feature", "snippet": "Loving the new module. Quick q: does it cover SOX 404 attestation workflows?", "sentiment": "positive", "timestamp": hours_ago(60)},

        {"id": "em-12", "company_id": "co-umbrella", "from_name": "Ada Wong", "subject": "SOC2 Type II report", "snippet": "Please send the latest SOC2 Type II report and your subprocessor list. Required before we sign renewal.", "sentiment": "neutral", "timestamp": hours_ago(12)},
        {"id": "em-13", "company_id": "co-umbrella", "from_name": "Albert Wesker", "subject": "R&D expansion", "snippet": "My R&D team wants to expand seats from 40 to 75. Send updated quote.", "sentiment": "positive", "timestamp": hours_ago(54)},
    ]


def build_tickets():
    return [
        {"id": "tk-1", "company_id": "co-acme", "subject": "Alert thresholds not migrating", "priority": "P3", "status": "Open", "opened": hours_ago(46)},
        {"id": "tk-2", "company_id": "co-hooli", "subject": "SSO claim mapping for new IdP", "priority": "P2", "status": "Open", "opened": hours_ago(40)},
        {"id": "tk-3", "company_id": "co-hooli", "subject": "API rate limit increase", "priority": "P3", "status": "Resolved", "opened": hours_ago(96)},
        {"id": "tk-4", "company_id": "co-globex", "subject": "SAP integration timeout (CRITICAL)", "priority": "P1", "status": "Open", "opened": hours_ago(6)},
        {"id": "tk-5", "company_id": "co-globex", "subject": "Data export failing for FR region", "priority": "P1", "status": "Open", "opened": hours_ago(38)},
        {"id": "tk-6", "company_id": "co-globex", "subject": "Bulk user provisioning broken", "priority": "P2", "status": "Open", "opened": hours_ago(72)},
        {"id": "tk-7", "company_id": "co-initech", "subject": "Feature request: SOX attestation", "priority": "P4", "status": "Triaged", "opened": hours_ago(60)},
        {"id": "tk-8", "company_id": "co-umbrella", "subject": "SOC2 doc request", "priority": "P3", "status": "In Progress", "opened": hours_ago(12)},
        {"id": "tk-9", "company_id": "co-umbrella", "subject": "GxP validation evidence", "priority": "P2", "status": "In Progress", "opened": hours_ago(72)},
    ]


def build_notes():
    return [
        {"id": "nt-1", "company_id": "co-acme", "author": "You", "body": "Sarah confirmed expansion into Marketing. Aiming for $80k uplift at renewal.", "timestamp": hours_ago(96)},
        {"id": "nt-2", "company_id": "co-hooli", "author": "You", "body": "Gavin replaced previous CIO 6 weeks ago. He is skeptical of all current vendors. Jared is our last warm contact.", "timestamp": hours_ago(140)},
        {"id": "nt-3", "company_id": "co-globex", "author": "You", "body": "Champion (Jacques) departed. Need to identify new champion fast. Marie is friendly but not influential.", "timestamp": hours_ago(110)},
        {"id": "nt-4", "company_id": "co-initech", "author": "You", "body": "Excellent fit. Bill agreed to reference call. Filed case study request with marketing.", "timestamp": hours_ago(70)},
        {"id": "nt-5", "company_id": "co-umbrella", "author": "You", "body": "Ada is meticulous on security. Once she signs off, Wesker will move quickly on the expansion.", "timestamp": hours_ago(80)},
    ]


def build_meetings():
    today = timezone.now().replace(hour=10, minute=0, second=0, microsecond=0)
    return [
        {"id": "mt-1", "company_id": "co-hooli", "title": "Hooli — Renewal kickoff with Gavin", "attendees": ["Gavin Belson", "Jared Dunn", "You"], "scheduled_at": today + timedelta(hours=2), "duration_min": 45, "type": "Renewal", "location": "Zoom"},
        {"id": "mt-2", "company_id": "co-globex", "title": "Globex — Escalation review", "attendees": ["Hans Gruber", "Marie Laurent", "You", "VP CS"], "scheduled_at": today + timedelta(hours=5), "duration_min": 30, "type": "Escalation", "location": "Google Meet"},
        {"id": "mt-3", "company_id": "co-acme", "title": "Acme — Q3 expansion working session", "attendees": ["Sarah Chen", "Marcus Webb", "You"], "scheduled_at": today + timedelta(hours=24), "duration_min": 60, "type": "Expansion", "location": "Zoom"},
        {"id": "mt-4", "company_id": "co-umbrella", "title": "Umbrella — Security review with Ada", "attendees": ["Ada Wong", "You"], "scheduled_at": today + timedelta(hours=26), "duration_min": 30, "type": "Security", "location": "Zoom"},
        {"id": "mt-5", "company_id": "co-initech", "title": "Initech — Quarterly business review", "attendees": ["Bill Lumbergh", "Peter Gibbons", "You"], "scheduled_at": today + timedelta(hours=50), "duration_min": 60, "type": "QBR", "location": "Zoom"},
    ]


def gen_trend(baseline, variance, length=30):
    arr = []
    for i in range(length, -1, -1):
        v = max(0, round(baseline + (math.sin(i / 3) + random.random() - 0.5) * variance))
        d = (timezone.now() - timedelta(days=i)).date().isoformat()
        arr.append({"date": d, "dau": v})
    return arr


def build_enrichments():
    return {
        "co-acme": {
            "mrr": 20000, "list_price": 264000, "discount": 9, "net_price": 240000,
            "billing_frequency": "Annual", "payment_terms": "Net 30",
            "contract_start": date(2023, 8, 15), "last_renewal_date": date(2025, 8, 15), "customer_since": date(2021, 8, 15),
            "contract_pdf_url": "/contracts/acme-msa-2025.pdf",
            "partner": None, "partner_margin": 0, "outstanding_balance": 0,
            "champion": "Sarah Chen — VP Data",
            "exec_sponsor": "James Whitfield — Chief Data Officer",
            "decision_makers": ["Sarah Chen (VP Data)", "James Whitfield (CDO)", "Lisa Park (VP Finance)"],
            "primary_risk": "Marketing pilot must succeed by Aug 15 to lock the $80k expansion",
            "current_opportunity": "Marketing dept expansion (+$80k ARR, verbal commit from Sarah)",
            "atlas_executive_summary": "Acme is a healthy, expanding account. Strong champion. Verbal commitment for Marketing expansion at renewal. Watch the SSO alert-config issue (P3). Plan: launch Marketing pilot by Jul 15 to lock the upsell.",
            "atlas_confidence": 92,
            "purchased_products": ["Analytics Core", "Workflow Automation", "SSO/SCIM"],
            "seats_purchased": 200, "seats_used": 176,
            "dau": 142, "wau": 188, "mau": 196,
            "feature_adoption": [
                {"feature": "Dashboards", "adoption": 96, "trend": "+4"},
                {"feature": "Alerts", "adoption": 78, "trend": "+11"},
                {"feature": "Workflows", "adoption": 64, "trend": "+22"},
                {"feature": "API", "adoption": 51, "trend": "+3"},
                {"feature": "Mobile", "adoption": 34, "trend": "-2"},
                {"feature": "AI Insights", "adoption": 28, "trend": "+28"},
            ],
            "api_usage_monthly": 4_240_000, "storage_used_gb": 142, "storage_total_gb": 500,
            "last_login": hours_ago(2),
            "power_users": ["Sarah Chen", "Marcus Webb", "Priya Singh", "David Liu"],
            "inactive_users": ["John Smith", "Emily Tran"],
            "adoption_trend": gen_trend(142, 18),
        },
        "co-hooli": {
            "mrr": 100000, "list_price": 1380000, "discount": 13, "net_price": 1200000,
            "billing_frequency": "Annual", "payment_terms": "Net 45",
            "contract_start": date(2020, 7, 16), "last_renewal_date": date(2025, 7, 16), "customer_since": date(2020, 7, 16),
            "contract_pdf_url": "/contracts/hooli-enterprise-plus-2025.pdf",
            "partner": "Pied Piper Solutions", "partner_margin": 8, "outstanding_balance": 0,
            "champion": "Jared Dunn — COO",
            "exec_sponsor": "⚠ NEW CIO Gavin Belson — relationship cold",
            "decision_makers": ["Gavin Belson (CIO)", "Jared Dunn (COO)", "Monica Hall (VP Procurement)"],
            "primary_risk": "New CIO actively consolidating vendors; demands ROI by EOW",
            "current_opportunity": "If we land the ROI deck, retain $1.2M and unlock $300k for Marketing org",
            "atlas_executive_summary": "Hooli is at high risk. New CIO Gavin Belson is reviewing all vendor spend; champion (Jared) is one level below. Seat utilization dropped from 84% to 71% after reorg. Must multi-thread: ROI to Gavin, MSA/SOC2 to Monica, technical case to Jared.",
            "atlas_confidence": 78,
            "purchased_products": ["Analytics Core", "Workflow Automation", "AI Agents", "Premium Support"],
            "seats_purchased": 850, "seats_used": 604,
            "dau": 412, "wau": 588, "mau": 718,
            "feature_adoption": [
                {"feature": "Dashboards", "adoption": 89, "trend": "-3"},
                {"feature": "Workflows", "adoption": 54, "trend": "-18"},
                {"feature": "AI Agents", "adoption": 41, "trend": "+12"},
                {"feature": "API", "adoption": 72, "trend": "+1"},
                {"feature": "Alerts", "adoption": 48, "trend": "-9"},
                {"feature": "Mobile", "adoption": 22, "trend": "-4"},
            ],
            "api_usage_monthly": 38_200_000, "storage_used_gb": 2840, "storage_total_gb": 5000,
            "last_login": hours_ago(4),
            "power_users": ["Jared Dunn", "Big Head", "Dinesh Chugtai", "Gilfoyle"],
            "inactive_users": ["Pat Lee", "Erlich Bachman", "Russ Hanneman"],
            "adoption_trend": gen_trend(412, 60),
        },
        "co-globex": {
            "mrr": 37500, "list_price": 528000, "discount": 15, "net_price": 450000,
            "billing_frequency": "Annual", "payment_terms": "Net 60",
            "contract_start": date(2022, 7, 10), "last_renewal_date": date(2024, 7, 10), "customer_since": date(2022, 7, 10),
            "contract_pdf_url": "/contracts/globex-business-2024.pdf",
            "partner": None, "partner_margin": 0, "outstanding_balance": 18750,
            "champion": "⚠ Departed — Jacques Pernod (left 2 weeks ago)",
            "exec_sponsor": "Hans Gruber — CTO (skeptical)",
            "decision_makers": ["Hans Gruber (CTO)", "Marie Laurent (Head of IT, new)", "Walter Eckhardt (CFO)"],
            "primary_risk": "3 open P1 tickets blocking month-end close; CTO evaluating alternatives",
            "current_opportunity": "Remediation plan + executive sponsorship could retain $450k",
            "atlas_executive_summary": "CRITICAL. Globex is days from churn. Champion departed. Hans Gruber demands remediation plan before renewal. SAP integration P1 unresolved for 6 days. Outstanding $18.75k invoice 12 days overdue. Action: ship written remediation plan today; escalate engineering to fix SAP integration this week.",
            "atlas_confidence": 64,
            "purchased_products": ["Analytics Core", "SAP Integration", "Standard Support"],
            "seats_purchased": 180, "seats_used": 76,
            "dau": 38, "wau": 64, "mau": 102,
            "feature_adoption": [
                {"feature": "Dashboards", "adoption": 42, "trend": "-28"},
                {"feature": "SAP Sync", "adoption": 18, "trend": "-44"},
                {"feature": "Workflows", "adoption": 22, "trend": "-12"},
                {"feature": "Alerts", "adoption": 19, "trend": "-15"},
                {"feature": "API", "adoption": 8, "trend": "-22"},
                {"feature": "Mobile", "adoption": 4, "trend": "-6"},
            ],
            "api_usage_monthly": 380_000, "storage_used_gb": 42, "storage_total_gb": 250,
            "last_login": hours_ago(22),
            "power_users": ["Marie Laurent"],
            "inactive_users": ["Klaus Mueller", "Sophie Bernard", "Pierre Dupont", "Jean-Luc Vidal", "Anna Ricci"],
            "adoption_trend": gen_trend(38, 30),
        },
        "co-initech": {
            "mrr": 15000, "list_price": 192000, "discount": 6, "net_price": 180000,
            "billing_frequency": "Annual", "payment_terms": "Net 30",
            "contract_start": date(2022, 9, 1), "last_renewal_date": date(2024, 9, 1), "customer_since": date(2019, 9, 1),
            "contract_pdf_url": "/contracts/initech-business-2024.pdf",
            "partner": None, "partner_margin": 0, "outstanding_balance": 0,
            "champion": "Bill Lumbergh — VP Finance",
            "exec_sponsor": "Michael Bolton — CFO",
            "decision_makers": ["Bill Lumbergh (VP Finance)", "Michael Bolton (CFO)", "Samir Nagheenanajar (Controller)"],
            "primary_risk": "Low — strong adoption, exec sponsor engaged",
            "current_opportunity": "SOX 404 attestation upsell ($12k ARR) + reference customer for FinServ vertical",
            "atlas_executive_summary": "Best-in-class healthy account. NPS 9. Exec sponsor agreed to reference call. Peter Gibbons asked about SOX 404 module (uplift +$12k). Recommend: file reference case study, send SOX upsell quote.",
            "atlas_confidence": 96,
            "purchased_products": ["Analytics Core", "Compliance Reporting", "Standard Support"],
            "seats_purchased": 60, "seats_used": 58,
            "dau": 51, "wau": 56, "mau": 58,
            "feature_adoption": [
                {"feature": "Dashboards", "adoption": 100, "trend": "0"},
                {"feature": "Compliance", "adoption": 94, "trend": "+12"},
                {"feature": "Workflows", "adoption": 81, "trend": "+4"},
                {"feature": "Alerts", "adoption": 76, "trend": "+2"},
                {"feature": "API", "adoption": 62, "trend": "+8"},
                {"feature": "Mobile", "adoption": 48, "trend": "+11"},
            ],
            "api_usage_monthly": 1_120_000, "storage_used_gb": 38, "storage_total_gb": 100,
            "last_login": hours_ago(1),
            "power_users": ["Bill Lumbergh", "Peter Gibbons", "Samir Nagheenanajar", "Michael Bolton"],
            "inactive_users": [],
            "adoption_trend": gen_trend(51, 6),
        },
        "co-umbrella": {
            "mrr": 56666, "list_price": 798000, "discount": 15, "net_price": 680000,
            "billing_frequency": "Annual", "payment_terms": "Net 45",
            "contract_start": date(2021, 7, 28), "last_renewal_date": date(2024, 7, 28), "customer_since": date(2018, 7, 28),
            "contract_pdf_url": "/contracts/umbrella-enterprise-2024.pdf",
            "partner": "Tyrell Consulting", "partner_margin": 12, "outstanding_balance": 0,
            "champion": "Albert Wesker — Chief Research Officer",
            "exec_sponsor": "Albert Wesker — CRO (decision maker, busy)",
            "decision_makers": ["Albert Wesker (CRO)", "Ada Wong (CISO)", "Leon Kennedy (VP Operations)"],
            "primary_risk": "CISO Ada Wong gating renewal on SOC2 Type II + subprocessor list",
            "current_opportunity": "R&D expansion 40→75 seats (+$35k ARR) pending security signoff",
            "atlas_executive_summary": "Umbrella is in a critical 14-day window. CISO Ada Wong gating renewal on security docs (SOC2 Type II, subprocessor list, GxP validation). Wesker has verbally committed to 35-seat R&D expansion contingent on signoff. Plan: ship security pack today, schedule Ada review for Jun 29.",
            "atlas_confidence": 84,
            "purchased_products": ["Analytics Core", "Compliance Reporting", "GxP Validation", "Premium Support", "AI Agents"],
            "seats_purchased": 220, "seats_used": 158,
            "dau": 124, "wau": 184, "mau": 212,
            "feature_adoption": [
                {"feature": "Dashboards", "adoption": 88, "trend": "+2"},
                {"feature": "Compliance", "adoption": 92, "trend": "+6"},
                {"feature": "GxP", "adoption": 71, "trend": "+18"},
                {"feature": "AI Agents", "adoption": 56, "trend": "+22"},
                {"feature": "API", "adoption": 64, "trend": "+8"},
                {"feature": "Mobile", "adoption": 19, "trend": "+3"},
            ],
            "api_usage_monthly": 8_400_000, "storage_used_gb": 1240, "storage_total_gb": 2000,
            "last_login": hours_ago(6),
            "power_users": ["Albert Wesker", "Ada Wong", "Leon Kennedy", "Claire Redfield"],
            "inactive_users": ["Jill Valentine", "Chris Redfield"],
            "adoption_trend": gen_trend(124, 22),
        },
    }


def build_invoices():
    import uuid

    list_ = []
    cfg = [
        {"id": "co-acme", "amt": 20000, "count": 12, "freq": "monthly", "start": 12},
        {"id": "co-hooli", "amt": 300000, "count": 4, "freq": "quarterly", "start": 12},
        {"id": "co-globex", "amt": 112500, "count": 8, "freq": "quarterly", "start": 24, "last_overdue": True},
        {"id": "co-initech", "amt": 45000, "count": 4, "freq": "quarterly", "start": 12},
        {"id": "co-umbrella", "amt": 170000, "count": 4, "freq": "quarterly", "start": 12},
    ]
    for c in cfg:
        for i in range(c["count"]):
            months_ago = c["start"] - i * (1 if c["freq"] == "monthly" else 3)
            if months_ago < -1:
                continue
            today = date.today()
            month_index = today.month - 1 - months_ago
            year = today.year + month_index // 12
            month = month_index % 12 + 1
            d = date(year, month, 1)
            is_future = months_ago < 0
            is_overdue = c.get("last_overdue") and i == c["count"] - 1
            status = "scheduled" if is_future else "overdue" if is_overdue else "paid"
            list_.append({
                "id": uuid.uuid4(),
                "company_id": c["id"],
                "number": f"INV-{str(2024 + (c['count'] - i) // 12)[-2:]}-{1000 + i * 7 + len(c['id'])}",
                "date": d,
                "due_date": d + timedelta(days=30),
                "amount": c["amt"],
                "status": status,
                "period": d.strftime("%b %Y") if c["freq"] == "monthly" else f"Q{(d.month - 1) // 3 + 1} {d.year}",
                "description": "Monthly subscription" if c["freq"] == "monthly" else "Quarterly subscription",
            })
    return list_


def build_products():
    return [
        {"id": "p-core", "name": "Analytics Core", "price_per_seat": 100, "monthly_per_seat": 9, "tier": "Business"},
        {"id": "p-enterprise", "name": "Analytics Enterprise", "price_per_seat": 180, "monthly_per_seat": 18, "tier": "Enterprise"},
        {"id": "p-enterprise-plus", "name": "Analytics Enterprise Plus", "price_per_seat": 300, "monthly_per_seat": 28, "tier": "Enterprise Plus"},
        {"id": "p-workflow", "name": "Workflow Automation", "price_per_seat": 40, "monthly_per_seat": 4, "tier": "Add-on"},
        {"id": "p-ai-agents", "name": "AI Agents", "price_per_seat": 80, "monthly_per_seat": 8, "tier": "Add-on"},
        {"id": "p-compliance", "name": "Compliance Reporting", "price_per_seat": 60, "monthly_per_seat": 6, "tier": "Add-on"},
        {"id": "p-gxp", "name": "GxP Validation", "price_per_seat": 90, "monthly_per_seat": 9, "tier": "Add-on"},
        {"id": "p-sso", "name": "SSO/SCIM", "price_per_seat": 0, "monthly_per_seat": 0, "flat_annual": 24000, "tier": "Add-on"},
        {"id": "p-premium-support", "name": "Premium Support", "price_per_seat": 0, "monthly_per_seat": 0, "flat_annual": 48000, "tier": "Support"},
    ]


def build_policies():
    today = date.today().isoformat()
    return [
        {"id": "pol-discount", "category": "Commercial", "title": "Discount Authorization Matrix", "owner": "Finance · Lisa Park", "last_updated": today, "tags": ["discount", "approval", "pricing"],
         "body": f"# Discount Authorization Matrix\n\nMaximum allowable discount by approver:\n\n- Up to **15%** — CSM auto-approve\n- **15.01% – 25%** — VP Customer Success approval\n- **25.01% – 40%** — CFO approval\n- **40.01% +** — Executive Committee (CEO + CFO)\n\nMulti-year deals: add an extra 5% headroom at each tier.\n\nExceptions: must be filed via deal-desk@atlas.com with revenue justification.\n\nLast reviewed: {today}"},
        {"id": "pol-refund", "category": "Commercial", "title": "Refund Policy", "owner": "Finance · Lisa Park", "last_updated": today, "tags": ["refund", "credit", "billing"],
         "body": "# Refund & Credit Policy\n\n- Pro-rated refunds available within 30 days of invoice for service-level breaches.\n- Annual prepayments are non-refundable; credit notes are the standard remediation.\n- Credit notes >$25k require CFO approval.\n- Refunds beyond 30 days require executive approval and a written remediation report."},
        {"id": "pol-soc2", "category": "Security", "title": "SOC2 Type II Disclosure", "owner": "Security · CISO Office", "last_updated": today, "tags": ["soc2", "security", "compliance"],
         "body": "# SOC2 Type II Disclosure\n\nAtlas maintains a current SOC2 Type II report covering Security, Availability, and Confidentiality.\n\nDisclosure process:\n1. Customer signs MNDA (template: legal/mnda.pdf)\n2. Send the latest report + subprocessor list from security-portal.atlas.com\n3. Walk through findings during a 30-min call\n\nReport refresh cadence: every 12 months."},
        {"id": "pol-escalation", "category": "Support", "title": "Customer Escalation Matrix", "owner": "Support · VP Support", "last_updated": today, "tags": ["escalation", "support", "p1"],
         "body": "# Customer Escalation Matrix\n\nP1 (production down):\n- Page on-call SRE within 15 min\n- VP Support paged at 30 min unresolved\n- Executive sponsor (CRO) at 60 min unresolved\n\nP2 (major impact, workaround exists):\n- Resolve within 4 business hours\n- Daily status update to champion\n\nP3 (minor): 2 business days SLA\nP4 (cosmetic/feature): triage weekly"},
        {"id": "pol-partner", "category": "Commercial", "title": "Partner Approval Process", "owner": "Partnerships · Director", "last_updated": today, "tags": ["partner", "channel", "margin"],
         "body": "# Partner / Channel Approval\n\nStandard partner margins:\n- Reseller: 12%\n- Referral: 8%\n- Strategic SI: up to 20% with director approval\n\nAll partner-led deals must be registered in deal-registration.atlas.com 30 days before close. Channel conflict reviewed weekly."},
        {"id": "pol-finance-approval", "category": "Commercial", "title": "Finance Approval Thresholds", "owner": "Finance · CFO Office", "last_updated": today, "tags": ["approval", "finance", "contract"],
         "body": "# Finance Approval Thresholds\n\nNon-standard terms requiring Finance signoff:\n- Net 60+ payment terms\n- Multi-year deals > $250k ACV\n- Custom indemnification\n- Revenue-share arrangements\n- Termination for convenience clauses\n\nTurnaround: 24h for standard, 72h for complex."},
        {"id": "pol-security-q", "category": "Security", "title": "Security Questionnaire Response", "owner": "Security · CISO Office", "last_updated": today, "tags": ["security", "questionnaire", "sig"],
         "body": "# Security Questionnaire Response Process\n\nStandard turnaround: 5 business days for SIG, CAIQ, or vendor-specific.\n\nMost-requested artifacts (pre-approved):\n- SOC2 Type II report\n- Penetration test summary (annual)\n- Subprocessor list\n- Data residency map\n- Encryption at rest/transit details\n- BCP/DR runbook"},
        {"id": "pol-billing", "category": "Commercial", "title": "Billing Frequency & Terms", "owner": "Finance · Lisa Park", "last_updated": today, "tags": ["billing", "invoicing", "terms"],
         "body": "# Billing Frequency & Payment Terms\n\nStandard: Annual prepay, Net 30.\nAvailable on request: Quarterly (Net 30), Monthly for SMB.\n\nNet 45 / Net 60 require Finance approval. Net 90+ requires CFO approval and 2% surcharge.\n\nLate fees: 1.5%/mo on outstanding balances >30 days."},
        {"id": "pol-renewal", "category": "Commercial", "title": "Renewal Playbook", "owner": "Customer Success · VP CS", "last_updated": today, "tags": ["renewal", "playbook", "expansion"],
         "body": "# Renewal Playbook\n\nT-120 days: open renewal opportunity in Salesforce\nT-90: champion & exec sponsor alignment call\nT-60: send renewal proposal with expansion path\nT-30: redline negotiations, finance approval if needed\nT-14: signature pursuit\nT-0: countersign + handoff to billing"},
        {"id": "pol-gxp", "category": "Security", "title": "GxP Validation Evidence", "owner": "Security · Compliance Lead", "last_updated": today, "tags": ["gxp", "pharma", "validation"],
         "body": "# GxP Validation Evidence\n\nFor regulated pharma customers (e.g. Umbrella, Pfizer):\n- IQ/OQ/PQ documents are stored in compliance-portal.atlas.com\n- 21 CFR Part 11 e-signature evidence available on request\n- Change control summary refreshed quarterly"},
        {"id": "pol-data-residency", "category": "Security", "title": "Data Residency", "owner": "Security · CISO Office", "last_updated": today, "tags": ["data", "residency", "eu", "gdpr"],
         "body": "# Data Residency Options\n\nAvailable regions: US-East, US-West, EU (Frankfurt), UK, APAC (Singapore), Australia.\n\nEU customers default to Frankfurt (GDPR Schrems II compliant). Cross-region replication available on Enterprise Plus."},
        {"id": "pol-ai-usage", "category": "Product", "title": "AI Agents Acceptable Use", "owner": "Product · AI Lead", "last_updated": today, "tags": ["ai", "agents", "policy"],
         "body": "# AI Agents Acceptable Use Policy\n\nAtlas AI Agents process customer data under the standard DPA. Data is never used for model training.\n\nProhibited uses: automated decisions affecting individuals' legal rights, PII enrichment from public sources, real-time biometric inference."},
    ]
