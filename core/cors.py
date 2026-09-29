from fastapi.middleware.cors import CORSMiddleware
from typing import List

def setup_cors(app, origins: List[str] = ["*"]):
    """
    Configura el middleware CORS para la aplicación FastAPI.
    
    Args:
        app: Instancia de FastAPI
        origins: Lista de orígenes permitidos (default: ["*"])
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )