from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from faster_whisper import WhisperModel
from transformers import pipeline
import io
import wave
import numpy as np
import logging
from scipy import signal

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

# Load Whisper model (use 'small' for balance of speed and accuracy)
try:
    whisper_model = WhisperModel("small", device="cpu", compute_type="int8")  # Use "cuda" for GPU
except Exception as e:
    logger.error(f"Failed to load Whisper model: {str(e)}")
    raise

# Load summarization model
try:
    summarizer = pipeline("summarization", model="t5-small")
except Exception as e:
    logger.error(f"Failed to load summarization model: {str(e)}")
    raise

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        # Read audio file
        audio_data = await file.read()
        try:
            wf = wave.open(io.BytesIO(audio_data), "rb")
        except Exception as e:
            logger.error(f"Failed to open WAV file: {str(e)}")
            return JSONResponse(status_code=400, content={"error": "Invalid WAV file"})

        audio = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
        sample_rate = wf.getframerate()
        wf.close()

        # Log audio details
        logger.info(f"Original sample rate: {sample_rate} Hz, Length: {len(audio)} samples")

        # Convert int16 audio to float32 (normalize to [-1.0, 1.0])
        audio = audio.astype(np.float32) / 32768.0

        # Resample to 16000 Hz if needed
        if sample_rate != 16000:
            logger.info(f"Resampling from {sample_rate} Hz to 16000 Hz")
            num_samples = int(len(audio) * 16000 / sample_rate)
            audio = signal.resample(audio, num_samples)
            sample_rate = 16000

        # Trim audio to first 10 seconds (160000 samples at 16kHz)
        max_samples = 160000
        if len(audio) > max_samples:
            logger.info(f"Trimming audio from {len(audio)} to {max_samples} samples")
            audio = audio[:max_samples]

        # Amplify audio (increase volume by 6x)
        audio = audio * 6.0
        audio = np.clip(audio, -1.0, 1.0)  # Prevent clipping

        # Log audio range
        logger.info(f"Processed audio min: {audio.min()}, max: {audio.max()}, mean: {audio.mean()}")

        # Transcribe with faster-whisper
        segments, info = whisper_model.transcribe(
            audio,
            vad_filter=False,  # Disable VAD to capture all speech
            language="en"  # Explicitly set to English
        )
        transcription = " ".join(segment.text for segment in segments).strip()

        # Log transcription
        logger.info(f"Transcription: {transcription}")

        # Summarize transcription (only if non-empty)
        summary = ""
        if transcription:
            try:
                summary = summarizer(
                    transcription,
                    max_length=15,  # Further reduced for short inputs
                    min_length=5,
                    do_sample=False,
                    length_penalty=0.6  # Favor very short summaries
                )[0]["summary_text"]
            except Exception as e:
                logger.warning(f"Summarization failed: {str(e)}")
                summary = transcription[:50]  # Fallback to truncated transcription
        else:
            logger.warning("No transcription generated, skipping summarization")

        return {"transcription": transcription, "summary": summary}
    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})