"""
End-to-end test suite for SolanaDebugger
Tests: backend API, error parsing, RPC fetching, AI integration
"""
import httpx
import json
import asyncio
import time

BACKEND_URL = "https://solana-debugger-production.up.railway.app"
# For local testing: use http://localhost:8000

TEST_CASES = [
    {
        "name": "Raw error log (funds issue)",
        "input": """Program log: AnchorError caused by account: vault. 
Error Code: Custom(6003). 
Error Message: Unauthorized""",
        "expected_severity": ["funds", "config", "bug"],
    },
    {
        "name": "Generic program error",
        "input": "Program 11111111111111111111111111111111 failed: custom program error: 0x1",
        "expected_severity": ["funds", "config", "bug", "cpi"],
    },
    {
        "name": "Account ownership error",
        "input": "Attempted to read account from program 11111111111111111111111111111111 but the account was not owned by the program",
        "expected_severity": ["config", "bug"],
    },
]

async def test_backend_health():
    """Test if backend is running"""
    print("\n✓ Testing backend health...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{BACKEND_URL}/")
            if response.status_code == 200:
                print(f"  ✓ Backend is online: {response.json()}")
                return True
            else:
                print(f"  ✗ Backend returned status {response.status_code}")
                return False
    except Exception as e:
        print(f"  ✗ Backend error: {e}")
        return False

async def test_error_explanation(input_text, test_name):
    """Test full error explanation flow"""
    print(f"\n✓ Testing: {test_name}")
    print(f"  Input: {input_text[:100]}...")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            start_time = time.time()
            
            response = await client.post(
                f"{BACKEND_URL}/debug",
                json={"input": input_text},
            )
            
            elapsed = time.time() - start_time
            
            if response.status_code != 200:
                print(f"  ✗ API returned status {response.status_code}")
                print(f"    Response: {response.text}")
                return False
            
            data = response.json()
            
            # Check for errors
            if "error" in data:
                print(f"  ✗ Error response: {data['error']}")
                return False
            
            # Validate response structure
            if "ai_explanation" not in data:
                print(f"  ✗ Missing ai_explanation in response")
                return False
            
            ai = data["ai_explanation"]
            
            # Check required fields
            required = ["explanation", "root_cause", "fix", "severity"]
            for field in required:
                if field not in ai:
                    print(f"  ✗ Missing field: {field}")
                    return False
            
            print(f"  ✓ Response received in {elapsed:.2f}s")
            print(f"    Severity: {ai['severity'].upper()}")
            print(f"    Explanation: {ai['explanation'][:80]}...")
            print(f"    Root cause: {ai['root_cause'][:80]}...")
            
            return True
            
    except asyncio.TimeoutError:
        print(f"  ✗ Request timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"  ✗ Exception: {e}")
        return False

async def main():
    print("=" * 60)
    print("SolanaDebugger - End-to-End Test Suite")
    print("=" * 60)
    
    # Test backend health
    health = await test_backend_health()
    if not health:
        print("\n✗ Backend is not accessible. Cannot continue.")
        return
    
    # Test each error case
    results = []
    for test_case in TEST_CASES:
        result = await test_error_explanation(
            test_case["input"],
            test_case["name"]
        )
        results.append((test_case["name"], result))
        await asyncio.sleep(1)  # Rate limiting
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Results")
    print("=" * 60)
    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\nPassed: {passed}/{total}")
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status} - {name}")
    
    if passed == total:
        print("\n✅ All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")

if __name__ == "__main__":
    asyncio.run(main())
