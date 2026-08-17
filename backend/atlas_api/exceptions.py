import logging

from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from .llm.base import LLMError

logger = logging.getLogger(__name__)


def api_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)
    if response is not None:
        return response

    if isinstance(exc, LLMError):
        logger.warning("LLM provider error: %s", exc)
        return Response({"error": "LLM request failed", "detail": str(exc)}, status=502)

    logger.exception("Unhandled API error")
    return Response({"error": "Internal server error", "detail": str(exc)}, status=500)
