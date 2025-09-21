import os
from dotenv import load_dotenv

load_dotenv()
from fastmcp import FastMCP
from fastmcp.server.auth.providers.google import GoogleProvider

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

# The GoogleProvider handles Google's token format and validation
auth_provider = GoogleProvider(
    client_id=client_id,  # Your Google OAuth Client ID
    client_secret=client_secret,                  # Your Google OAuth Client Secret
    base_url="http://localhost:8000",                  # Must match your OAuth configuration
    required_scopes=[                                  # Request user information
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
    ],
    # redirect_path="/auth/callback"                  # Default value, customize if needed
)

mcp = FastMCP(name="Google Secured App", auth=auth_provider)

# Add a protected tool to test authentication
@mcp.tool
async def get_user_info() -> dict:
    """Returns information about the authenticated Google user."""
    from fastmcp.server.dependencies import get_access_token
    
    token = get_access_token()
    print(f"Token claims: {token}")
    # The GoogleProvider stores user data in token claims
    return {
        "google_id": token.claims.get("sub"),
        "email": token.claims.get("email"),
        "name": token.claims.get("name"),
        "picture": token.claims.get("picture"),
        "locale": token.claims.get("locale")
    }