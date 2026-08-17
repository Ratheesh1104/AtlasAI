import uuid

from django.db import models


class Company(models.Model):
    id = models.CharField(primary_key=True, max_length=40)
    name = models.CharField(max_length=200)
    industry = models.CharField(max_length=120)
    logo = models.CharField(max_length=8)
    arr = models.BigIntegerField(default=0)
    plan = models.CharField(max_length=80)
    employees = models.IntegerField(default=0)
    region = models.CharField(max_length=80)
    csm = models.CharField(max_length=120, default="You")
    health = models.IntegerField(default=0)
    health_label = models.CharField(max_length=40)
    health_trend = models.CharField(max_length=10, blank=True, default="")
    renewal_date = models.DateTimeField()
    renewal_status = models.CharField(max_length=40)
    product_usage_summary = models.TextField(blank=True, default="")
    strategic_notes = models.TextField(blank=True, default="")

    # Commercial enrichment
    mrr = models.BigIntegerField(default=0)
    list_price = models.BigIntegerField(default=0)
    discount = models.IntegerField(default=0)
    net_price = models.BigIntegerField(default=0)
    billing_frequency = models.CharField(max_length=40, blank=True, default="")
    payment_terms = models.CharField(max_length=40, blank=True, default="")
    contract_start = models.DateField(null=True, blank=True)
    last_renewal_date = models.DateField(null=True, blank=True)
    customer_since = models.DateField(null=True, blank=True)
    contract_pdf_url = models.CharField(max_length=300, blank=True, default="")
    partner = models.CharField(max_length=200, null=True, blank=True)
    partner_margin = models.IntegerField(default=0)
    outstanding_balance = models.BigIntegerField(default=0)

    # Relationship / strategy enrichment
    champion = models.CharField(max_length=200, blank=True, default="")
    exec_sponsor = models.CharField(max_length=200, blank=True, default="")
    decision_makers = models.JSONField(default=list, blank=True)
    primary_risk = models.TextField(blank=True, default="")
    current_opportunity = models.TextField(blank=True, default="")
    atlas_executive_summary = models.TextField(blank=True, default="")
    atlas_confidence = models.IntegerField(default=0)

    # Adoption enrichment
    purchased_products = models.JSONField(default=list, blank=True)
    seats_purchased = models.IntegerField(default=0)
    seats_used = models.IntegerField(default=0)
    dau = models.IntegerField(default=0)
    wau = models.IntegerField(default=0)
    mau = models.IntegerField(default=0)
    feature_adoption = models.JSONField(default=list, blank=True)
    api_usage_monthly = models.BigIntegerField(default=0)
    storage_used_gb = models.FloatField(default=0)
    storage_total_gb = models.FloatField(default=0)
    last_login = models.DateTimeField(null=True, blank=True)
    power_users = models.JSONField(default=list, blank=True)
    inactive_users = models.JSONField(default=list, blank=True)
    adoption_trend = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Contact(models.Model):
    id = models.CharField(primary_key=True, max_length=40)
    company = models.ForeignKey(Company, related_name="contacts", on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    title = models.CharField(max_length=200, blank=True, default="")
    email = models.EmailField()
    role = models.CharField(max_length=120, blank=True, default="")

    def __str__(self):
        return self.name


class EmailMessage(models.Model):
    id = models.CharField(primary_key=True, max_length=40)
    company = models.ForeignKey(Company, related_name="emails", on_delete=models.CASCADE)
    from_name = models.CharField(max_length=200, db_column="from")
    subject = models.CharField(max_length=300)
    snippet = models.TextField(blank=True, default="")
    sentiment = models.CharField(max_length=20, blank=True, default="")
    timestamp = models.DateTimeField()

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return self.subject


class Ticket(models.Model):
    id = models.CharField(primary_key=True, max_length=40)
    company = models.ForeignKey(Company, related_name="tickets", on_delete=models.CASCADE)
    subject = models.CharField(max_length=300)
    priority = models.CharField(max_length=10)
    status = models.CharField(max_length=40)
    opened = models.DateTimeField()

    class Meta:
        ordering = ["-opened"]

    def __str__(self):
        return self.subject


class Note(models.Model):
    id = models.CharField(primary_key=True, max_length=40)
    company = models.ForeignKey(Company, related_name="notes", on_delete=models.CASCADE)
    author = models.CharField(max_length=120, default="You")
    body = models.TextField()
    timestamp = models.DateTimeField()

    class Meta:
        ordering = ["-timestamp"]


class Meeting(models.Model):
    id = models.CharField(primary_key=True, max_length=40)
    company = models.ForeignKey(Company, related_name="meetings", on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    attendees = models.JSONField(default=list, blank=True)
    scheduled_at = models.DateTimeField()
    duration_min = models.IntegerField(default=30)
    type = models.CharField(max_length=40, blank=True, default="")
    location = models.CharField(max_length=120, blank=True, default="")

    class Meta:
        ordering = ["scheduled_at"]

    def __str__(self):
        return self.title


class Invoice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, related_name="invoices", on_delete=models.CASCADE)
    number = models.CharField(max_length=60)
    date = models.DateField()
    due_date = models.DateField()
    amount = models.BigIntegerField()
    status = models.CharField(max_length=20)
    period = models.CharField(max_length=40)
    description = models.CharField(max_length=200, blank=True, default="")

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return self.number


class Policy(models.Model):
    id = models.CharField(primary_key=True, max_length=60)
    category = models.CharField(max_length=80)
    title = models.CharField(max_length=200)
    owner = models.CharField(max_length=200, blank=True, default="")
    last_updated = models.DateField()
    tags = models.JSONField(default=list, blank=True)
    body = models.TextField()

    class Meta:
        ordering = ["category", "title"]
        verbose_name_plural = "policies"

    def __str__(self):
        return self.title


class Product(models.Model):
    id = models.CharField(primary_key=True, max_length=60)
    name = models.CharField(max_length=200)
    price_per_seat = models.IntegerField(default=0)
    monthly_per_seat = models.IntegerField(default=0)
    flat_annual = models.IntegerField(default=0)
    tier = models.CharField(max_length=80, blank=True, default="")

    def __str__(self):
        return self.name


class Quote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, related_name="quotes", null=True, blank=True, on_delete=models.SET_NULL)
    data = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, default="draft")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class Brief(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, related_name="briefs", on_delete=models.CASCADE)
    meeting = models.ForeignKey(Meeting, null=True, blank=True, on_delete=models.SET_NULL)
    brief = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class Followup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, related_name="followups", on_delete=models.CASCADE)
    meeting = models.ForeignKey(Meeting, null=True, blank=True, on_delete=models.SET_NULL)
    result = models.JSONField(default=dict, blank=True)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]


class WorkbenchCard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        Company, related_name="workbench_cards", null=True, blank=True, on_delete=models.CASCADE
    )
    source = models.CharField(max_length=20)  # proactive | user_prompt
    prompt = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, default="ready")  # ready | approved | dismissed
    priority_rank = models.IntegerField(default=2)
    intent = models.CharField(max_length=40, blank=True, default="")
    priority = models.CharField(max_length=4, blank=True, default="")
    title = models.CharField(max_length=300, blank=True, default="")
    reason = models.TextField(blank=True, default="")
    business_impact = models.TextField(blank=True, default="")
    recommended_action = models.TextField(blank=True, default="")
    estimated_seconds = models.IntegerField(default=30)
    artifacts = models.JSONField(default=dict, blank=True)
    edited = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    dismissed_at = models.DateTimeField(null=True, blank=True)
    edited_at = models.DateTimeField(null=True, blank=True)
    regenerated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["priority_rank", "-created_at"]


class Task(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, related_name="tasks", null=True, blank=True, on_delete=models.CASCADE)
    followup = models.ForeignKey(
        Followup, related_name="tasks", null=True, blank=True, on_delete=models.SET_NULL
    )
    card = models.ForeignKey(
        WorkbenchCard, related_name="tasks", null=True, blank=True, on_delete=models.SET_NULL
    )
    title = models.CharField(max_length=300)
    owner = models.CharField(max_length=120, blank=True, default="")
    due = models.CharField(max_length=80, blank=True, default="")
    priority = models.CharField(max_length=4, blank=True, default="")
    status = models.CharField(max_length=20, default="Open")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
