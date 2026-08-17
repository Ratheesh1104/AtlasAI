from .. import models
from ..serializers import (
    CompanySerializer, ContactSerializer, EmailMessageSerializer,
    MeetingSerializer, NoteSerializer, TicketSerializer,
)


def get_company_context(company_id):
    company = models.Company.objects.filter(id=company_id).first()
    return {
        "company": CompanySerializer(company).data if company else None,
        "contacts": ContactSerializer(models.Contact.objects.filter(company_id=company_id), many=True).data,
        "emails": EmailMessageSerializer(
            models.EmailMessage.objects.filter(company_id=company_id).order_by("-timestamp"), many=True
        ).data,
        "tickets": TicketSerializer(
            models.Ticket.objects.filter(company_id=company_id).order_by("-opened"), many=True
        ).data,
        "notes": NoteSerializer(
            models.Note.objects.filter(company_id=company_id).order_by("-timestamp"), many=True
        ).data,
        "meetings": MeetingSerializer(
            models.Meeting.objects.filter(company_id=company_id).order_by("scheduled_at"), many=True
        ).data,
    }


def build_timeline(ctx):
    items = []
    for e in ctx["emails"]:
        items.append({
            "type": "email", "id": e["id"], "title": f"Email from {e['from']}: {e['subject']}",
            "detail": e["snippet"], "meta": e["sentiment"], "at": e["timestamp"],
        })
    for t in ctx["tickets"]:
        items.append({
            "type": "ticket", "id": t["id"], "title": f"{t['priority']} ticket — {t['subject']}",
            "detail": f"Status: {t['status']}", "meta": t["priority"], "at": t["opened"],
        })
    for n in ctx["notes"]:
        items.append({
            "type": "note", "id": n["id"], "title": f"Note by {n['author']}",
            "detail": n["body"], "meta": "note", "at": n["timestamp"],
        })
    for m in ctx["meetings"]:
        items.append({
            "type": "meeting", "id": m["id"], "title": m["title"],
            "detail": f"{m['type']} • {m['duration_min']}m • {m['location']}", "meta": m["type"], "at": m["scheduled_at"],
        })
    items.sort(key=lambda i: i["at"], reverse=True)
    return items
