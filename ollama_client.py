import asyncio
import httpx
import re
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

# --- Configuration ---
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL = "mistral"

# --- System Prompt ---
SYSTEM_PROMPT = """
You are a database assistant. Your only job is to translate the user's request into a single, specific tool command.
You MUST respond using ONLY ONE of the following commands. Do not add any other text or explanation.

1. Create the user table:
   CREATE_TABLE

2. Insert a new user with their name and email:
   INSERT_USER(name="<user_name>", email="<user_email>")

3. Get all users from the table:
   GET_USERS
"""

async def ask_llm(prompt):
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                OLLAMA_URL,
                json={"model": MODEL, "prompt": prompt, "stream": False}
            )
        response.raise_for_status()
        return response.json()["response"]
    except httpx.RequestError as e:
        print(f"\n⚠ Ollama Connection Error: {e}")
        return ""

async def main():
    # Start the server process
    server_params = StdioServerParameters(command="python", args=["mcp_tool.py"])

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            print("✅ Connected to MCP Server (Ollama Client)")
            
            # --- DEBUGGING STEP: LIST TOOLS ---
            # This proves the server is alive and tells us the EXACT tool names
            print("\n🔍 Checking available tools on server...")
            try:
                tools_response = await session.list_tools()
                available_tools = [t.name for t in tools_response.tools]
                print(f"✅ Found tools: {available_tools}")
            except Exception as e:
                print(f"❌ Could not list tools. The server might be crashing. Error: {e}")
                return # Stop if we can't even list tools
            # ----------------------------------

            print("\nType 'create table', 'add user Bob with email bob@email.com', 'list users', or 'exit'.")

            while True:
                user_input = input("\nYou: ")
                if user_input.lower() in ["exit", "quit"]:
                    break

                full_prompt = f"{SYSTEM_PROMPT}\n\nUser: {user_input}\nAssistant:"
                ai_text = await ask_llm(full_prompt)

                if not ai_text: continue

                command = ai_text.strip()
                print(f"\n🤖 LLM Command: {command}")

                if command.startswith("CREATE_TABLE"):
                    # Call the tool using the simple name found in the list above
                    result = await session.call_tool("create_table_tool", {})
                    print(f"🛠️ Tool Result: {result}")

                elif command.startswith("INSERT_USER"):
                    match = re.search(r'name="([^"]+)",\s*email="([^"]+)"', command)
                    if match:
                        name, email = match.groups()
                        result = await session.call_tool(
                            "insert_user_tool", 
                            {"name": name, "email": email}
                        )
                        print(f"🛠️ Tool Result: {result}")
                    else:
                        print("⚠️ Error: LLM provided INSERT_USER command but arguments could not be parsed.")

                elif command.startswith("GET_USERS"):
                    result = await session.call_tool("get_users_tool", {})
                    print("👥 Users:")
                    if not result:
                        print("  - No users found in the table.")
                    for user in result:
                        print(f"  - ID: {user['id']}, Name: {user['name']}, Email: {user['email']}")
                else:
                    print(f"⚠️ Unexpected LLM Output: {ai_text}")

if __name__ == "__main__":
    asyncio.run(main())