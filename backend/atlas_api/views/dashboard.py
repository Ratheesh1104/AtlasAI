import json

from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from .. import models
from ..llm.factory import get_llm_provider
from ..services import aggregation
from ..services.formatting import days_until


class DashboardV2View(APIView):
    def get(self, request):
        return Response(aggregation.build_dashboard_v2())


class DashboardAISummaryView(APIView):
    def post(self, request):
        companies = list(models.Company.objects.all())
        compact = [
            {
                "name": c.name, "industry": c.industry, "arr": c.arr, "mrr": c.mrr,
                "health": c.health, "health_trend": c.health_trend, "renewal_days": days_until(c.renewal_date),
                "atlas_confidence": c.atlas_confidence, "primary_risk": c.primary_risk,
                "current_opportunity": c.current_opportunity, "atlas_summary": c.atlas_executive_summary,
            }
            for c in companies
        ]
        portfolio = {
            "managed_arr": sum(c["arr"] or 0 for c in compact),
            "avg_health": round(sum(c["health"] or 0 for c in compact) / len(compact)) if compact else 0,
            "accounts": len(compact),
            "at_risk": len([c for c in compact if c["health"] < 70]),
        }

        system = (
            "You are Atlas, an AI analyst writing the morning executive briefing for a VP of "
            "Customer Success. Tone: confident, concise, evidence-grounded. Output strict JSON."
        )
        user = (
            f"PORTFOLIO METRICS:\n{json.dumps(portfolio, indent=2)}\n\n"
            f"ACCOUNTS:\n{json.dumps(compact, indent=2)}\n\n"
            'Return JSON with EXACT schema:\n{\n'
            '  "executive_summary": string (3-5 short sentences, name specific accounts, cite numbers),\n'
            '  "confidence": integer 0-100,\n'
            '  "reasoning": string (1 sentence — why this confidence),\n'
            '  "insights": [{ "title": string, "delta": string (e.g. "+18%" or "-22%"), "detail": string (1 sentence), '
            '"sentiment": one of ["positive","neutral","negative"], "sources": string[] (2-3 source apps) }] (6 items),\n'
            '  "forecast": {\n'
            '    "quarter_end_arr": integer (predict next quarter end ARR),\n'
            '    "expected_expansion": integer (next 90 days),\n'
            '    "expected_churn": integer (next 90 days),\n'
            '    "expected_renewals_count": integer,\n'
            '    "confidence": integer 0-100,\n'
            '    "biggest_risks": [{ "company": string, "risk": string, "impact": integer }] (2-3),\n'
            '    "biggest_opportunities": [{ "company": string, "opportunity": string, "impact": integer }] (2-3)\n'
            '  },\n'
            '  "recommendations": [{ "rank": integer, "title": string, "company": string, "action": string, '
            '"revenue_impact": integer, "kind": one of ["protect","expand","escalate"] }] (3-5 items, ranked by revenue impact)\n'
            '}'
        )

        result = get_llm_provider().complete_json(system=system, user=user)
        result["last_updated"] = timezone.now().isoformat()
        result["sources_used"] = ["Salesforce", "Stripe", "Chargebee", "Zendesk", "Mixpanel", "Amplitude", "Slack", "Meeting Notes"]
        return Response(result)


class DashboardLegacyView(APIView):
    def get(self, request):
        return Response(aggregation.build_dashboard_legacy())
