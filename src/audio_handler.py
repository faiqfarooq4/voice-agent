import pyaudio
import numpy as np
from loguru import logger
from io import BytesIO
import pyttsx3

class AudioHandler:
    def __init__(self, config):
        self.sample_rate = config["sample_rate"]
        self.chunk_size = config["chunk_size"]
        self.p = pyaudio.PyAudio()
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 200)  # Faster speech
        logger.info("Available audio devices:")
        self.output_devices = []
        for i in range(self.p.get_device_count()):
            device_info = self.p.get_device_info_by_index(i)
            logger.info(f"Device {i}: {device_info['name']}, Output Channels: {device_info['maxOutputChannels']}")
            if device_info["maxOutputChannels"] > 0:
                self.output_devices.append(i)

    def capture_audio(self):
        try:
            stream = self.p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            logger.info("Capturing audio...")
            frames = []
            silence_threshold = 600
            silence_counter = 0
            max_silence = 1 * self.sample_rate // self.chunk_size  # Faster cutoff

            while True:
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                amplitude = np.frombuffer(data, dtype=np.int16).max()
                if amplitude < silence_threshold:
                    silence_counter += 1
                else:
                    silence_counter = 0
                    frames.append(data)
                if silence_counter > max_silence and len(frames) > 0:
                    break

            stream.stop_stream()
            stream.close()
            audio_data = b''.join(frames)
            logger.info(f"Captured audio length: {len(audio_data)} bytes")
            return audio_data if len(audio_data) > 0 else None
        except Exception as e:
            logger.error(f"Audio capture error: {e}")
            return None

    def play_audio(self, text):
        try:
            logger.info(f"Playing audio for text: {text}")
            for device_index in self.output_devices:
                try:
                    logger.info(f"Attempting playback on device index: {device_index}")
                    # Use pyttsx3 for direct playback
                    self.tts_engine.say(text)
                    self.tts_engine.runAndWait()
                    logger.info("Audio playback completed.")
                    return
                except Exception as e:
                    logger.error(f"Audio playback error on device {device_index}: {e}")
            logger.error("No devices played audio successfully.")
        except Exception as e:
            logger.error(f"Audio playback error: {e}")

    def close(self):
        self.p.terminate()
        self.tts_engine.stop()