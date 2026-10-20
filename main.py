from datetime import datetime
import hashlib
import hmac
import urllib.parse
import os

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse

import mysql.connector
from dotenv import load_dotenv


load_dotenv()

app = FastAPI()

VNPAY_TMN_CODE = os.getenv("VNPAY_TMN_CODE")
VNPAY_HASH_SECRET = os.getenv("VNPAY_HASH_SECRET")

VNPAY_PAYMENT_URL = os.getenv(
    "VNPAY_PAYMENT_URL",
    "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"
)

BASE_URL = os.getenv("BASE_URL")

RETURN_URL = f"{BASE_URL}/payment/return"


def log_section(title: str):
    print("\n", flush=True)
    print(title, flush=True)
    print(flush=True)


# MYSQL CONNECTION
def get_db_connection():

    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )

# VNPAY SIGNATURE GENERATION
def generate_vnpay_signature(
    params: dict,
    hash_secret: str
) -> str:

    valid_params = {}

    for key, value in params.items():

        if value is not None and value != "":
            valid_params[key] = str(value)

    sorted_params = sorted(valid_params.items())

    hash_data = urllib.parse.urlencode(
        sorted_params
    )

    secure_hash = hmac.new(
        hash_secret.encode("utf-8"),
        hash_data.encode("utf-8"),
        hashlib.sha512
    ).hexdigest()

    return secure_hash


# VNPAY SIGNATURE VERIFICATION
def verify_vnpay_signature(
    params: dict, received_hash: str) -> bool:

    secure_params = {
        key: value
        for key, value in params.items()
        if key not in [
            "vnp_SecureHash",
            "vnp_SecureHashType"
        ]
    }

    sorted_params = sorted(
        secure_params.items()
    )

    hash_data = urllib.parse.urlencode(
        sorted_params
    )

    calculated_hash = hmac.new(
        VNPAY_HASH_SECRET.encode("utf-8"),
        hash_data.encode("utf-8"),
        hashlib.sha512
    ).hexdigest()

    return hmac.compare_digest(
        calculated_hash.lower(),
        received_hash.lower()
    )


def process_ipn_params(
    params: dict,
    source: str = "VNPAY IPN CALLBACK"
):

    log_section(source)

    print("Received parameters:", flush=True)
    print(params, flush=True)

    received_hash = params.get(
        "vnp_SecureHash"
    )

    if not received_hash:

        print("Missing secure hash", flush=True)

        return JSONResponse({

            "RspCode": "97",

            "Message": "Invalid signature"

        })

    is_valid = verify_vnpay_signature(
        params,
        received_hash
    )

    if not is_valid:

        print("Invalid signature", flush=True)

        return JSONResponse({

            "RspCode": "97",

            "Message": "Invalid signature"

        })

    print("Signature verified", flush=True)

    order_id = params.get(
        "vnp_TxnRef"
    )

    amount = int(
        params.get(
            "vnp_Amount",
            0
        )
    ) // 100

    response_code = params.get(
        "vnp_ResponseCode"
    )

    transaction_status = params.get(
        "vnp_TransactionStatus"
    )

    transaction_no = params.get(
        "vnp_TransactionNo"
    )

    print(
        f"Order ID: {order_id}",
        flush=True
    )

    print(
        f"Amount: {amount}",
        flush=True
    )

    print(
        f"Response Code: {response_code}",
        flush=True
    )

    print(
        f"Transaction Status: {transaction_status}",
        flush=True
    )

    db = get_db_connection()

    cursor = db.cursor(
        dictionary=True
    )

    cursor.execute(
        """
        SELECT *
        FROM transactions
        WHERE order_id = %s
        """,
        (order_id,)
    )

    transaction = cursor.fetchone()

    if not transaction:

        cursor.close()
        db.close()

        print("Order not found", flush=True)

        return JSONResponse({

            "RspCode": "01",

            "Message": "Order not found"

        })

    print("Transaction found", flush=True)

    if transaction["amount"] != amount:

        cursor.close()
        db.close()

        print("Invalid amount", flush=True)

        return JSONResponse({

            "RspCode": "04",

            "Message": "Invalid amount"

        })

    print("Amount verified", flush=True)

    if transaction["status"] != "PENDING":

        cursor.close()
        db.close()

        print(
            "Order already confirmed",
            flush=True
        )

        return JSONResponse({

            "RspCode": "02",

            "Message":
                "Order already confirmed"

        })

    if (
        response_code == "00"
        and transaction_status == "00"
    ):

        new_status = "PAID"

    else:

        new_status = "FAILED"

    cursor.execute(
        """
        UPDATE transactions

        SET
            status = %s,
            vnp_transaction_no = %s,
            response_code = %s

        WHERE order_id = %s
        """,

        (
            new_status,
            transaction_no,
            response_code,
            order_id
        )
    )

    db.commit()

    print(
        f"Database updated: {new_status}",
        flush=True
    )

    cursor.close()
    db.close()

    return JSONResponse({

        "RspCode": "00",

        "Message": "Confirm Success"

    })


# HOMEPAGE

@app.get("/", response_class=HTMLResponse)
def home():

    return """
    <!DOCTYPE html>

    <html>

    <head>

        <title>VNPAY Sandbox Demo</title>

        <style>

            body {
                font-family: Arial;
                text-align: center;
                padding-top: 50px;
            }

            .container {
                width: 500px;
                margin: auto;
                padding: 30px;
                border: 1px solid #ddd;
                border-radius: 10px;
            }

            input {
                padding: 10px;
                width: 80%;
                margin: 10px;
            }

            button {
                padding: 12px 25px;
                background: #0066cc;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }

        </style>

    </head>

    <body>

        <div class="container">

            <h2>VNPAY Sandbox Payment</h2>

            <form action="/payment/create" method="get">

                <p>
                    <label>Amount (VND)</label>
                </p>

                <input
                    type="number"
                    name="amount"
                    value="100000"
                    min="1000"
                    required
                >

                <p>
                    <label>Order Information</label>
                </p>

                <input
                    type="text"
                    name="order_info"
                    value="T-Shirt"
                    required
                >

                <br>

                <button type="submit">
                    Pay with VNPAY
                </button>

            </form>

        </div>

    </body>

    </html>
    """


# CREATE PAYMENT REQUEST
@app.get("/payment/create")
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
    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute(
        """
        INSERT INTO transactions
        (
            order_id,
            amount,
            status
        )
        VALUES (%s, %s, %s)
        """,
        (
            order_id,
            amount,
            "PENDING"
        )
    )

    db.commit()

    cursor.close()
    db.close()

    # VNPAY PAYMENT PARAMETERS
    amount_for_vnpay = amount * 100

    create_date = datetime.now().strftime(
        "%Y%m%d%H%M%S"
    )

    client_ip = request.client.host

    payment_params = {

        "vnp_Version": "2.1.0",

        "vnp_Command": "pay",

        "vnp_TmnCode": VNPAY_TMN_CODE,

        "vnp_Amount": str(
            amount_for_vnpay
        ),

        "vnp_CurrCode": "VND",

        "vnp_TxnRef": order_id,

        "vnp_OrderInfo": order_info,

        "vnp_OrderType": "other",

        "vnp_Locale": "en",

        "vnp_ReturnUrl": RETURN_URL,

        "vnp_IpAddr": client_ip,

        "vnp_CreateDate": create_date
    }

    # GENERATE SECURE HASH
    secure_hash = generate_vnpay_signature(
        payment_params,
        VNPAY_HASH_SECRET
    )

    payment_params[
        "vnp_SecureHash"
    ] = secure_hash

    # CREATE VNPAY PAYMENT URL
    payment_url = (
        VNPAY_PAYMENT_URL
        + "?"
        + urllib.parse.urlencode(
            payment_params
        )
    )

    print("\n")
    print("        PAYMENT REQUEST")
    print("Order ID:", order_id)
    print("Amount:", amount)
    print("Order Info:", order_info)
    print("Payment URL:", payment_url)
    print("\n")

    # Redirect customer to VNPAY
    return RedirectResponse(
        url=payment_url
    )

# VNPAY RETURN URL
@app.get("/payment/return")
async def payment_return(
    request: Request
):

    params = dict(request.query_params)

    order_id = params.get("vnp_TxnRef")

    response_code = params.get("vnp_ResponseCode")

    transaction_status = params.get("vnp_TransactionStatus")

    log_section("VNPAY RETURN URL")
    print("Customer browser returned from VNPAY", flush=True)
    print("Order ID:", order_id, flush=True)
    print("Response Code:", response_code, flush=True)
    print("Transaction Status:", transaction_status, flush=True)

    if (
        response_code == "00"
        and transaction_status == "00"
    ):
        return RedirectResponse(
            url="/payment/success"
        )

    return RedirectResponse(
        url="/payment/failed"
    )

@app.get("/payment/failed", response_class=HTMLResponse)
def payment_failed():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Payment Failed</title>
    </head>

    <body style="
        font-family: Arial;
        text-align: center;
        padding-top: 100px;
    ">

        <h1>Payment Failed</h1>

        <p>Your payment was not completed.</p>

        <a href="/">
            Try Again
        </a>

    </body>
    </html>
    """
    
@app.get("/payment/success", response_class=HTMLResponse)
def payment_success():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Payment Successful</title>
    </head>

    <body style="
        font-family: Arial;
        text-align: center;
        padding-top: 100px;
    ">

        <h1>Payment Successful!</h1>

        <p>Your payment has been completed successfully.</p>

        <a href="/">
            Back to Home
        </a>

    </body>
    </html>
    """

# VNPAY IPN CALLBACK
@app.get("/payment/ipn")
async def vnpay_ipn(request: Request):
    params = dict(
        request.query_params
    )
    
    return process_ipn_params(
        params,
        "VNPAY IPN CALLBACK"
    )
