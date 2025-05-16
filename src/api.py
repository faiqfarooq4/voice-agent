from fastapi import FastAPI, File, UploadFile, HTTPException
from src.stt import STT
from src.tts import TTS
from src.llm import LLM
from src.conversation_manager import ConversationManager
from src.utils import load_config
from loguru import logger
import asyncio

app = FastAPI()
config = load_config("config/config.yaml")
stt = STT(config["stt"])
tts = TTS(config["tts"])
llm = LLM(config["llm"])
conversation_manager = ConversationManager(llm)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/process")
async def process_audio(audio: UploadFile = File(...)):
    try:
        audio_data = await audio.read()
        user_input = await asyncio.to_thread(stt.transcribe, audio_data)
        
        if not user_input:
            response_text = "Sorry, I didn't catch that. Could you repeat?"
            stage = "Error"
        else:
            response_text, stage = conversation_manager.process_input(user_input)

        return {
            "user_input": user_input or "",
            "response": response_text,
            "stage": stage
        }
    except Exception as e:
        logger.error(f"API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))