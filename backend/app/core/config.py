import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Autonomous Code Debugging Agent"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Base paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    ROOT_DIR: Path = BASE_DIR.parent
    WORKSPACES_DIR: Path = BASE_DIR / "workspaces"
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/debugging_agent.db"
    
    # Agent settings
    MAX_ITERATIONS: int = 5
    EXECUTION_TIMEOUT_SECONDS: int = 60
    SANDBOX_TYPE: str = "auto"  # 'auto', 'docker', 'process'
    
    # LLM Settings
    LLM_PROVIDER: str = "mock"  # 'mock', 'openai'
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "")
    
    # Sample project path
    SAMPLE_PROJECT_DIR: Path = ROOT_DIR / "sample-project"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
settings.WORKSPACES_DIR.mkdir(parents=True, exist_ok=True)
