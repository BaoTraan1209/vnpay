from app.services.transactions import process_ipn_params


def handle_callback(params: dict):
    """
    Keep this function small for presentation:
    receive callback -> print important data -> forward to verification.
    """
    print("\n========== VNPAY IPN CALLBACK ==========")
    print("Order ID:", params.get("vnp_TxnRef"))
    print("Response Code:", params.get("vnp_ResponseCode"))
    print("Transaction Status:", params.get("vnp_TransactionStatus"))
    print("Amount from VNPAY:", params.get("vnp_Amount"))

    return process_ipn_params(
        params,
        source="VNPAY IPN CALLBACK"
    )
