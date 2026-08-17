import json
import uuid

from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from .. import models
from ..llm.factory import get_llm_provider
from ..serializers import BriefSerializer, FollowupSerializer
from ..services.company_context import get_company_context


def _find_meeting(ctx, meeting_id):
    if meeting_id:
        return next((m for m in ctx["meetings"] if m["id"] == meeting_id), None)
    return ctx["meetings"][0] if ctx["meetings"] else None


class BriefView(APIView):
    def post(self, request):
        company_id = request.data.get("companyId")
        meeting_id = request.data.get("meetingId")
        ctx = get_company_context(company_id)
        if not ctx["company"]:
            return Response({"error": "company not found"}, status=404)
        meeting = _find_meeting(ctx, meeting_id)

        system = (
            "You are Atlas, an elite Customer Success AI assistant. You produce concise, executive-grade "
            "meeting briefs that save CSMs at least 30 minutes of prep. Be specific, reference real evidence "
            "from the data provided. Avoid generic phrases. Output strict JSON."
        )
        user = (
            f"Generate a meeting brief.\n\nMEETING:\n{json.dumps(meeting, indent=2)}\n\n"
            f"COMPANY:\n{json.dumps(ctx['company'], indent=2)}\n\n"
            f"CONTACTS:\n{json.dumps(ctx['contacts'], indent=2)}\n\n"
            f"RECENT EMAILS:\n{json.dumps(ctx['emails'][:8], indent=2)}\n\n"
            f"OPEN TICKETS:\n{json.dumps(ctx['tickets'], indent=2)}\n\n"
            f"CRM NOTES:\n{json.dumps(ctx['notes'], indent=2)}\n\n"
            'Return JSON with EXACT keys:\n{\n'
            '  "executive_summary": string (3-5 sentences),\n'
            '  "recent_activity": string[] (4-6 bullets),\n'
            '  "open_issues": string[] (each issue with severity tag),\n'
            '  "sentiment": { "label": one of ["Positive","Neutral","Mixed","Negative"], "reasoning": string },\n'
            '  "renewal_status": { "label": string, "days_to_renewal": number, "summary": string },\n'
            '  "risks": string[] (3-5 specific risks),\n'
            '  "expansion_opportunities": string[] (2-4 concrete opportunities),\n'
            '  "talking_points": string[] (5-7 actionable talking points in priority order),\n'
            '  "next_actions": [{ "action": string, "owner": string, "due": string }] (3-5 items)\n'
            '}'
        )
        brief_content = get_llm_provider().complete_json(system=system, user=user)
        record = models.Brief.objects.create(
            company_id=company_id, meeting_id=meeting["id"] if meeting else None, brief=brief_content,
        )
        return Response(BriefSerializer(record).data)


class FollowupView(APIView):
    def post(self, request):
        company_id = request.data.get("companyId")
        meeting_id = request.data.get("meetingId")
        transcript = request.data.get("transcript")
        ctx = get_company_context(company_id)
        if not ctx["company"]:
            return Response({"error": "company not found"}, status=404)
        meeting = _find_meeting(ctx, meeting_id)
        latest_brief = models.Brief.objects.filter(company_id=company_id).order_by("-created_at").first()

        system = (
            "You are Atlas. Produce a post-meeting follow-up package. Email must be professional, specific, "
            "reference what was discussed. Output strict JSON."
        )
        user = (
            f"Generate follow-up.\n\nMEETING:\n{json.dumps(meeting, indent=2)}\n\n"
            f"COMPANY:\n{json.dumps(ctx['company'], indent=2)}\n\n"
            f"LATEST BRIEF:\n{json.dumps(latest_brief.brief if latest_brief else None, indent=2)}\n\n"
            f"TRANSCRIPT / MEETING NOTES:\n{transcript or '(no transcript provided — infer reasonable outcomes from brief and context)'}\n\n"
            'Return JSON with keys:\n{\n'
            '  "email": { "to": string[], "subject": string, "body": string (markdown OK, 200-350 words) },\n'
            '  "crm_note": string (concise structured note, 100-180 words),\n'
            '  "tasks": [{ "title": string, "owner": string, "due": string, "priority": one of ["P1","P2","P3"] }] (3-6 tasks)\n'
            '}'
        )
        result = get_llm_provider().complete_json(system=system, user=user)
        record = models.Followup.objects.create(
            company_id=company_id, meeting_id=meeting["id"] if meeting else None, result=result, approved=False,
        )
        return Response(FollowupSerializer(record).data)


class FollowupApproveView(APIView):
    def post(self, request):
        followup_id = request.data.get("id")
        fu = models.Followup.objects.filter(id=followup_id).first()
        if not fu:
            return Response({"error": "not found"}, status=404)

        tasks = fu.result.get("tasks") or []
        task_objs = [
            models.Task(
                id=uuid.uuid4(), company_id=fu.company_id, followup=fu,
                title=t.get("title", ""), owner=t.get("owner", ""), due=t.get("due", ""),
                priority=t.get("priority", ""), status="Open",
            )
            for t in tasks
        ]
        if task_objs:
            models.Task.objects.bulk_create(task_objs)

        fu.approved = True
        fu.approved_at = timezone.now()
        fu.save(update_fields=["approved", "approved_at"])
        return Response({"ok": True, "tasks_created": len(task_objs)})
