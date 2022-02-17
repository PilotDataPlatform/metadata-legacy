from typing import Any
from typing import Dict

from common import VaultClient
from pydantic import BaseSettings
from pydantic import Extra
from starlette.config import Config

config = Config('.env')
SRV_NAMESPACE = config('APP_NAME', cast=str, default='service_entityinfo')
CONFIG_CENTER_ENABLED = config('CONFIG_CENTER_ENABLED', cast=str, default='false')


def load_vault_settings(settings: BaseSettings) -> Dict[str, Any]:
    if CONFIG_CENTER_ENABLED == 'false':
        return {}
    else:
        vc = VaultClient(config('VAULT_URL'), config('VAULT_CRT'), config('VAULT_TOKEN'))
        return vc.get_from_vault(SRV_NAMESPACE)


class Settings(BaseSettings):
    """Store service configuration settings."""

    APP_NAME: str = 'service_entityinfo'
    PORT: int = 5066
    HOST: str = '127.0.0.1'
    env: str = ''
    namespace: str = SRV_NAMESPACE

    NEO4J_SERVICE: str
    ENTITYINFO_SERVICE: str
    PROVENANCE_SERVICE: str
    UTILITY_SERVICE: str
    DATA_OPS_UTIL: str
    CATALOGUING_SERVICE: str

    RDS_DB_URI: str
    RDS_SCHEMA_DEFAULT: str

    OPEN_TELEMETRY_ENABLED: bool = False
    OPEN_TELEMETRY_HOST: str = '127.0.0.1'
    OPEN_TELEMETRY_PORT: int = 6831

    def __init__(self):
        super().__init__()
        self.NEO4J_SERVICE_V1 = self.NEO4J_SERVICE + '/v1/neo4j/'
        self.NEO4J_SERVICE_V2 = self.NEO4J_SERVICE + '/v2/neo4j/'
        self.PROVENANCE_SERVICE_V1 = self.PROVENANCE_SERVICE + '/v1/'
        self.UTILITY_SERVICE_V1 = self.UTILITY_SERVICE + '/v1/'
        self.DATAOPS = self.DATA_OPS_UTIL
        self.CATALOGUING = self.CATALOGUING_SERVICE

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        extra = Extra.allow

        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            return load_vault_settings, env_settings, init_settings, file_secret_settings


ConfigClass = Settings()
