from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import subprocess
import uuid
import os
import tempfile
import platform

app = FastAPI(
    title="Piper TTS API", 
    version="1.0.0",
    description="Text-to-Speech API using Piper TTS"
)

# Detect if we're on Windows or Linux
IS_WINDOWS = platform.system() == "Windows"

# Set paths based on environment
if IS_WINDOWS:
    # Local development paths
    PIPER_PATH = "C:/Users/User/Documents/piper/piper.exe"
    MODEL_PATH = "C:/Users/User/Documents/piper/exported_model.onnx"
else:
    # Cloud deployment paths (files in same directory as server.py)
    PIPER_PATH = "./piper"
    MODEL_PATH = "./exported_model.onnx"

@app.get("/")
def read_root():
    return {
        "message": "🎤 Piper TTS API is running!",
        "docs": "/docs",
        "platform": platform.system(),
        "endpoints": {
            "health": "/health",
            "synthesize": "/synthesize",
            "documentation": "/docs"
        }
    }

@app.get("/health")
def health_check():
    """Check if Piper and model files are available"""
    piper_exists = os.path.exists(PIPER_PATH)
    model_exists = os.path.exists(MODEL_PATH)
    
    # Check if piper is executable (Linux only)
    piper_executable = True
    if not IS_WINDOWS and piper_exists:
        piper_executable = os.access(PIPER_PATH, os.X_OK)
    
    status = "healthy" if (piper_exists and model_exists and piper_executable) else "unhealthy"
    
    return {
        "status": status,
        "piper_found": piper_exists,
        "piper_executable": piper_executable,
        "model_found": model_exists,
        "piper_path": PIPER_PATH,
        "model_path": MODEL_PATH,
        "platform": platform.system(),
        "working_directory": os.getcwd(),
        "files_in_directory": os.listdir(".") if os.path.exists(".") else []
    }

@app.post("/synthesize")
def synthesize(text: str):
    """Convert text to speech using Piper TTS"""
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    if len(text) > 1000:
        raise HTTPException(status_code=400, detail="Text too long (max 1000 characters)")
   
    output_file = f"output_{uuid.uuid4()}.wav"
    
    # Create a temporary text file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as temp_file:
        temp_file.write(text)
        temp_file_path = temp_file.name
    
    try:
        # Check if files exist
        if not os.path.exists(PIPER_PATH):
            raise HTTPException(status_code=500, detail=f"Piper executable not found at {PIPER_PATH}")
        if not os.path.exists(MODEL_PATH):
            raise HTTPException(status_code=500, detail=f"Model file not found at {MODEL_PATH}")
        
        # Make piper executable on Linux
        if not IS_WINDOWS:
            try:
                os.chmod(PIPER_PATH, 0o755)
            except Exception as e:
                print(f"Warning: Could not make piper executable: {e}")
        
        # Use temp file as input
        with open(temp_file_path, 'r', encoding='utf-8') as input_file:
            result = subprocess.run(
                [PIPER_PATH, "--model", MODEL_PATH, "--output_file", output_file],
                stdin=input_file,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                timeout=30  # 30 second timeout
            )
        
        print(f"Piper stdout: {result.stdout.decode()}")
        print(f"Piper stderr: {result.stderr.decode()}")
        
        # Verify the file was created and has content
        if not os.path.exists(output_file):
            raise HTTPException(status_code=500, detail="Audio file was not generated")
        
        file_size = os.path.getsize(output_file)
        print(f"Generated audio file size: {file_size} bytes")
        
        if file_size < 1000:  # Less than 1KB might indicate empty audio
            raise HTTPException(status_code=500, detail="Generated audio file appears to be empty or corrupted")
        
        # Add a small delay to ensure file is fully written
        import time
        time.sleep(0.1)
        
        # Clean up temp file before returning
        try:
            os.unlink(temp_file_path)
        except:
            pass
        
        return FileResponse(
            output_file, 
            media_type="audio/wav",
            filename=f"speech_{uuid.uuid4().hex[:8]}.wav",
            headers={
                "Content-Disposition": "attachment",
                "Cache-Control": "no-cache"
            }
        )
    
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Speech synthesis timed out")
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode() if e.stderr else str(e)
        raise HTTPException(status_code=500, detail=f"Piper execution failed: {error_msg}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        # Clean up temp file
        try:
            os.unlink(temp_file_path)
        except:
            pass

# For local development
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)