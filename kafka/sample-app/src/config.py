import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class GlobalSettings(BaseSettings):
    KAFKA_BOOTSTRAP_SERVERS : str
    KAFKA_SECURITY_PROTOCOL : str
    KAFKA_SASL_USERNAME : str | None
    KAFKA_SASL_PASSWORD : str | None
    KAFKA_SASL_MECHANISM : str | None
    KAFKA_SR_URL : str
    KAFKA_SR_AUTH : str | None
    OPCUA_ENDPOINT : str
    OPCUA_ROOT_NODE_ID : str

    runtime_env: str | None  = os.getenv("APPENV")
    env_filename: str = f".env.{runtime_env}" if runtime_env else ".env"
    model_config = SettingsConfigDict(env_file=env_filename, env_file_encoding='utf-8')
    
    TEST_TOPIC : str = f"{runtime_env}-test-topic"
    WIND_GENERATION_TOPIC : str = f"{runtime_env}-hz-infra-power-generation-yeongam"
    WIND_DIRECTION_TOPIC : str = f"{runtime_env}-hz-infra-wind-direction-yeongam"
    WIND_SPEED_TOPIC : str = f"{runtime_env}-hz-infra-wind-speed-yeongam"


@lru_cache()
def get_config() -> GlobalSettings:
    return GlobalSettings() # type:ignore
