"""
This module defines the FastAPI application instance and configures its middleware, 
including CORS and router setup. The application serves as the entry point for the API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.clients.router import router as clients_router

# Create FastAPI application instance
app = FastAPI()

# Set API endpoints on router
app.include_router(clients_router)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_methods=["*"],  # Allows all methods, including OPTIONS
    allow_headers=["*"],  # Allows all headers
)
