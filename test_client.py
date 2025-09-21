from fastmcp import Client
import asyncio
import json

async def main():
    # The client will automatically handle Google OAuth
    async with Client("http://localhost:8000/mcp/", auth="oauth") as client:
        # First-time connection will open Google login in your browser
        print("✓ Authenticated with Google!")
        
        # Test the protected tool
        result = await client.call_tool("get_user_info")
        user_info = result.content

        # print(f"Google user: {user_info}")
        user_info_text = user_info[0].text

        user_info_dict = json.loads(user_info_text)

        print(f"Google user: {user_info_dict['email']}")
        print(f"Name: {user_info_dict['name']}")

if __name__ == "__main__":
    asyncio.run(main())