# Test Commands for Recording
# Run these commands in separate terminal while server is running

print("""
========================================
TEST COMMANDS FOR VIDEO RECORDING
========================================

1. START SERVER FIRST:
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

2. TEST ENDPOINTS:

=== Test 1: Basic Text Input ===
curl -X POST http://localhost:8000/api/v1/extract/text -H "Content-Type: application/json" -d "{\"text\": \"Book dentist next Friday at 3pm\"}"

=== Test 2: Different Department ===
curl -X POST http://localhost:8000/api/v1/extract/text -H "Content-Type: application/json" -d "{\"text\": \"Schedule doctor tomorrow at 10am\"}"

=== Test 3: Ambiguous Request (Guardrails) ===
curl -X POST http://localhost:8000/api/v1/extract/text -H "Content-Type: application/json" -d "{\"text\": \"Book dentist sometime\"}"

=== Test 4: Health Check ===
curl http://localhost:8000/api/v1/health

=== Test 5: API Docs (in browser) ===
http://localhost:8000/docs


AFTER SERVER IS RUNNING, USE THESE PYTHON COMMANDS:
""")

import subprocess
import sys
import time
import os
import requests

def test_endpoints():
    print("\n" + "="*50)
    print("RUNNING TESTS...")
    print("="*50 + "\n")
    
    base_url = "http://localhost:8000"
    
    # Test 1
    print("Test 1: Basic Text Input")
    print("-" * 30)
    r = requests.post(f"{base_url}/api/v1/extract/text", json={"text": "Book dentist next Friday at 3pm"})
    print(f"Input: Book dentist next Friday at 3pm")
    print(f"Output: {r.json()}\n")
    
    # Test 2
    print("Test 2: Different Department")
    print("-" * 30)
    r = requests.post(f"{base_url}/api/v1/extract/text", json={"text": "Schedule doctor appointment tomorrow at 10am"})
    print(f"Input: Schedule doctor appointment tomorrow at 10am")
    print(f"Output: {r.json()}\n")
    
    # Test 3
    print("Test 3: Ambiguous Request (Guardrails)")
    print("-" * 30)
    r = requests.post(f"{base_url}/api/v1/extract/text", json={"text": "Book dentist sometime"})
    print(f"Input: Book dentist sometime")
    print(f"Output: {r.json()}\n")
    
    # Test 4
    print("Test 4: Health Check")
    print("-" * 30)
    r = requests.get(f"{base_url}/api/v1/health")
    print(f"Output: {r.json()}\n")
    
    print("="*50)
    print("ALL TESTS COMPLETED!")
    print("="*50)

if __name__ == "__main__":
    try:
        test_endpoints()
    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure server is running first:")
        print("python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")