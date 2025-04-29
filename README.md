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

4. You can test the Whisper-Model if he works well by simply run this command:
   ```bash
   curl -X POST -F "file=@input_16khz.wav" http://localhost:8000/transcribe
   ```

5. You can verify the audio file if it is compatible with the whisper input terms:
   ```bash
   python verify_wav.py input_16khz.wav
   ```
   you should probably see this:
   ```
   INFO: File: input_16khz.wav
   INFO: Channels: 1
   INFO: Sample Width: 2 bytes
   INFO: Sample Rate: 16000 Hz
   INFO: Frames: 160000
   INFO: Duration: 10.000 seconds
   INFO: File is valid WAV
   ```
