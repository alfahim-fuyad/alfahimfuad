"""Views for the floating chatbot.

Single endpoint:  POST /chatbot/chat/  {message, history?}
Returns JSON:     {reply, provider, failed}

The conversation history is sent by the client on each request, so the
backend stays stateless and works behind any number of gunicorn workers.
"""

import json
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .llm import chat

logger = logging.getLogger(__name__)

MAX_MESSAGE_LEN = 2000
MAX_HISTORY_ITEMS = 12


def _normalise_history(raw):
    """Sanitise client-sent history into a clean list of role/content dicts."""
    if not isinstance(raw, list):
        return []
    clean = []
    for item in raw[:MAX_HISTORY_ITEMS]:
        if not isinstance(item, dict):
            continue
        role = item.get("role")
        content = item.get("content")
        if role not in ("user", "assistant"):
            continue
        if not isinstance(content, str):
            continue
        clean.append({"role": role, "content": content[:MAX_MESSAGE_LEN]})
    return clean


@csrf_exempt
@require_POST
def chat_view(request):
    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON body."}, status=400
        )

    message = (data.get("message") or "").strip()
    if not message:
        return JsonResponse(
            {"error": "Empty message."}, status=400
        )
    if len(message) > MAX_MESSAGE_LEN:
        return JsonResponse(
            {"error": "Message too long."}, status=400
        )

    history = _normalise_history(data.get("history"))

    try:
        result = chat(message, history=history)
    except Exception as exc:  # final safety net
        logger.exception("chatbot: unexpected error: %s", exc)
        return JsonResponse(
            {
                "reply": (
                    "Sorry — something went wrong on my side. "
                    "Please try again in a moment."
                ),
                "provider": "fallback",
                "failed": [],
            },
            status=200,
        )

    return JsonResponse(result, status=200)
