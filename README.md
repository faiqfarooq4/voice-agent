Voice Assistant for Customer Care

A conversational voice assistant for telecom call centers using FastAPI, Whisper, gTTS, and Hugging Face LLM.

Setup





Install dependencies: pip install -r requirements.txt



Update config/config.yaml with your Hugging Face API key.



Start FastAPI server: uvicorn src.api:app --host 0.0.0.0 --port 8000



Run the client: python main.py

Features





STT: Whisper (small model) for low-latency speech recognition.



TTS: gTTS for natural audio.



LLM: Hugging Face Meta-Llama-3-8B-Instruct for intelligent responses.



Backend: FastAPI for asynchronous processing.



Workflow: Scripted call center flow (Fronter, Verifier, Closer).



Error Handling: Handles poor audio and irrelevant inputs.

Usage

Speak to the assistant via your microphone. Follow the scripted telecom support flow."# voice-agent" 
