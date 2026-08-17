import json
import uuid

from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from .. import models
from ..llm.factory import get_llm_provider
from ..serializers import CompanySerializer, WorkbenchCardSerializer
from ..services.company_context import get_company_context
from ..services.formatting import days_until

PRIORITY_RANK = {"P0": 0, "P1": 1, "P2": 2}


def _company_map():
    return {c.id: CompanySerializer(c).data for c in models.Company.objects.all()}


def _with_company(card_data, company_map):
    return {**card_data, "company": company_map.get(card_data["company_id"])}


class WorkbenchOverviewView(APIView):
    def get(self, request):
        companies = list(models.Company.objects.all())
        meetings_all = list(models.Meeting.objects.all())
        tickets = list(models.Ticket.objects.exclude(status="Resolved"))
        now = timezone.now()
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now.replace(hour=23, minute=59, second=59, microsecond=999000)
        todays = [m for m in meetings_all if start <= m.scheduled_at <= end]
        high_risk = [c for c in companies if c.health < 70]
        expansion = [c for c in companies if c.health >= 80 or "expansion" in (c.strategic_notes or "").lower()]
        renewals_30 = [c for c in companies if (days_until(c.renewal_date) or 999) <= 30]
        pending = models.WorkbenchCard.objects.filter(status="ready").count()
        return Response({
            "highRisk": len(high_risk), "expansion": len(expansion), "renewals": len(renewals_30),
            "meetings": len(todays), "approvals": pending, "openTickets": len(tickets),
        })


class WorkbenchCardsView(APIView):
    def get(self, request):
        cards = models.WorkbenchCard.objects.filter(status__in=["ready", "approved"]).order_by("priority_rank", "-created_at")[:20]
        company_map = _company_map()
        return Response([_with_company(WorkbenchCardSerializer(c).data, company_map) for c in cards])


class WorkbenchProactiveView(APIView):
    def post(self, request):
        companies = list(models.Company.objects.all())
        portfolio = []
        for c in companies:
            ctx = get_company_context(c.id)
            next_meeting = next((m for m in ctx["meetings"] if m["scheduled_at"] > timezone.now().isoformat()), None)
            portfolio.append({
                "company": ctx["company"],
                "contacts": ctx["contacts"][:3],
                "recent_emails": [
                    {"from": e["from"], "subject": e["subject"], "snippet": e["snippet"], "sentiment": e["sentiment"], "when": e["timestamp"]}
                    for e in ctx["emails"][:4]
                ],
                "open_tickets": [t for t in ctx["tickets"] if t["status"] != "Resolved"],
                "notes": ctx["notes"][:2],
                "next_meeting": next_meeting,
            })

        system = (
            "You are Atlas, an elite AI Chief of Staff for Customer Success Managers. Your job is to scan the "
            "CSM's entire portfolio and identify the 5 highest-value next-best-actions they should take TODAY. "
            "For each, you generate the complete deliverable so the CSM only needs to review and approve. Be "
            "specific, evidence-grounded, and assertive. No generic advice. Output strict JSON."
        )
        user = (
            f"PORTFOLIO SNAPSHOT:\n{json.dumps(portfolio, indent=2)}\n\n"
            'Return JSON: { "cards": [ ... 5 items ... ] }\n\n'
            'Each card has EXACT schema:\n{\n'
            '  "company_id": string,\n'
            '  "intent": one of ["draft_email","prepare_meeting","summarize","schedule_call","success_plan","update_crm","executive_escalation"],\n'
            '  "priority": one of ["P0","P1","P2"],\n'
            '  "title": short string (e.g. "Globex executive escalation"),\n'
            '  "reason": 1-2 sentences explaining why Atlas surfaced this NOW (cite specific evidence),\n'
            '  "business_impact": 1 sentence with concrete $ figure,\n'
            '  "recommended_action": 1 sentence,\n'
            '  "estimated_seconds": integer between 20 and 90,\n'
            '  "artifacts": {\n'
            '    "email": optional { "to": string[], "subject": string, "body": string (200-350 words, markdown OK), "suggested_send_time": string },\n'
            '    "crm_note": optional string,\n'
            '    "tasks": optional [{ "title": string, "owner": string, "due": string, "priority": one of ["P1","P2","P3"] }],\n'
            '    "success_plan": optional { "milestones": [{ "title": string, "owner": string, "due": string, "description": string }] },\n'
            '    "summary": optional string\n'
            '  }\n}\n\n'
            "Rules:\n"
            "- Mix card types (email, escalation, success plan, expansion proposal, schedule_call, etc.)\n"
            "- Rank P0 first (urgent, business-critical), then P1, then P2\n"
            "- Each card MUST include artifacts populated for its intent (draft_email → email, success_plan → success_plan, etc.)\n"
            "- Make emails reference actual evidence from the portfolio (specific tickets, names, dates)\n"
            "- Suggested_send_time should be a realistic ISO datetime within next 24h"
        )
        result = get_llm_provider().complete_json(system=system, user=user)

        models.WorkbenchCard.objects.filter(source="proactive").exclude(status="approved").delete()
        card_objs = []
        for c in result.get("cards") or []:
            priority = c.get("priority", "P2")
            card_objs.append(models.WorkbenchCard(
                id=uuid.uuid4(), source="proactive", prompt=None, status="ready",
                priority_rank=PRIORITY_RANK.get(priority, 2),
                company_id=c.get("company_id"), intent=c.get("intent", ""), priority=priority,
                title=c.get("title", ""), reason=c.get("reason", ""), business_impact=c.get("business_impact", ""),
                recommended_action=c.get("recommended_action", ""), estimated_seconds=c.get("estimated_seconds", 30),
                artifacts=c.get("artifacts") or {},
            ))
        if card_objs:
            models.WorkbenchCard.objects.bulk_create(card_objs)

        company_map = _company_map()
        return Response([_with_company(WorkbenchCardSerializer(c).data, company_map) for c in card_objs])


class WorkbenchExecuteView(APIView):
    def post(self, request):
        prompt = (request.data.get("prompt") or "").strip()
        if not prompt:
            return Response({"error": "prompt required"}, status=400)

        companies = list(models.Company.objects.all())
        company_list = [
            {"id": c.id, "name": c.name, "industry": c.industry, "health": c.health, "renewal_date": c.renewal_date.isoformat()}
            for c in companies
        ]

        system = (
            "You are Atlas, an AI Chief of Staff. The CSM gives you a natural-language command. You must: "
            "(1) detect the target company from the list, (2) detect the intent, (3) read the customer memory, "
            "(4) generate the complete deliverable. Output strict JSON."
        )
        detect_user = (
            f'COMMAND: "{prompt}"\n\nAVAILABLE COMPANIES:\n{json.dumps(company_list, indent=2)}\n\n'
            'Return JSON:\n{\n'
            '  "company_id": string (best match) or null if no clear company referenced,\n'
            '  "intent": one of ["draft_email","prepare_meeting","summarize","schedule_call","success_plan","update_crm","executive_escalation"],\n'
            '  "topic": short string describing what the deliverable should cover\n}'
        )
        detect = get_llm_provider().complete_json(system=system, user=detect_user)
        if not detect.get("company_id"):
            return Response({"error": "Could not identify which company. Try mentioning the company by name."}, status=400)

        ctx = get_company_context(detect["company_id"])
        if not ctx["company"]:
            return Response({"error": "Company not found"}, status=404)

        gen_user = (
            f'THE CSM ASKED: "{prompt}"\nDETECTED INTENT: {detect.get("intent")}\nTOPIC: {detect.get("topic")}\n\n'
            f"COMPANY:\n{json.dumps(ctx['company'], indent=2)}\n\n"
            f"CONTACTS:\n{json.dumps(ctx['contacts'], indent=2)}\n\n"
            f"RECENT EMAILS:\n{json.dumps(ctx['emails'][:6], indent=2)}\n\n"
            f"OPEN TICKETS:\n{json.dumps([t for t in ctx['tickets'] if t['status'] != 'Resolved'], indent=2)}\n\n"
            f"NOTES:\n{json.dumps(ctx['notes'], indent=2)}\n\n"
            "Generate the complete deliverable card. Return JSON with EXACT schema:\n{\n"
            f'  "company_id": "{detect["company_id"]}",\n'
            f'  "intent": "{detect.get("intent")}",\n'
            '  "priority": one of ["P0","P1","P2"],\n'
            '  "title": short string,\n'
            '  "reason": 1-2 sentences,\n'
            '  "business_impact": 1 sentence with $ figure,\n'
            '  "recommended_action": 1 sentence,\n'
            '  "estimated_seconds": integer 20-90,\n'
            '  "artifacts": {\n'
            '    "email": { "to": string[], "subject": string, "body": string (200-350 words), "suggested_send_time": string } (if intent involves email),\n'
            '    "crm_note": string (if update_crm or follow-up),\n'
            '    "tasks": [{ "title", "owner", "due", "priority" }] (always include 2-4),\n'
            '    "success_plan": { "milestones": [{ "title", "owner", "due", "description" }] } (if success_plan intent),\n'
            '    "summary": string (if summarize intent)\n'
            "  }\n}\n\n"
            "Make the artifact concrete, evidence-grounded, and ready to send."
        )
        card = get_llm_provider().complete_json(system=system, user=gen_user)
        priority = card.get("priority", "P2")
        record = models.WorkbenchCard.objects.create(
            id=uuid.uuid4(), source="user_prompt", prompt=prompt, status="ready",
            priority_rank=PRIORITY_RANK.get(priority, 2), company_id=card.get("company_id") or detect["company_id"],
            intent=card.get("intent", detect.get("intent", "")), priority=priority, title=card.get("title", ""),
            reason=card.get("reason", ""), business_impact=card.get("business_impact", ""),
            recommended_action=card.get("recommended_action", ""), estimated_seconds=card.get("estimated_seconds", 30),
            artifacts=card.get("artifacts") or {},
        )
        company_map = _company_map()
        return Response(_with_company(WorkbenchCardSerializer(record).data, company_map))


class WorkbenchCardActionView(APIView):
    def post(self, request, card_id, action):
        card = models.WorkbenchCard.objects.filter(id=card_id).first()
        if not card:
            return Response({"error": "not found"}, status=404)

        if action == "approve":
            tasks = (card.artifacts or {}).get("tasks") or []
            task_objs = [
                models.Task(
                    id=uuid.uuid4(), company_id=card.company_id, card=card,
                    title=t.get("title", ""), owner=t.get("owner", ""), due=t.get("due", ""),
                    priority=t.get("priority", ""), status="Open",
                )
                for t in tasks
            ]
            if task_objs:
                models.Task.objects.bulk_create(task_objs)
            card.status = "approved"
            card.approved_at = timezone.now()
            card.save(update_fields=["status", "approved_at"])
            return Response({"ok": True, "tasks_created": len(task_objs)})

        if action == "dismiss":
            card.status = "dismissed"
            card.dismissed_at = timezone.now()
            card.save(update_fields=["status", "dismissed_at"])
            return Response({"ok": True})

        if action == "update":
            if "artifacts" in request.data:
                card.artifacts = request.data["artifacts"]
            if "title" in request.data:
                card.title = request.data["title"]
            card.edited = True
            card.edited_at = timezone.now()
            card.save()
            return Response(WorkbenchCardSerializer(card).data)

        if action == "regenerate":
            ctx = get_company_context(card.company_id)
            if not ctx["company"]:
                return Response({"error": "company not found"}, status=404)
            system = (
                "You are Atlas, an AI Chief of Staff. Regenerate a fresh deliverable for the CSM. Be specific, "
                "evidence-grounded, ready to send. Output strict JSON."
            )
            user = (
                f"INTENT: {card.intent}\nORIGINAL PROMPT: {card.prompt or '(proactive)'}\nORIGINAL TITLE: {card.title}\n"
                f"REASON IT MATTERED: {card.reason}\n\n"
                f"COMPANY:\n{json.dumps(ctx['company'], indent=2)}\n\n"
                f"CONTACTS:\n{json.dumps(ctx['contacts'], indent=2)}\n\n"
                f"RECENT EMAILS:\n{json.dumps(ctx['emails'][:6], indent=2)}\n\n"
                f"OPEN TICKETS:\n{json.dumps([t for t in ctx['tickets'] if t['status'] != 'Resolved'], indent=2)}\n\n"
                f"NOTES:\n{json.dumps(ctx['notes'], indent=2)}\n\n"
                'Return JSON with the SAME schema as before:\n{\n'
                '  "title": string,\n'
                '  "priority": "P0" | "P1" | "P2",\n'
                '  "reason": string,\n'
                '  "business_impact": string,\n'
                '  "recommended_action": string,\n'
                '  "estimated_seconds": integer,\n'
                '  "artifacts": { "email"?, "crm_note"?, "tasks"?, "success_plan"?, "summary"? }\n}\n\n'
                "Make this DIFFERENT and improved compared to the prior version. Vary tone or angle."
            )
            result = get_llm_provider().complete_json(system=system, user=user)
            card.title = result.get("title") or card.title
            card.priority = result.get("priority") or card.priority
            card.reason = result.get("reason") or card.reason
            card.business_impact = result.get("business_impact") or card.business_impact
            card.recommended_action = result.get("recommended_action") or card.recommended_action
            card.estimated_seconds = result.get("estimated_seconds") or card.estimated_seconds
            card.artifacts = result.get("artifacts") or card.artifacts
            card.edited = False
            card.regenerated_at = timezone.now()
            card.save()
            company_map = _company_map()
            return Response(_with_company(WorkbenchCardSerializer(card).data, company_map))

        return Response({"error": "unknown action"}, status=400)
