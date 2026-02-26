import asyncio
import re
import httpx  # Needed to catch its specific error
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

# --- CONFIG ---
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL = "mistral" 

SYSTEM_PROMPT = """
You are a database assistant.

INSTRUCTIONS:
1. If the user says "hi" or asks a question, JUST REPLY NORMALLY.

2. If the user wants to CREATE a table, output:
   CMD:CREATE table="<table_name>"
   (Default to "users" if no name is specified)

3. If the user wants to ADD/INSERT a user, output:
   CMD:INSERT name="<name>" email="<email>"

4. If the user wants to LIST users, output:
   CMD:LIST

Do not provide SQL code.
"""

async def ask_llm(prompt):
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(OLLAMA_URL, json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.1}
            })
            resp.raise_for_status() # This will raise an error on 4xx/5xx responses
            return resp.json()["response"]
    # CHANGED: Be specific about network errors
    except httpx.RequestError as e:
        print(f"⚠ LLM Network Error: {e}")
        return ""

async def main():
    server_params = StdioServerParameters(
        command="python", 
        args=["mcp_server.py"], 
        env=None
    )

    print("🔌 Connecting to MCP Server...")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            
            await session.initialize()
            print("✅ Connected! System ready.")
            print("Type: 'create table employees', 'add user [name] [email]', 'list users'\n")

            while True:
                user_input = input("You: ")
                if user_input.lower() in ["exit", "quit"]: break

                ai_text = await ask_llm(f"{SYSTEM_PROMPT}\nUser: {user_input}")
                
                executed = False
                try:
                    create_match = re.search(r'CMD:\s*CREATE\s*(?:table="([^"]+)")?', ai_text)
                    
                    if create_match and "CMD:CREATE" in ai_text:
                        table_name = create_match.group(1) if create_match.group(1) else "users"
                        print(f"🤖 AI Action: Create Table '{table_name}'")
                        res = await session.call_tool("create_table", {"table_name": table_name})
                        print(f"🔧 Result: {res.content[0].text}")
                        executed = True

                    elif match := re.search(r'CMD:\s*INSERT\s+name="([^"]+)"\s+email="([^"]+)"', ai_text):
                        name, email = match.groups()
                        print(f"🤖 AI Action: Add User ({name}, {email})")
                        res = await session.call_tool("insert_user", {"name": name, "email": email})
                        print(f"🔧 Result: {res.content[0].text}")
                        executed = True

                    elif re.search(r"CMD:\s*LIST", ai_text):
                        print("🤖 AI Action: List Users")
                        res = await session.call_tool("get_users", {})
                        print(f"🔧 Result: {res.content[0].text}")
                        executed = True

                    if not executed and ai_text: # Only print chat if it's not empty
                        print(f"🤖 AI Chat: {ai_text.strip()}")
                
                # This is a good place for a general catch, because an error here is
                # likely an unexpected tool or server communication problem.
                except Exception as e:
                    print(f"❌ An unexpected error occurred during tool execution: {e}")

if __name__ == "__main__":
    asyncio.run(main())