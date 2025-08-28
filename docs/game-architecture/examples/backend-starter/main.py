from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from api import auth, characters, chat, items
from models.database import engine, get_db
from models import user, character, chat as chat_models

# Create database tables
user.Base.metadata.create_all(bind=engine)
character.Base.metadata.create_all(bind=engine)
chat_models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Game API",
    description="A comprehensive game backend API",
    version="1.0.0"
)

# CORS middleware for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(characters.router, prefix="/api/characters", tags=["Characters"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(items.router, prefix="/api/items", tags=["Items"])

@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Game API is running",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Test database connection
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)