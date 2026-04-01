import threading
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .ai import analyze_cv, match_cv_with_jd, CVAnalysis, JobMatchAnalysis
from .grpc_server import serve_grpc

app = FastAPI(title="AI CV Microservice 🚀 (Dual REST & gRPC)")

# --- REST Models ---
class CVRequest(BaseModel):
    cv_text: str

class MatchRequest(BaseModel):
    cv_text: str
    jd_text: str

class CVResponse(CVAnalysis):
    pass

class MatchResponse(JobMatchAnalysis):
    pass

# --- Startup Event for gRPC ---
@app.on_event("startup")
def start_grpc_server():
    print("Starting gRPC server thread...")
    grpc_thread = threading.Thread(target=serve_grpc, daemon=True)
    grpc_thread.start()

# --- REST Endpoints ---
@app.get("/")
def root():
    return {
        "message": "AI Service Running 🚀",
        "modes": ["REST (HTTP 8000)", "gRPC (50051)"]
    }

@app.post("/analyze-cv", response_model=CVResponse)
def analyze(data: CVRequest):
    try:
        if not data.cv_text.strip():
            raise HTTPException(status_code=400, detail="CV text cannot be empty.")
        result = analyze_cv(data.cv_text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Analysis failed: {str(e)}")

@app.post("/match-cv", response_model=MatchResponse)
def match(data: MatchRequest):
    try:
        if not data.cv_text.strip() or not data.jd_text.strip():
            raise HTTPException(status_code=400, detail="Both CV and JD text must be provided.")
        result = match_cv_with_jd(data.cv_text, data.jd_text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Matching failed: {str(e)}")
