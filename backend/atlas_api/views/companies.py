from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView

from .. import models
from ..serializers import CompanySerializer, ContactSerializer, InvoiceSerializer
from ..services.company_context import build_timeline, get_company_context


class CompanyListView(APIView):
    def get(self, request):
        return Response(CompanySerializer(models.Company.objects.all(), many=True).data)


class CompanyDetailView(APIView):
    def get(self, request, company_id):
        ctx = get_company_context(company_id)
        if not ctx["company"]:
            return Response({"error": "not found"}, status=404)
        timeline = build_timeline(ctx)
        invoices = InvoiceSerializer(models.Invoice.objects.filter(company_id=company_id).order_by("-date"), many=True).data
        for inv in invoices:
            timeline.append({
                "type": "invoice", "id": inv["id"],
                "title": f"Invoice {inv['number']} — ${inv['amount']:,}",
                "detail": f"{inv['period']} • {inv['status']}", "meta": inv["status"],
                "at": f"{inv['date']}T09:00:00Z",
            })
        timeline.sort(key=lambda i: i["at"], reverse=True)
        return Response({**ctx, "timeline": timeline, "invoices": invoices})


class CompanyTimelineView(APIView):
    def get(self, request, company_id):
        ctx = get_company_context(company_id)
        return Response({"company": ctx["company"], "timeline": build_timeline(ctx)})


class SearchView(APIView):
    def get(self, request):
        q = request.query_params.get("q", "")
        if not q:
            return Response([])
        companies = CompanySerializer(
            models.Company.objects.filter(Q(name__icontains=q) | Q(industry__icontains=q))[:10], many=True
        ).data
        contacts = ContactSerializer(
            models.Contact.objects.filter(Q(name__icontains=q) | Q(email__icontains=q) | Q(title__icontains=q))[:10],
            many=True,
        ).data
        return Response({"companies": companies, "contacts": contacts})
