from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    google_api_key: str = ""

    # Featured tickers shown on the landing page
    FEATURED_TICKERS: list = ["TATASTEEL", "COALINDIA", "NATIONALUM"]

    # Display name overrides (symbol -> friendly name)
    TICKER_LABELS: dict = {
        "NATIONALUM": "NALCO",
    }

    class Config:
        env_file = ".env"


settings = Settings()
