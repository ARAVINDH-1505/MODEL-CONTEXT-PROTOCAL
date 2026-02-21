import asyncio
from google import genai
from mcp.client.stdio import stdio_client, StdioServerParameters
from dotenv import load_dotenv
import os  

load_dotenv()
# ---------------------------------------------------------
# GEMINI CONFIGURATION
# ---------------------------------------------------------

GEMINI_API_KEY = os.getenv("GEMINI_KEY")

gemini = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """
You are an AI assistant that controls database tools.

Available tools:

1. create_table_tool()
   → Creates users table

2. insert_user_tool(name, email)
   → Inserts new user

3. get_users_tool()
   → Returns all users

Decide which tool to use based on user request.
Respond clearly.
"""

# ---------------------------------------------------------
# MAIN CLIENT LOGIC
# ---------------------------------------------------------

async def main():

    server_params = StdioServerParameters(
        command="python",
        args=["mcp_tool.py"]   # MCP server file
    )

    async with stdio_client(server_params) as mcp:

        print("✅ Connected to MCP Server")

        while True:

            user_input = input("\nYou: ")

            if user_input.lower() in ["exit", "quit"]:
                print("👋 Exiting...")
                break

            # -------------------------------------------------
            # GEMINI DECISION
            # -------------------------------------------------

            response = gemini.models.generate_content(
                model="gemini-2.0-flash",
                contents=SYSTEM_PROMPT + "\nUser: " + user_input
            )

            ai_text = response.text
            print("\nGemini:", ai_text)

            # -------------------------------------------------
            # SIMPLE TOOL ROUTING (Practice Level)
            # -------------------------------------------------

            if "create_table" in ai_text.lower():

                result = await mcp.call_tool("create_table_tool", {})
                print("🛠 Tool Response:", result)

            elif "insert_user" in ai_text.lower():

                name = input("Enter name: ")
                email = input("Enter email: ")

                result = await mcp.call_tool(
                    "insert_user_tool",
                    {"name": name, "email": email}
                )

                print("🛠 Tool Response:", result)

            elif "get_users" in ai_text.lower():

                result = await mcp.call_tool("get_users_tool", {})
                print("👥 Users:", result)

            else:
                print("⚠ Gemini did not select a valid tool.")

# ---------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------

asyncio.run(main())