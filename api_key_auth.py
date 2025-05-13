from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
import os
from dotenv import load_dotenv

load_dotenv(".env")

api_key_header = APIKeyHeader(name="x-api-key")


def ensure_valid_api_key(api_key_header: str = Security(api_key_header)):
    def check_api_key(key: str) -> bool:
        print(f"API Key header:  {api_key_header}")
        valid_keys = os.environ.get("API_KEYS", "").split(",")
        print(f"Valid Keys:  {valid_keys}")
        return key in valid_keys and key != ""

    if not check_api_key(api_key_header):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )