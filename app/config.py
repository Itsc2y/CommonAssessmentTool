"""
This module contains the configuration settings for the application.
It uses Pydantic's BaseSettings to load settings from environment variables.
"""
from typing import ClassVar
from pydantic_settings import BaseSettings
from pydantic import BaseModel

class Settings(BaseSettings):
    """
    Settings class to manage application configuration.

    Attributes:
        MONGODB_URI (str): MongoDB connection URI.
        MONGODB_NAME (str): MongoDB database name.
    """
    MONGODB_URI: str
    MONGODB_NAME: str

    class Config(BaseModel):
        """
        Config class to specify Pydantic settings behavior.

        Attributes:
            env_file (str): Path to the .env file.
        """
        env_file: ClassVar[str]  = ".env"

# Instantiate the settings object to be used throughout the application
settings = Settings()
