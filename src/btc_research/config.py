from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_prefix='BTC_', extra='ignore')

    symbol: str = 'BTCUSDT'
    websocket_url: str = 'wss://fstream.binance.com/ws'
    futures_api_url: str = 'https://fapi.binance.com'
    depth_levels: int = Field(default=1000, ge=5)
    archive_dir: str = './data/raw'
    collector_instance_id: str = 'local'

    # Credentials are intentionally not defined as required values here.
    # Public market-data collection does not require an API key.


settings = Settings()
