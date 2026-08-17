from rest_framework import serializers

from . import models


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Company
        fields = "__all__"


class ContactSerializer(serializers.ModelSerializer):
    company_id = serializers.CharField(read_only=True)

    class Meta:
        model = models.Contact
        fields = ["id", "company_id", "name", "title", "email", "role"]


class EmailMessageSerializer(serializers.ModelSerializer):
    company_id = serializers.CharField(read_only=True)

    class Meta:
        model = models.EmailMessage
        fields = ["id", "company_id", "from_name", "subject", "snippet", "sentiment", "timestamp"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["from"] = data.pop("from_name")
        return data


class TicketSerializer(serializers.ModelSerializer):
    company_id = serializers.CharField(read_only=True)

    class Meta:
        model = models.Ticket
        fields = ["id", "company_id", "subject", "priority", "status", "opened"]


class NoteSerializer(serializers.ModelSerializer):
    company_id = serializers.CharField(read_only=True)

    class Meta:
        model = models.Note
        fields = ["id", "company_id", "author", "body", "timestamp"]


class MeetingSerializer(serializers.ModelSerializer):
    company_id = serializers.CharField(read_only=True)

    class Meta:
        model = models.Meeting
        fields = ["id", "company_id", "title", "attendees", "scheduled_at", "duration_min", "type", "location"]


class InvoiceSerializer(serializers.ModelSerializer):
    company_id = serializers.CharField(read_only=True)
    id = serializers.UUIDField(read_only=True)

    class Meta:
        model = models.Invoice
        fields = ["id", "company_id", "number", "date", "due_date", "amount", "status", "period", "description"]


class PolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Policy
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = "__all__"


class QuoteSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    company_id = serializers.CharField(read_only=True)

    class Meta:
        model = models.Quote
        fields = ["id", "company_id", "data", "status", "created_at"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        payload = data.pop("data") or {}
        return {**payload, **data}


class BriefSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    company_id = serializers.CharField(read_only=True)
    meeting_id = serializers.CharField(read_only=True)

    class Meta:
        model = models.Brief
        fields = ["id", "company_id", "meeting_id", "brief", "created_at"]


class FollowupSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    company_id = serializers.CharField(read_only=True)
    meeting_id = serializers.CharField(read_only=True)

    class Meta:
        model = models.Followup
        fields = ["id", "company_id", "meeting_id", "result", "approved", "created_at", "approved_at"]


class WorkbenchCardSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    company_id = serializers.CharField(read_only=True)

    class Meta:
        model = models.WorkbenchCard
        fields = [
            "id", "company_id", "source", "prompt", "status", "priority_rank", "intent", "priority",
            "title", "reason", "business_impact", "recommended_action", "estimated_seconds", "artifacts",
            "edited", "created_at", "approved_at", "dismissed_at", "edited_at", "regenerated_at",
        ]


class TaskSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    company_id = serializers.CharField(read_only=True)

    class Meta:
        model = models.Task
        fields = ["id", "company_id", "title", "owner", "due", "priority", "status", "created_at"]
