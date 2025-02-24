import uvicorn
import os
from dotenv import load_dotenv

def main():
    """Start the FastAPI application with uvicorn."""
    # Load environment variables
    load_dotenv()
    
    # Get configuration from environment
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "9020"))
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    uvicorn.run(
        "src.backend.app:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level
    )

if __name__ == "__main__":
    main() 