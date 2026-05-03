@echo off
echo Starting AI Appointment Scheduler...
echo.
echo Starting FastAPI server on port 8000...
start "FastAPI Server" python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
timeout /t 3 /nobreak >nul
echo.
echo Server started at http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo To start ngrok, run in a new terminal:
echo   ngrok http 8000
pause