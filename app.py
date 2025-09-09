from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import logging
from main import PipeLine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RAG Chatbot API",
    description="API for AI chatbot with RAG capabilities",
    version="1.0.0"
)

# CORS middleware - cho phép frontend gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong production nên chỉ định domain cụ thể
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (CSS, JS, images)
if os.path.exists("src/interface"):
    app.mount("/static", StaticFiles(directory="src/interface"), name="static")

# Initialize RAG pipeline
try:
    pipeline = PipeLine()
    logger.info("✅ RAG Pipeline initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize RAG Pipeline: {e}")
    pipeline = None

# Pydantic models for request/response
class ChatRequest(BaseModel):
    message: str
    timestamp: str = None

class ChatResponse(BaseModel):
    reply: str
    status: str = "success"

class StatusResponse(BaseModel):
    status: str
    version: str
    pipeline_ready: bool

# API Routes
@app.get("/", response_class=FileResponse)
async def serve_frontend():
    """Serve trang chủ HTML"""
    html_path = os.path.join("src", "interface", "home.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    else:
        raise HTTPException(status_code=404, detail="Frontend file not found")

@app.get("/api/status", response_model=StatusResponse)
async def api_status():
    """Kiểm tra trạng thái API và pipeline"""
    return StatusResponse(
        status="running",
        version="1.0.0",
        pipeline_ready=pipeline is not None
    )

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Endpoint xử lý chat với RAG pipeline"""
    try:
        # Validate input
        user_message = request.message.strip()
        if not user_message:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Check if pipeline is available
        if pipeline is None:
            raise HTTPException(
                status_code=503, 
                detail="RAG pipeline is not available. Please check server logs."
            )
        
        logger.info(f"🔵 User query: {user_message[:100]}...")
        
        # Get response from RAG pipeline
        response = pipeline.main(user_message)
        
        # Ensure response is not too long
        # max_length = 8000
        # if len(response) > max_length:
        #     response = response[:max_length] + "\n\n[Phản hồi đã được cắt ngắn do quá dài. Vui lòng hỏi cụ thể hơn để nhận câu trả lời ngắn gọn.]"
        
        logger.info(f"🟢 Bot response: {response[:100]}...")
        
        return ChatResponse(reply=response, status="success")
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"❌ Error in chat_endpoint: {e}", exc_info=True)
        return ChatResponse(
            reply="Xin lỗi, đã có lỗi xảy ra trong quá trình xử lý. Vui lòng thử lại sau.",
            status="error"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "pipeline_status": "ready" if pipeline else "error"
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Endpoint not found", "status": 404}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return {"error": "Internal server error", "status": 500}

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting RAG Chatbot Server...")
    uvicorn.run(
        "app:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )