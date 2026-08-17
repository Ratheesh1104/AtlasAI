from django.core.management import call_command
from rest_framework.response import Response
from rest_framework.views import APIView

from .. import models
from ..serializers import CompanySerializer, TaskSerializer


class RootView(APIView):
    def get(self, request):
        return Response({"message": "Atlas API", "version": "0.1"})


class SeedView(APIView):
    def post(self, request):
        call_command("seed_atlas")
        counts = {
            "companies": models.Company.objects.count(),
            "contacts": models.Contact.objects.count(),
            "emails": models.EmailMessage.objects.count(),
            "tickets": models.Ticket.objects.count(),
            "notes": models.Note.objects.count(),
            "meetings": models.Meeting.objects.count(),
        }
        return Response({"ok": True, "counts": counts})


class TaskListView(APIView):
    def get(self, request):
        tasks = models.Task.objects.order_by("-created_at")
        company_map = {c.id: CompanySerializer(c).data for c in models.Company.objects.all()}
        return Response([
            {**TaskSerializer(t).data, "company": company_map.get(t.company_id)}
            for t in tasks
        ])
