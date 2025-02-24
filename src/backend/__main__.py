import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Get host and port from environment variables
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "9020"))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    # Run the FastAPI application
    uvicorn.run(
        "src.backend.app:app",
        host=host,
        port=port,
        reload=reload
    ) 