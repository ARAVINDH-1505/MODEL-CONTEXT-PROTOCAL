import sys
from mcp.server.fastmcp import FastMCP
from db_connector import create_table, insert_user, get_users
from typing import List, Dict

# Initialize without a specific name first to ensure no confusion
mcp = FastMCP("demo") 

@mcp.tool()
def create_table_tool() -> str:
    """A tool to create the necessary 'users' database table."""
    create_table()
    return "Table 'users' created or already exists."

@mcp.tool()
def insert_user_tool(name: str, email: str) -> Dict:
    """A tool to insert a new user with a name and email."""
    rows_affected = insert_user(name, email)
    if rows_affected > 0:
        return {"status": "success", "rows_affected": rows_affected}
    else:
        return {"status": "failed", "reason": "User could not be inserted. Check for duplicate email."}

@mcp.tool()
def get_users_tool() -> List[Dict]:
    """A tool to retrieve a list of all users from the database."""
    return get_users()

if __name__ == "__main__":
    mcp.run()