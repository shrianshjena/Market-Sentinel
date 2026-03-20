from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    gemini_api_key: str = ""
    groq_api_key: str = ""
    hf_api_key: str = ""

    # Featured tickers shown on the landing page
    FEATURED_TICKERS: list = ["TATASTEEL", "COALINDIA", "NATIONALUM", "HINDZINC", "HINDCOPPER"]

    # Display name overrides (symbol -> friendly name)
    TICKER_LABELS: dict = {
        "NATIONALUM": "NALCO",
        "HINDZINC": "Hindustan Zinc",
        "HINDCOPPER": "Hindustan Copper",
    }

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
