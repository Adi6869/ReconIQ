from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.v1 import chat, scan, tools
from .config import settings

app = FastAPI(
    title="ReconIQ API",
    description="Interactive chatbot-based reconnaissance assistant",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(scan.router, prefix="/api/v1/scan", tags=["scan"])
app.include_router(tools.router, prefix="/api/v1/tools", tags=["tools"])

@app.get("/")
async def root():
    return {"message": "ReconIQ API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ReconIQ API"}