from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router

def create_app() -> FastAPI:
    app = FastAPI()
    
    # Add CORS middleware with more permissive settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins
        allow_credentials=True,
        allow_methods=["*"],  # Allow all methods
        allow_headers=["*"],  # Allow all headers
        expose_headers=["*"]  # Expose all headers
    )
    
    app.include_router(router)
    return app

app = create_app()
