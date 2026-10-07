from fastapi.responses import JSONResponse

from app.database import get_db_connection
from app.services.vnpay import verify_vnpay_signature


# =========================================================
# CREATE PENDING TRANSACTION
# =========================================================

def create_pending_transaction(
    order_id: str,
    amount: int
):
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


# =========================================================
# TRANSACTION VERIFICATION
# =========================================================

def process_ipn_params(
    params: dict,
    source: str = "VNPAY IPN CALLBACK"
):

    print("\n========== TRANSACTION VERIFICATION ==========")
    print("Source:", source)

    # =====================================================
    # 1. VERIFY SECURE HASH
    # =====================================================

    received_hash = params.get("vnp_SecureHash")

    if not received_hash:
        print("1. SecureHash: INVALID")

        return JSONResponse({
            "RspCode": "97",
            "Message": "Invalid signature"
        })

    is_valid_signature = verify_vnpay_signature(
        params,
        received_hash
    )

    if not is_valid_signature:
        print("1. SecureHash: INVALID")

        return JSONResponse({
            "RspCode": "97",
            "Message": "Invalid signature"
        })

    print("1. SecureHash: VALID")


    # =====================================================
    # GET VNPAY DATA
    # =====================================================

    order_id = params.get("vnp_TxnRef")

    amount = int(
        params.get("vnp_Amount", 0)
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


    # =====================================================
    # 2. VERIFY TRANSACTION ID
    # =====================================================

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
        print("2. Transaction ID: NOT FOUND")

        cursor.close()
        db.close()

        return JSONResponse({
            "RspCode": "01",
            "Message": "Order not found"
        })

    print("2. Transaction ID: VALID")
    print("   Order ID:", order_id)


    # =====================================================
    # 3. VERIFY AMOUNT
    # =====================================================

    if transaction["amount"] != amount:

        print("3. Amount: INVALID")

        print(
            "   Database Amount:",
            transaction["amount"]
        )

        print(
            "   VNPAY Amount:",
            amount
        )

        print(
            "   Transaction remains PENDING"
        )

        cursor.close()
        db.close()

        return JSONResponse({
            "RspCode": "04",
            "Message": "Invalid amount"
        })

    print("3. Amount: VALID")
    print("   Database Amount:", transaction["amount"])
    print("   VNPAY Amount:", amount)


    # =====================================================
    # 4. VERIFY RESPONSE CODE + TRANSACTION STATUS
    # =====================================================

    print(
        "4. Response Code:",
        response_code
    )

    print(
        "   Transaction Status:",
        transaction_status
    )

    if (
        response_code == "00"
        and transaction_status == "00"
    ):
        print("   Payment Result: SUCCESS")
        new_status = "PAID"

    else:
        print("   Payment Result: FAILED")
        new_status = "FAILED"


    # =====================================================
    # 5. VERIFY DATABASE STATE
    # =====================================================

    if transaction["status"] != "PENDING":

        print(
            "5. Database State:",
            transaction["status"]
        )

        print(
            "   Transaction already processed"
        )

        cursor.close()
        db.close()

        return JSONResponse({
            "RspCode": "02",
            "Message": "Order already confirmed"
        })

    print(
        "5. Database State: PENDING"
    )


    # =====================================================
    # UPDATE FINAL TRANSACTION STATE
    # =====================================================

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

    print("---------------------------------------------")
    print(
        "Database Update: PENDING ->",
        new_status
    )
    print(
        "Final Status:",
        new_status
    )
    print("=============================================\n")

    cursor.close()
    db.close()

    return JSONResponse({
        "RspCode": "00",
        "Message": "Confirm Success"
    }) 