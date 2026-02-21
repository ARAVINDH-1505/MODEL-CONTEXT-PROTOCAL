from mcp.server.fastmcp import FastMCP
from db_connector import create_table, insert_user, get_users

mcp=FastMCP("sql-tools")

@mcp.tool()
def create_table_tool():
    create_table()
    return "Table created successfully."

@mcp.tool()
def insert_user_tool(name: str, email: str):
    rows = insert_user(name, email)
    return {"status": "success", "rows": rows}

@mcp.tool()
def get_users_tool():
    users = get_users()
    return users

if __name__ == "__main__":
    mcp.run()
    print("MCP server is running...")