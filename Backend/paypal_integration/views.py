from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
import paypalrestsdk
from paypalrestsdk import Payment
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

paypalrestsdk.configure({
    "mode": getattr(settings, "PAYPAL_MODE", "sandbox"),
    "client_id": getattr(settings, "PAYPAL_CLIENT_ID", ""),
    "client_secret": getattr(settings, "PAYPAL_CLIENT_SECRET", ""),
})

@csrf_exempt
def create_payment(request):
    if request.method == "POST":
        try:
            # Example payment creation logic
            payment = Payment({
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal"
                },
                "transactions": [{
                    "amount": {
                        "total": "10.00",
                        "currency": "USD"
                    },
                    "description": "Test payment"
                }],
                "redirect_urls": {
                    "return_url": "http://localhost:8000/api/v1/paypal/execute",
                    "cancel_url": "http://localhost:8000/api/v1/paypal/cancel"
                }
            })

            if payment.create():
                return JsonResponse({"paymentID": payment.id})
            else:
                logger.error(f"PayPal Payment Creation Error: {payment.error}")
                return JsonResponse({"error": payment.error}, status=400)
        except Exception as e:
            logger.exception("An error occurred while creating the PayPal payment.")
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return HttpResponseNotAllowed(["POST"])

@csrf_exempt
def execute_payment(request):
    if request.method == "POST":
        payment_id = request.POST.get("paymentID")
        payer_id = request.POST.get("payerID")
        if not payment_id or not payer_id:
            return JsonResponse({"error": "Missing paymentID or payerID"}, status=400)

        try:
            payment = Payment.find(payment_id)
            if payment.execute({"payer_id": payer_id}):
                return JsonResponse({"status": "Payment executed successfully"})
            else:
                return JsonResponse({"error": payment.error}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return HttpResponseNotAllowed(["POST"])
