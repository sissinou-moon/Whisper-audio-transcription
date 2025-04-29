# Whisper Speech App
Real-time speech-to-text using Whisper (FastAPI backend).

## Setup
1. Install Python 3.13, `ffmpeg`, and dependencies:
   ```bash
   pip install fastapi uvicorn faster-whisper transformers scipy
   ```

2. If you want to change audio file to .wav 16KHZ you need to add `ffmpeg` to the pc environment , then run this:
   ```bash
   ffmpeg -i input.wav -ar 16000 -ac 1 -t 10 -filter:a "volume=10dB" input_16khz.wav
   ```

3. After you set the environment and write the script `whisperapi.py` , run the server:
   ```bash
   python -m uvicorn whisperapi:app --host 0.0.0.0 --port 8000
   ```
