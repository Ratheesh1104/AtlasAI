from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from .. import models
from ..serializers import InvoiceSerializer, ProductSerializer, QuoteSerializer
from ..services.formatting import days_until


class ProductListView(APIView):
    def get(self, request):
        return Response(ProductSerializer(models.Product.objects.all(), many=True).data)


class InvoiceListView(APIView):
    def get(self, request):
        qs = models.Invoice.objects.order_by("-date")
        company_id = request.query_params.get("company_id")
        if company_id:
            qs = qs.filter(company_id=company_id)
        return Response(InvoiceSerializer(qs, many=True).data)


class QuoteCalculateView(APIView):
    def post(self, request):
        body = request.data
        company_id = body.get("company_id")
        line_items = body.get("line_items") or []
        discount_pct = body.get("discount_pct") or 0

        company = models.Company.objects.filter(id=company_id).first()
        if not company:
            return Response({"error": "company not found"}, status=404)

        products = {p.id: p for p in models.Product.objects.all()}

        additional_arr = 0
        items = []
        for li in line_items:
            product = products.get(li.get("product_id"))
            if not product:
                items.append({**li, "error": "unknown product"})
                continue
            qty = li.get("quantity") or 0
            unit = product.price_per_seat or 0
            flat = product.flat_annual or 0
            line_arr = qty * unit + (flat if qty > 0 and li.get("include_flat") else 0)
            if li.get("action") == "remove":
                line_arr = -line_arr
            additional_arr += line_arr
            items.append({**li, "product": ProductSerializer(product).data, "line_arr": line_arr})

        gross_arr = additional_arr
        discount_amt = round(gross_arr * (discount_pct / 100))
        net_arr = gross_arr - discount_amt
        additional_mrr = round(net_arr / 12)

        days_remaining = max(1, days_until(company.renewal_date) or 1)
        prorated_amount = round(net_arr * (days_remaining / 365))

        if discount_pct > 40:
            approval_required, approver = "exec", "CEO + CFO"
        elif discount_pct > 25:
            approval_required, approver = "cfo", "CFO"
        elif discount_pct > 15:
            approval_required, approver = "vp", "VP Customer Success"
        else:
            approval_required, approver = "auto", "CSM auto-approve"

        current_arr = company.net_price or company.arr or 0
        new_arr = current_arr + net_arr

        return Response({
            "company": {
                "id": company.id, "name": company.name, "current_arr": current_arr,
                "current_mrr": company.mrr, "renewal_date": company.renewal_date,
            },
            "items": items,
            "gross_additional_arr": gross_arr,
            "discount_pct": discount_pct,
            "discount_amount": discount_amt,
            "additional_arr": net_arr,
            "additional_mrr": additional_mrr,
            "prorated_amount": prorated_amount,
            "days_remaining": days_remaining,
            "new_arr": new_arr,
            "revenue_difference": net_arr,
            "approval_required": approval_required,
            "approver": approver,
        })


class QuoteSaveView(APIView):
    def post(self, request):
        body = dict(request.data)
        company_id = body.pop("company_id", None)
        quote = models.Quote.objects.create(company_id=company_id, data=body, status="draft")
        return Response(QuoteSerializer(quote).data)
