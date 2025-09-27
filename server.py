import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
from fastmcp import FastMCP
from fastmcp.server.auth.providers.google import GoogleProvider

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

# Initialize Supabase client
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

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
    """Returns information about the authenticated Google user along with email"""
    from fastmcp.server.dependencies import get_access_token
    
    token = get_access_token()
    print(f"Token claims: {token}")
    # The GoogleProvider stores user data in token claims
    return {
        # "google_id": token.claims.get("sub"),
        "email": token.claims.get("email"),
        "name": token.claims.get("name"),
        # "picture": token.claims.get("picture"),
        # "locale": token.claims.get("locale")
    }

@mcp.tool
async def get_user_expenses(email_id: str) -> dict:
    """Returns the user's expense details including amount and category from the database.
    
    Args:
        email_id (str): Email ID of the user whose expenses need to be fetched
    """
    try:
        print(f"Fetching expenses for email_id: {email_id}")
        # Query the transactions table filtered by email_id
        response = (
            supabase.table("transactions")
            .select("amount, category, created_at")
            .eq("email_id", email_id)
            .execute()
        )
        
        return {
            "status": "success",
            "expenses": response.data
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
    
