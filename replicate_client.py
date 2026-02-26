import asyncio
import replicate
import os
from dotenv import load_dotenv
from mcp.client.stdio import stdio_client, StdioServerParameters
from replicate.exceptions import ReplicateError

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

load_dotenv()

os.environ["REPLICATE_API_TOKEN"] = os.getenv("REPLICATE_API_KEY")

SYSTEM_PROMPT = """
You are an assistant controlling database tools.

Available tools:

- create_table_tool → Creates users table
- insert_user_tool → Inserts user
- get_users_tool → Returns users

Respond clearly what action should be taken.
"""

MODEL = "meta/meta-llama-3-8b-instruct"

# ---------------------------------------------------------
# MAIN LOGIC
# ---------------------------------------------------------

async def main():

    server_params = StdioServerParameters(
        command="python",
        args=["mcp_tool.py"]
    )

    async with stdio_client(server_params) as mcp:

        print("✅ Connected to MCP Server (Replicate Client)")

        while True:

            user_input = input("\nYou: ")

            if user_input.lower() in ["exit", "quit"]:
                break

            try:

                output = replicate.run(
                    MODEL,
                    input={
                        "prompt": SYSTEM_PROMPT + "\nUser: " + user_input
                    }
                )

                ai_text = "".join(output)
                print("\nLLM:", ai_text)

            except ReplicateError as e:
                print("\n⚠ Replicate API Error:", e)
                continue

            # -------------------------------------------------
            # SIMPLE TOOL ROUTING
            # -------------------------------------------------

            if "create" in ai_text.lower():

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