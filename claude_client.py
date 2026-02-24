import asyncio
import os
from dotenv import load_dotenv
import anthropic
from mcp.client.stdio import stdio_client, StdioServerParameters

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

load_dotenv()

client = anthropic.Anthropic(
    api_key=os.getenv("CLAUDE_API_KEY")
)

SYSTEM_PROMPT = """
You are an assistant controlling database tools.

Available tools:

- create_table_tool → Creates users table
- insert_user_tool → Inserts user
- get_users_tool → Returns users

Respond clearly which action to take.
"""

# ---------------------------------------------------------
# MAIN LOGIC
# ---------------------------------------------------------

async def main():

    server_params = StdioServerParameters(
        command="python",
        args=["mcp_tool.py"]
    )

    async with stdio_client(server_params) as mcp:

        print("✅ Connected to MCP Server (Claude Client)")

        while True:

            user_input = input("\nYou: ")

            if user_input.lower() in ["exit", "quit"]:
                break

            try:

                response = client.messages.create(
                    model="claude-3-haiku-20240307",  # fast + free-tier friendly
                    max_tokens=300,
                    messages=[
                        {"role": "user", "content": SYSTEM_PROMPT + "\nUser: " + user_input}
                    ]
                )

                ai_text = response.content[0].text
                print("\nClaude:", ai_text)

            except Exception as e:
                print("\n⚠ Claude API Error:", e)
                continue

            # -------------------------------------------------
            # SIMPLE TOOL ROUTING
            # -------------------------------------------------

            if "create" in ai_text.lower() and "table" in ai_text.lower():

                result = await mcp.call_tool("create_table_tool", {})
                print("🛠 Tool:", result)

            elif "insert" in ai_text.lower():

                name = input("Name: ")
                email = input("Email: ")

                result = await mcp.call_tool(
                    "insert_user_tool",
                    {"name": name, "email": email}
                )

                print("🛠 Tool:", result)

            elif "get" in ai_text.lower():

                result = await mcp.call_tool("get_users_tool", {})
                print("👥 Users:", result)

asyncio.run(main())