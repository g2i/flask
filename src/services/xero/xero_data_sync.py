import airbyte as ab
from airbyte.caches import PostgresCache
from dotenv import load_dotenv
import os, json, redis
from datetime import datetime, timedelta

class XeroDataSync:
    def __init__(self):
        load_dotenv()
        self.redis_client = redis.from_url(os.environ['REDIS_URL'])
        self.source = self._configure_source()
        self.pg_cache = self._configure_cache()
        
    def _configure_source(self):
        xero_tokens_json = self.redis_client.get("xero_tokens")
        xero_tokens = json.loads(xero_tokens_json)
        source = ab.get_source("source-xero")
        refresh_token = xero_tokens.get("refresh_token")
        access_token = xero_tokens.get("access_token")
        expires_in = xero_tokens.get("expires_in")
        token_expiry_date = (datetime.now() + timedelta(seconds=xero_tokens.get("expires_in", 1800))).isoformat()
        source.set_config(
            config={
                "authentication": {
                    "client_id": os.getenv("XERO_CLIENT_ID"),
                    "client_secret": os.getenv("XERO_CLIENT_SECRET"),
                    "refresh_token": refresh_token,
                    "access_token": access_token,
                    "token_expiry_date": token_expiry_date
                },
                "tenant_id": os.getenv("XERO_TENANT_ID"),
                "start_date": "2016-01-01T00:00:00Z"
            }
        )
        return source

    def _configure_cache(self):
        return PostgresCache(
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT"),
            username=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            database=os.getenv("POSTGRES_DATABASE"),
            schema_name="xero"
        )

    def sync_data(self):
        self.source.select_all_streams()
        read_result: ab.ReadResult = self.source.read(cache=self.pg_cache, force_full_refresh=True)
        print(read_result)
        print("Data sync finished")

if __name__ == "__main__":
    syncer = XeroDataSync()
    syncer.sync_data()