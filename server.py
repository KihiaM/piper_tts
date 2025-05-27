from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import piper
import io
import wave
import os
from typing import Optional

app = FastAPI()

# Global variable to store loaded voice models
loaded_voices = {}

class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = "default"
    speed: Optional[float] = 1.0

def load_voice(voice_path: str):
    """Load a Piper voice model"""
    try:
        if voice_path not in loaded_voices:
            print(f"Loading voice model: {voice_path}")
            loaded_voices[voice_path] = piper.PiperVoice.load(voice_path)
        return loaded_voices[voice_path]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load voice model: {str(e)}")

def text_to_speech(text: str, voice_model, speed: float = 1.0):
    """Convert text to speech using Piper"""
    try:
        # Synthesize speech
        audio_data = voice_model.synthesize(text, length_scale=1.0/speed)
        
        # Convert to WAV format
        audio_bytes = io.BytesIO()
        with wave.open(audio_bytes, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(voice_model.config.sample_rate)
            wav_file.writeframes(audio_data.tobytes())
        
        audio_bytes.seek(0)
        return audio_bytes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS synthesis failed: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Piper TTS Server is running"}

@app.post("/tts")
async def generate_speech(request: TTSRequest):
    """Generate speech from text"""
    try:
        # Use your own trained model
        # Replace 'your_model.onnx' with the actual filename of your trained model
        voice_path = "your_model.onnx"  # Update this to your model filename
        
        # Check if voice file exists
        if not os.path.exists(voice_path):
            raise HTTPException(
                status_code=404, 
                detail=f"Voice model not found: {voice_path}. Please make sure your trained .onnx file is in the root directory."
            )
        
        # Load voice model
        voice_model = load_voice(voice_path)
        
        # Generate speech
        audio_data = text_to_speech(request.text, voice_model, request.speed)
        
        return StreamingResponse(
            io.BytesIO(audio_data.read()),
            media_type="audio/wav",
            headers={"Content-Disposition": "attachment; filename=speech.wav"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/voices")
async def list_voices():
    """List available voice models"""
    voice_files = [f for f in os.listdir(".") if f.endswith('.onnx')]
    return {"voices": voice_files}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
