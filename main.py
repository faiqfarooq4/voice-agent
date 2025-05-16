import requests
import base64
from src.audio_handler import AudioHandler
from src.utils import load_config, setup_logging
from loguru import logger
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time

def check_server_health(api_url, timeout=5):
    try:
        response = requests.get(f"{api_url}/health", timeout=timeout)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Server health check failed: {e}")
        return False

def main():
    config = load_config("config/config.yaml")
    setup_logging(config["logging"])

    audio_handler = AudioHandler(config["audio"])
    api_url = "http://localhost:8000"

    # Check server health
    logger.info("Checking FastAPI server health...")
    for _ in range(5):
        if check_server_health(api_url):
            logger.info("FastAPI server is running.")
            break
        logger.warning("FastAPI server not responding. Retrying in 2 seconds...")
        time.sleep(2)
    else:
        logger.error("FastAPI server is not running. Please start it with: uvicorn src.api:app --host 0.0.0.0 --port 8000")
        return

    # Setup retry mechanism
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=0.2, status_forcelist=[429, 500, 502, 503, 504])
    session.mount("http://", HTTPAdapter(max_retries=retries))

    logger.info("Voice assistant started. Initiating real-time conversation.")

    try:
        # Start with initial scripted prompt
        initial_prompt = "Hello, this is Horizon Telecom. My name is Assistant. May I have your name, please?"
        print(f"Assistant: {initial_prompt}")
        audio_handler.play_audio(initial_prompt)

        while True:
            audio_data = audio_handler.capture_audio()
            if audio_data is None:
                continue

            files = {"audio": ("audio.wav", audio_data, "audio/wav")}
            try:
                response = session.post(f"{api_url}/process", files=files, timeout=10)
                response.raise_for_status()
                data = response.json()
                print(f"User: {data['user_input']}")
                print(f"Assistant: {data['response']}")
                audio_handler.play_audio(data["response"])
            except requests.exceptions.RequestException as e:
                logger.error(f"API error: {e}")
                error_text = "Sorry, I encountered an issue. Could you repeat?"
                print(f"Assistant: {error_text}")
                audio_handler.play_audio(error_text)

    except KeyboardInterrupt:
        logger.info("Shutting down voice assistant.")
        audio_handler.close()

if __name__ == "__main__":
    main()