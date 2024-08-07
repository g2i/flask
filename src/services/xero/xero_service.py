import airbyte as ab
from datetime import datetime, timedelta
import json
from src.utils.redis_client import redis_client
from src.config.environment import XERO_CLIENT_ID, XERO_CLIENT_SECRET, XERO_TENANT_ID

def configure_xero_source():
    xero_tokens_json = redis_client.get("xero_tokens")
    xero_tokens = json.loads(xero_tokens_json)
    source = ab.get_source("source-xero")
    refresh_token = xero_tokens.get("refresh_token")
    access_token = xero_tokens.get("access_token")
    expires_in = xero_tokens.get("expires_in")
    token_expiry_date = (datetime.now() + timedelta(seconds=xero_tokens.get("expires_in", 1800))).isoformat()
    source.set_config(
        config={
            "authentication": {
                "client_id": XERO_CLIENT_ID,
                "client_secret": XERO_CLIENT_SECRET,
                "refresh_token": refresh_token,
                "access_token": access_token,
                "token_expiry_date": token_expiry_date
            },
            "tenant_id": XERO_TENANT_ID,
            "start_date": "2016-01-01T00:00:00Z"
        }
    )
    return source