import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import Orders, PaymentTransactions
from .ecpay_payment_sdk import ECPayPaymentSdk  # ✅ 使用 SDK

@csrf_exempt
def create_ecpay_payment(request, order_id):
    """為指定的訂單建立 ECPay 付款表單"""

    order = get_object_or_404(Orders, order_id=order_id)

    # 設定 ECPay SDK
    ecpay_payment_sdk = ECPayPaymentSdk(
        MerchantID="3002607",
        HashKey="pwFHCqoQZGmho4w6",
        HashIV="EkRm7iFT261dpevs"
    )

    # 設定 ECPay 付款參數
    order_params = {
        "MerchantTradeNo": f"{order.order_id}_{int(datetime.datetime.now().timestamp())}",
        "MerchantTradeDate": order.order_date.strftime("%Y/%m/%d %H:%M:%S"),
        "PaymentType": "aio",
        "TotalAmount": str(int(order.total_amount)),
        "TradeDesc": "商品支付",
        "ItemName": "訂單商品",
        "ReturnURL": "https://396d-1-160-12-173.ngrok-free.app/cart/ecpay/callback/",
        "ClientBackURL": "http://localhost:5173/orderlist",
        "ChoosePayment": "ALL",
        "EncryptType": 1
    }

    # 產生訂單參數（SDK 會自動計算 CheckMacValue）
    final_order_params = ecpay_payment_sdk.create_order(order_params)

    # 產生 ECPay HTML 付款表單
    action_url = "https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5"
    payment_form_html = ecpay_payment_sdk.gen_html_post_form(action_url, final_order_params)

    return JsonResponse({"payment_form": payment_form_html})


@csrf_exempt
def ecpay_callback(request):
    """ECPay 付款完成後，更新付款資訊"""
    if request.method == "POST":
        data = request.POST.dict()
        merchant_trade_no = data.get("MerchantTradeNo")
        rtn_code = data.get("RtnCode")  # ✅ ECPay 付款狀態
        payment_type = data.get("PaymentType")  # ✅ 使用者選擇的付款方式
        transaction_id = data.get("TradeNo")  # ✅ ECPay 交易編號

        order_id = merchant_trade_no.split("_")[0]
        order = get_object_or_404(Orders, order_id=order_id)

        # ✅ 新增付款交易記錄
        PaymentTransactions.objects.create(
            order=order,
            payment_status="SUCCESS" if rtn_code == "1" else "FAILED",
            payment_method=payment_type,
            transaction_id=transaction_id,
            payment_amount=order.total_amount,
        )

        # ✅ 更新訂單狀態
        order.order_status = "COMPLETED" if rtn_code == "1" else "CANCELLED"
        order.save()

        return JsonResponse({"message": "1|OK"})

