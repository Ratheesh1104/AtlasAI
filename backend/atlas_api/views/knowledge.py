import json

from rest_framework.response import Response
from rest_framework.views import APIView

from .. import models
from ..llm.factory import get_llm_provider
from ..serializers import PolicySerializer


class PolicyListView(APIView):
    def get(self, request):
        policies = models.Policy.objects.order_by("category", "title")
        return Response(PolicySerializer(policies, many=True).data)


class KnowledgeSearchView(APIView):
    def post(self, request):
        q = (request.data.get("query") or "").strip()
        if not q:
            return Response({"error": "query required"}, status=400)

        policies = list(models.Policy.objects.all())
        pol_payload = [{"id": p.id, "title": p.title, "category": p.category, "body": p.body} for p in policies]

        system = (
            "You are Atlas Knowledge, an internal policy search assistant. Answer the question from the "
            "policies provided. Cite specific policies. Be concise but complete. If unsure, say so and lower "
            "confidence. Output strict JSON."
        )
        user = (
            f'QUESTION: "{q}"\n\n'
            f"POLICIES (JSON array):\n{json.dumps(pol_payload, indent=2)}\n\n"
            'Return JSON:\n{\n'
            '  "answer": string (markdown OK, 80-200 words),\n'
            '  "confidence": integer 0-100,\n'
            '  "reasoning": string (1-2 sentences — why this confidence),\n'
            '  "missing_info": string[] (questions Atlas would still want answered),\n'
            '  "sources": [{ "policy_id": string, "excerpt": string (relevant quoted snippet), "relevance": integer 0-100 }]\n'
            '}'
        )
        result = get_llm_provider().complete_json(system=system, user=user)

        pol_map = {p.id: p for p in policies}
        hydrated = []
        for s in result.get("sources") or []:
            policy = pol_map.get(s.get("policy_id"))
            if policy:
                hydrated.append({**s, "policy": PolicySerializer(policy).data})
        result["sources"] = hydrated
        return Response(result)
