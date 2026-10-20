def test_amount_mismatch():
    # Simulated data
    order_id = "ORDER_TEST001"
    vnpay_amount = 30000
    mysql_amount = 50000
    database_status = "PENDING"

    print("\n========== TRANSACTION VERIFICATION ==========")

    # STEP 1: SECURE HASH
    print("\n1. SECURE HASH VERIFICATION")
    print("Secure Hash: VALID (simulated)")
    print("Result: PASSED")

    # STEP 2: TRANSACTION ID
    print("\n2. TRANSACTION ID VERIFICATION")
    print("VNPAY Order ID:", order_id)
    print("MySQL Order ID:", order_id)
    print("Transaction ID: VALID")
    print("Result: PASSED")

    # STEP 3: AMOUNT
    print("\n3. AMOUNT VERIFICATION")
    print("VNPAY Amount:", f"{vnpay_amount:,} VND")
    print("MySQL Amount:", f"{mysql_amount:,} VND")

    if vnpay_amount != mysql_amount:
        print("Amount: INVALID")
        print("Reason: Amount mismatch")

        print("\n========== VERIFICATION STOPPED ==========")
        print("Failed at: STEP 3 - Amount")
        print("Response: RspCode 04 - Invalid amount")
        print("Database UPDATE: NOT EXECUTED")
        print("Simulated MySQL Status:", database_status)
        return

    print("Amount: VALID")
    print("Result: PASSED")

    # STEP 4: RESPONSE CODE
    print("\n4. RESPONSE CODE VERIFICATION")
    response_code = "00"
    transaction_status = "00"

    if response_code == "00" and transaction_status == "00":
        new_status = "PAID"
    else:
        new_status = "FAILED"

    print("Response Code:", response_code)
    print("Payment Result:", new_status)

    # STEP 5: DATABASE STATE
    print("\n5. DATABASE STATE VERIFICATION")
    print("Current State:", database_status)

    if database_status != "PENDING":
        print("Database State: ALREADY PROCESSED")
        return

    print("Database State: VALID")
    print("Simulated Update:", database_status, "->", new_status)


if __name__ == "__main__":
    test_amount_mismatch()