import os
import psycopg2
from psycopg2.extras import RealDictCursor
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

# Get Supabase direct database connection string
CONN_STRING = os.environ.get("SUPABASE_DATABASE_URL")

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

# @mcp.tool
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

@mcp.tool
async def execute_transaction_query(query: str, email_id: str) -> dict:
    """Execute a custom SELECT query on the transactions table.
    
    table name: transactions
    columns:
    email_id VARCHAR(255) NOT NULL,          -- identifies the person
    amount NUMERIC(12,2) NOT NULL,           -- transaction amount with 2 decimal places
    currency VARCHAR(10) NOT NULL DEFAULT 'USD', -- ISO 4217 currency code
    transaction_type VARCHAR(50) NOT NULL,   -- e.g., 'debit', 'credit', 'refund'
    category VARCHAR(50) NOT NULL,           -- e.g., 'food', 'clothes', 'shopping', 'other'
    description TEXT,                        -- optional description
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- timestamp

    
    Args:
        query (str): The SELECT query to execute. Must include 'WHERE email_id = %s'
        email_id (str): Email ID of the user whose transactions to query
        
    Example queries:
        "SELECT amount, category FROM transactions WHERE email_id = %s AND created_at < '2026-01-01'"
        "SELECT SUM(amount) FROM transactions WHERE email_id = %s AND transaction_type = 'debit'"
    """
    # Security checks
    query_lower = query.lower().strip()
    if not query_lower.startswith('select'):
        return {
            "status": "error",
            "message": "Only SELECT queries are allowed"
        }
        
    if 'where email_id = %s' not in query_lower:
        return {
            "status": "error",
            "message": "Query must include 'WHERE email_id = %s' clause for security"
        }
        
    try:
        with psycopg2.connect(CONN_STRING) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Execute query with email parameter
                cur.execute(query, (email_id,))
                results = cur.fetchall()
                
                return {
                    "status": "success",
                    "data": results,
                    "count": len(results)
                }
                
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
    
