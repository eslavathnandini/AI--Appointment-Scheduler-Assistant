import requests

print("Testing Image OCR Endpoint")
print("=" * 50)

# Test each sample image
images = [
    "sample_images/appointment_1.png",
    "sample_images/appointment_2.png", 
    "sample_images/appointment_3.png",
    "sample_images/appointment_4.png",
    "sample_images/appointment_5.png",
]

for img_path in images:
    print(f"\nTesting: {img_path}")
    print("-" * 40)
    try:
        with open(img_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                'http://localhost:8000/api/v1/extract/image',
                files=files
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure server is running: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")

print("\n" + "=" * 50)
print("Image tests completed!")