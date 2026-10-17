from datetime import datetime

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from app.config import (
    VNPAY_TMN_CODE,
    RETURN_URL,
)
from app.services.vnpay import build_payment_url
from app.services.transactions import (
    create_pending_transaction,
    process_ipn_params,
)

router = APIRouter(prefix="/payment")

@router.get("/create")
def create_payment(
    request: Request,
    amount: int,
    order_info: str
):
    order_id = (
        "ORDER_"
        + datetime.now().strftime("%Y%m%d%H%M%S")
    )

    # Save transaction as PENDING
    create_pending_transaction(
        order_id,
        amount
    )

    # VNPAY requires amount * 100
    amount_for_vnpay = amount * 100

    create_date = datetime.now().strftime(
        "%Y%m%d%H%M%S"
    )

    client_ip = request.client.host

    payment_params = {
        "vnp_Version": "2.1.0",
        "vnp_Command": "pay",
        "vnp_TmnCode": VNPAY_TMN_CODE,
        "vnp_Amount": str(amount_for_vnpay),
        "vnp_CurrCode": "VND",
        "vnp_TxnRef": order_id,
        "vnp_OrderInfo": order_info,
        "vnp_OrderType": "other",
        "vnp_Locale": "en",
        "vnp_ReturnUrl": RETURN_URL,
        "vnp_IpAddr": client_ip,
        "vnp_CreateDate": create_date
    }

    payment_url = build_payment_url(payment_params)

    print(
        "Order ID:",
        order_id,
        flush=True
    )

    print(
        "Amount:",
        amount,
        flush=True
    )

    print(
        "Order Info:",
        order_info,
        flush=True
    )

    print(
        "Payment URL:",
        payment_url,
        flush=True
    )

    return RedirectResponse(url=payment_url)

@router.get("/return")
async def payment_return(request: Request):

    params = dict(request.query_params)

    order_id = params.get("vnp_TxnRef")
    response_code = params.get("vnp_ResponseCode")
    transaction_status = params.get("vnp_TransactionStatus")

    print(
        "Customer browser returned from VNPAY",
        flush=True
    )

    print(
        "Order ID:",
        order_id,
        flush=True
    )

    print(
        "Response Code:",
        response_code,
        flush=True
    )

    print(
        "Transaction Status:",
        transaction_status,
        flush=True
    )

    if (
        response_code == "00"
        and transaction_status == "00"
    ): return RedirectResponse(url="/payment/success")

    return RedirectResponse(url="/payment/failed")


@router.get("/ipn")
async def vnpay_ipn(request: Request):

    params = dict(request.query_params)
    return process_ipn_params(
        params,
        "VNPAY IPN CALLBACK"
    )