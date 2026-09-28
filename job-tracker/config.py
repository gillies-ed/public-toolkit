from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./job_tracker.db"
    llm_base_url: str = "http://localhost:11434/v1"
    llm_model: str = "default"
    llm_api_key: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
