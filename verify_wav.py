import wave
import sys
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def verify_wav_file(file_path: str) -> bool:
    """
    Verify if a file is a valid WAV file and log its properties.
    Returns True if valid, False otherwise.
    """
    try:
        # Check if file exists
        if not Path(file_path).is_file():
            logger.error(f"File does not exist: {file_path}")
            return False

        # Open WAV file
        with wave.open(file_path, "rb") as wf:
            # Get WAV properties
            channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
            sample_rate = wf.getframerate()
            frames = wf.getnframes()
            duration = frames / sample_rate if sample_rate > 0 else 0

            # Log properties
            logger.info(f"File: {file_path}")
            logger.info(f"Channels: {channels}")
            logger.info(f"Sample Width: {sample_width} bytes")
            logger.info(f"Sample Rate: {sample_rate} Hz")
            logger.info(f"Frames: {frames}")
            logger.info(f"Duration: {duration:.3f} seconds")

            # Basic validation
            if channels < 1:
                logger.error("Invalid number of channels")
                return False
            if sample_width < 1:
                logger.error("Invalid sample width")
                return False
            if sample_rate < 1:
                logger.error("Invalid sample rate")
                return False
            if frames < 1:
                logger.error("No audio data (empty file)")
                return False

            return True

    except wave.Error as e:
        logger.error(f"WAV file error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return False

def main():
    if len(sys.argv) < 2:
        logger.error("Usage: python verify_wav.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    is_valid = verify_wav_file(file_path)
    logger.info(f"File is {'valid' if is_valid else 'invalid'} WAV")

if __name__ == "__main__":
    main()