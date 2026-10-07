import os
from dotenv import load_dotenv

load_dotenv()

VNPAY_TMN_CODE = os.getenv("VNPAY_TMN_CODE")
VNPAY_HASH_SECRET = os.getenv("VNPAY_HASH_SECRET")

VNPAY_PAYMENT_URL = os.getenv(
    "VNPAY_PAYMENT_URL",
    "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"
)

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")
RETURN_URL = f"{BASE_URL}/payment/return"

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
