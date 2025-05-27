"""Main FastAPI application module."""

import logging
import sys  # Added for basic logging configuration

# Basic logging configuration (add this before FastAPI app creation)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("fastapi_debug.log"),
        logging.StreamHandler(sys.stdout),  # Keep console logging
    ],
)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .table_guide import table_guide_router

app = FastAPI(title="DeerFlow API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(table_guide_router, prefix="/api")
