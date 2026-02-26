from mcp.server.fastmcp import FastMCP
from db_connector import create_table, insert_user, get_users
# We need to access the error type to catch it
from mysql.connector import Error as MySQLError 


mcp = FastMCP("mysqldb")

@mcp.tool(name="create_table")
def create_table_tool(table_name: str = "users") -> str:
    """Creates a table with the given name (default: users)."""
    try:
        create_table(table_name)
        return f"Table '{table_name}' created successfully."
    # CHANGED: Catch the two specific errors we expect from our db_connector
    except (ValueError, MySQLError) as e:
        return f"Failed to create table: {str(e)}"

@mcp.tool(name="insert_user")
def insert_user_tool(name: str, email: str) -> str:
    """Inserts a user into the 'users' table."""
    try:
        rows = insert_user(name, email)
        if rows > 0:
            return "User inserted successfully."
        return "Failed to insert user (Email might exist)."
    except MySQLError as e:
        return f"Database error while inserting user: {str(e)}"

@mcp.tool(name="get_users")
def get_users_tool() -> str:
    """Returns a list of all users from the 'users' table."""
    users = get_users()
    if not users:
        return "No users found."
    return str(users)

if __name__ == "__main__":
    mcp.run()