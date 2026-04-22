"""Authentication models."""

from pydantic import BaseModel, Field


class ApiCredentials(BaseModel):
    """API credentials returned from L1 authentication.

    These credentials are used for L2 (HMAC-SHA256) authentication
    on trading endpoints.
    """

    api_key: str = Field(alias="apiKey", description="UUID format API key")
    secret: str = Field(description="Base64-encoded secret for HMAC signing")
    passphrase: str = Field(description="Random passphrase string")

    model_config = {"populate_by_name": True}


class Credentials(BaseModel):
    """Convenience wrapper for API credentials used in the SDK."""

    api_key: str
    secret: str
    passphrase: str

    @classmethod
    def from_api_response(cls, response: ApiCredentials) -> "Credentials":
        """Create Credentials from API response."""
        return cls(
            api_key=response.api_key,
            secret=response.secret,
            passphrase=response.passphrase,
        )
