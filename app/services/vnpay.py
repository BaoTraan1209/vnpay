import hashlib
import hmac
import urllib.parse

from app.config import (
    VNPAY_HASH_SECRET,
    VNPAY_PAYMENT_URL,
)


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


def verify_vnpay_signature(
    params: dict,
    received_hash: str
) -> bool:
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


def build_payment_url(params: dict) -> str:
    secure_hash = generate_vnpay_signature(
        params,
        VNPAY_HASH_SECRET
    )

    payment_params = dict(params)
    payment_params["vnp_SecureHash"] = secure_hash

    return (
        VNPAY_PAYMENT_URL
        + "?"
        + urllib.parse.urlencode(payment_params)
    )
