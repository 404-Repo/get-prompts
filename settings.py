from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    port: int
    """Port of the service"""
    api_key: str
    """API-KEY to auth prompt generators."""
    text_prompt_default_file: str = "resources/default_text_prompts.txt"
    """File with default text prompts."""
    text_prompt_batch_size: int = 100000
    """Number of text prompts to return to validators."""
    text_prompt_storage_size: int = 1000000
    """Number of text prompts saved in the service"""
    image_prompt_default_file: str = "resources/default_image_prompts.txt"
    """File with default image image prompts."""
    image_prompt_batch_size: int = 10000
    """Number of image prompts to return to validators."""
    image_prompt_storage_size: int = 100000
    """Number of image prompts stored in get prompts service"""

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()  # type: ignore
