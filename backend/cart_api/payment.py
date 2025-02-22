import random
import string
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from cart.models import Orders, PaymentTransactions
from .ecpay_payment_sdk import ECPayPaymentSdk
from authentication.permissions import IsAuthenticatedWithCustomToken
from rest_framework.permissions import AllowAny

class ECPayPaymentView(APIView):
    """建立 ECPay 付款請求"""
    permission_classes = [IsAuthenticatedWithCustomToken]
    def post(self, request, order_id):
        """為指定的訂單建立 ECPay 付款表單"""
        order = get_object_or_404(Orders, order_id=order_id)

        # 設定 ECPay SDK
        ecpay_payment_sdk = ECPayPaymentSdk(
            MerchantID="3002607",
            HashKey="pwFHCqoQZGmho4w6",
            HashIV="EkRm7iFT261dpevs"
        )
        random_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        # 設定 ECPay 付款參數
        order_params = {
            "MerchantTradeNo": f"{order.order_id}ECPAY{random_code}",
            "MerchantTradeDate": order.order_date.strftime("%Y/%m/%d %H:%M:%S"),
            "PaymentType": "aio",
            "TotalAmount": str(int(order.total_amount)),
            "TradeDesc": "商品支付",
            "ItemName": "訂單商品",
            "ReturnURL": "https://7793-1-160-29-99.ngrok-free.app/cart_api/ecpay/callback/",
            "ClientBackURL": "http://localhost:5173/orderlist",
            "ChoosePayment": "ALL",
            "EncryptType": 1
        }

        # 產生訂單參數（SDK 會自動計算 CheckMacValue）
        final_order_params = ecpay_payment_sdk.create_order(order_params)

        # 產生 ECPay HTML 付款表單
        action_url = "https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5"
        payment_form_html = ecpay_payment_sdk.gen_html_post_form(action_url, final_order_params)

        return Response({"payment_form": payment_form_html}, status=status.HTTP_200_OK)


class ECPayCallbackView(APIView):
    """ECPay 付款完成後的回調處理"""

    permission_classes = [AllowAny]

    def post(self, request):
        """ECPay 付款完成後，更新付款資訊"""
        data = request.POST.dict()
        print("ECpay回傳數據:", data)

        if not data:
            return Response({"error": "未收到 ECPay 回應"}, status=status.HTTP_400_BAD_REQUEST)

        merchant_trade_no = data.get("MerchantTradeNo")
        rtn_code = data.get("RtnCode")  # ECPay 付款狀態
        payment_type = data.get("PaymentType")  # 使用者選擇的付款方式
        transaction_id = data.get("TradeNo")  # ECPay 交易編號
        print("收到的付款方式:", payment_type)

        if not merchant_trade_no:
            return Response({"error": "缺少 MerchantTradeNo"}, status=status.HTTP_400_BAD_REQUEST)

        order_id = merchant_trade_no.replace("ECPAY", "")[:-4]  # 移除 "ECPAY" 獲取 order_id
        order_id = int(order_id)  # 確保 order_id 是數字
        order = get_object_or_404(Orders, order_id=order_id)

        # 新增付款交易記錄
        PaymentTransactions.objects.create(
            order=order,
            payment_status="SUCCESS" if rtn_code == "1" else "FAILED",
            payment_method=payment_type,
            transaction_id=transaction_id,
            payment_amount=order.total_amount,
        )

        # 更新訂單狀態
        order.order_status = "COMPLETED" if rtn_code == "1" else "CANCELLED"
        order.save()

        return Response("1|OK", status=status.HTTP_200_OK)
