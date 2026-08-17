from django.core.management.base import BaseCommand
from django.db import transaction

from atlas_api import models
from atlas_api.services import seed_data


class Command(BaseCommand):
    help = "Wipe and reseed the Atlas demo dataset (companies, contacts, emails, tickets, notes, meetings, invoices, policies, products)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--if-empty",
            action="store_true",
            help="Only seed if the companies table is currently empty (used by the dev server on startup).",
        )

    def handle(self, *args, **options):
        if options["if_empty"] and models.Company.objects.exists():
            self.stdout.write("Companies table not empty, skipping seed (--if-empty).")
            return

        with transaction.atomic():
            self._wipe()
            counts = self._insert()

        self.stdout.write(self.style.SUCCESS(f"Seeded Atlas demo data: {counts}"))

    def _wipe(self):
        for model in [
            models.Task, models.WorkbenchCard, models.Followup, models.Brief, models.Quote,
            models.Invoice, models.Policy, models.Product,
            models.Meeting, models.Note, models.Ticket, models.EmailMessage, models.Contact,
            models.Company,
        ]:
            model.objects.all().delete()

    def _insert(self):
        companies = seed_data.build_companies()
        enrichments = seed_data.build_enrichments()
        counts = {}

        company_objs = []
        for c in companies:
            fields = {**c, **enrichments.get(c["id"], {})}
            company_objs.append(models.Company(**fields))
        models.Company.objects.bulk_create(company_objs)
        counts["companies"] = len(company_objs)

        contacts = seed_data.build_contacts()
        models.Contact.objects.bulk_create(
            models.Contact(id=c["id"], company_id=c["company_id"], name=c["name"], title=c["title"], email=c["email"], role=c["role"])
            for c in contacts
        )
        counts["contacts"] = len(contacts)

        emails = seed_data.build_emails()
        models.EmailMessage.objects.bulk_create(
            models.EmailMessage(
                id=e["id"], company_id=e["company_id"], from_name=e["from_name"], subject=e["subject"],
                snippet=e["snippet"], sentiment=e["sentiment"], timestamp=e["timestamp"],
            )
            for e in emails
        )
        counts["emails"] = len(emails)

        tickets = seed_data.build_tickets()
        models.Ticket.objects.bulk_create(
            models.Ticket(id=t["id"], company_id=t["company_id"], subject=t["subject"], priority=t["priority"], status=t["status"], opened=t["opened"])
            for t in tickets
        )
        counts["tickets"] = len(tickets)

        notes = seed_data.build_notes()
        models.Note.objects.bulk_create(
            models.Note(id=n["id"], company_id=n["company_id"], author=n["author"], body=n["body"], timestamp=n["timestamp"])
            for n in notes
        )
        counts["notes"] = len(notes)

        meetings = seed_data.build_meetings()
        models.Meeting.objects.bulk_create(
            models.Meeting(
                id=m["id"], company_id=m["company_id"], title=m["title"], attendees=m["attendees"],
                scheduled_at=m["scheduled_at"], duration_min=m["duration_min"], type=m["type"], location=m["location"],
            )
            for m in meetings
        )
        counts["meetings"] = len(meetings)

        invoices = seed_data.build_invoices()
        models.Invoice.objects.bulk_create(
            models.Invoice(
                id=i["id"], company_id=i["company_id"], number=i["number"], date=i["date"], due_date=i["due_date"],
                amount=i["amount"], status=i["status"], period=i["period"], description=i["description"],
            )
            for i in invoices
        )
        counts["invoices"] = len(invoices)

        policies = seed_data.build_policies()
        models.Policy.objects.bulk_create(
            models.Policy(id=p["id"], category=p["category"], title=p["title"], owner=p["owner"], last_updated=p["last_updated"], tags=p["tags"], body=p["body"])
            for p in policies
        )
        counts["policies"] = len(policies)

        products = seed_data.build_products()
        models.Product.objects.bulk_create(
            models.Product(
                id=p["id"], name=p["name"], price_per_seat=p["price_per_seat"], monthly_per_seat=p["monthly_per_seat"],
                flat_annual=p.get("flat_annual", 0), tier=p["tier"],
            )
            for p in products
        )
        counts["products"] = len(products)

        return counts
