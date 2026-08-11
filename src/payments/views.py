from django.http import HttpResponse, HttpResponseBadRequest
from django.views import View

from .services import PaymentError, handle_callback


class LiqPayCallbackView(View):
    """Webhook — CSRF exempt via csrf_exempt in urls."""

    def post(self, request):
        data = request.POST.get('data', '')
        signature = request.POST.get('signature', '')
        if not data or not signature:
            return HttpResponseBadRequest('missing data')
        try:
            handle_callback(data_b64=data, signature=signature)
        except PaymentError as exc:
            return HttpResponseBadRequest(str(exc))
        return HttpResponse('ok')
