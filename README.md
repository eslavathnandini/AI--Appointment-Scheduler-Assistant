# AI-Powered Appointment Scheduler Assistant

A backend service that parses natural language or document-based appointment requests and converts them into structured scheduling data. The system handles both typed text and image inputs (scanned notes, emails) with OCR.

## Features

- **Text Processing**: Parse natural language appointment requests
- **Image OCR**: Extract text from images using OCR.space API
- **Entity Extraction**: Extract date, time, and department entities
- **Normalization**: Convert extracted entities to ISO format (Asia/Kolkata timezone)
- **Guardrails**: Validate and detect ambiguous requests

## Architecture

```
┌──────────────┐    ┌──────────────┐
│  Text Input  │    │ Image Input  │
└──────┬───────┘    └──────┬───────┘
       │                   │
       ▼                   ▼
┌─────────────────────────────────┐
│      Processing Pipeline        │
├─────────────────────────────────┤
│  1. Input Normalization         │
│  2. OCR (images only)           │
│  3. Entity Extraction           │
│  4. Normalization               │
│  5. Guardrail Validation        │
│  6. Final JSON Output           │
└─────────────────────────────────┘
```

## Tech Stack

- **Framework**: FastAPI
- **OCR**: OCR.space API
- **NLP**: Custom entity extraction
- **Date/Time**: python-dateutil, pytz

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd project
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Edit `.env` file:
```
OCR_API_KEY=K84560877788957
OPENAI_API_KEY=your-openai-api-key-here
```

### 5. Run the Server

```bash
python -m uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### 6. Start ngrok for Public Access

```bash
ngrok http 8000
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/extract/text` | POST | Process text input |
| `/api/v1/extract/image` | POST | Process image with OCR |
| `/api/v1/health` | GET | Health check |
| `/docs` | GET | API documentation |

## Sample Requests

### 1. Text Input - Basic Request

```bash
curl -X POST "http://localhost:8000/api/v1/extract/text" \
  -H "Content-Type: application/json" \
  -d '{"text": "Book dentist next Friday at 3pm"}'
```

**Response:**
```json
{
  "appointment": {
    "department": "Dentist",
    "date": "2025-09-26",
    "time": "15:00",
    "tz": "Asia/Kolkata"
  },
  "status": "ok"
}
```

### 2. Text Input - Different Departments

```bash
curl -X POST "http://localhost:8000/api/v1/extract/text" \
  -H "Content-Type: application/json" \
  -d '{"text": "Schedule doctor appointment tomorrow at 10am"}'
```

### 3. Image Input (cURL with Form Data)

```bash
curl -X POST "http://localhost:8000/api/v1/extract/image" \
  -F "file=@appointment_note.png"
```

### 4. Ambiguous Request (Guardrails)

```bash
curl -X POST "http://localhost:8000/api/v1/extract/text" \
  -H "Content-Type: application/json" \
  -d '{"text": "Book dentist sometime next week"}'
```

**Response:**
```json
{
  "appointment": {
    "department": "Dentist",
    "date": null,
    "time": null,
    "tz": "Asia/Kolkata"
  },
  "status": "needs_clarification",
  "message": "Ambiguous or missing: date, time. Please provide specific details."
}
```

### 5. Health Check

```bash
curl -X GET "http://localhost:8000/api/v1/health"
```

## Testing Examples

### Test with Postman

1. **Text Endpoint**: `POST http://localhost:8000/api/v1/extract/text`
   - Body: `{"text": "Book dentist next Friday at 3pm"}`

2. **Image Endpoint**: `POST http://localhost:8000/api/v1/extract/image`
   - Body: Select "form-data", key="file", value=select image file

## Supported Date/Time Formats

### Date Phrases
- `next Friday` → 2025-09-26 (calculated from today)
- `tomorrow` → 2025-05-04
- `today` → 2025-05-03
- `25th December` → 2025-12-25
- `12/25/2025` → 2025-12-25
- `2025-09-26` → 2025-09-26

### Time Phrases
- `3pm` → 15:00
- `3:30pm` → 15:30
- `10am` → 10:00
- `morning` → 09:00
- `afternoon` → 14:00
- `evening` → 18:00

## Supported Departments

- Dentist, Doctor, Cardiologist, Dermatologist
- Neurologist, Orthopedist, Ophthalmologist, Pediatrician
- Psychiatrist, Gynecologist, Urologist, ENT
- Physiotherapist, Veterinarian

## Project Structure

```
project/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI app entry point
│   ├── config.py         # Configuration settings
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py    # API endpoints
│   │   └── models.py    # Pydantic models
│   └── services/
│       ├── __init__.py
│       ├── ocr_service.py       # OCR.space integration
│       ├── extraction_service.py # Entity extraction
│       ├── normalize_service.py  # Date/time normalization
│       └── guardrail_service.py  # Validation
├── tests/
│   ├── __init__.py
│   └── test_pipeline.py
├── requirements.txt
├── .env
└── README.md
```

## License

MIT