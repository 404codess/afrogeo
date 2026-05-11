"""
Example: Basic Location Verification with Afrogeo
"""

from afrogeo import verify

def run_example():
    # 1. Successful verification (Full names)
    print("--- Case 1: Valid Data (Full Names) ---")
    data1 = {
        "country": "Nigeria",
        "state": "Edo",
        "lga": "Oredo"
    }
    result1 = verify(data1)
    if result1:
        print(f"SUCCESS: Normalized: {result1.normalized}")
    else:
        print(f"FAILED: {result1.errors}")

    # 2. Successful verification (ISO codes)
    print("\n--- Case 2: Valid Data (ISO Codes) ---")
    data2 = {
        "country": "NG",
        "state": "ED",
        "lga": "Oredo"
    }
    result2 = verify(data2)
    if result2:
        print(f"SUCCESS: State: {result2.normalized['state']}")

    # 3. Handling Errors
    print("\n--- Case 3: Invalid Data ---")
    data3 = {
        "country": "Nigeria",
        "state": "Lagos",
        "lga": "InvalidLGA"
    }
    result3 = verify(data3)
    if not result3:
        print(f"WARNING: Validation failed as expected: {result3.errors}")

if __name__ == "__main__":
    run_example()
