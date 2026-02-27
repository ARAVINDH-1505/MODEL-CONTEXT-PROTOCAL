# 🧠 MCP Database Assistant — Ollama Mistral + MySQL

A local AI-powered database assistant that uses **Ollama (Mistral)** as the LLM, **Model Context Protocol (MCP)** as the tool communication layer, and **MySQL** as the backend — all running **100% locally** with no cloud API required.

> Additional clients for **Claude**, **OpenAI**, and **Gemini** are also included in this repo.

---

## 📁 Project Structure

```
├── mcp_client.py              ← 🔑 Main client — uses Ollama/Mistral LLM to decide tools
├── mcp_server.py              ← 🔑 MCP server — exposes DB tools via MCP protocol
├── db_connector.py            ← 🔑 MySQL connector — create_table, insert_user, get_users
├── mcp_tool.py                ← Simplified MCP tool server (used by Claude/OpenAI/Gemini clients)
├── claude_client.py           ← Claude API client
├── openai_client.py           ← OpenAI API client
├── gemini_client.py           ← Gemini API client
├── .env                       ← Environment variables (API keys, DB credentials)
├── .gitignore
└── README.md
```

---

## 🏗️ Architecture — How It All Connects

```
┌─────────────────────────────────────────────────────────────────────┐
│                        YOUR LOCAL MACHINE                           │
│                                                                     │
│   ┌──────────────────────────────────────────────────────────────┐  │
│   │                     mcp_client.py                            │  │
│   │                                                              │  │
│   │   1. Takes user input (e.g. "add user John john@email.com") │  │
│   │                          │                                   │  │
│   │                          ▼                                   │  │
│   │   ┌──────────────────────────────────┐                       │  │
│   │   │     Ollama — Mistral Model       │  ← runs locally        │  │
│   │   │  http://127.0.0.1:11434          │    no internet needed  │  │
│   │   │                                  │                       │  │
│   │   │  Reads SYSTEM_PROMPT, decides    │                       │  │
│   │   │  which CMD to output:            │                       │  │
│   │   │   • CMD:CREATE table="users"     │                       │  │
│   │   │   • CMD:INSERT name="X" email="" │                       │  │
│   │   │   • CMD:LIST                     │                       │  │
│   │   └──────────────────┬───────────────┘                       │  │
│   │                      │                                        │  │
│   │   2. Regex parses CMD from LLM output                        │  │
│   │                      │                                        │  │
│   │                      ▼                                        │  │
│   │   ┌────────────────────────────────────────┐                  │  │
│   │   │  MCP Client (stdio_client + session)   │                  │  │
│   │   │  Calls: session.call_tool(...)         │                  │  │
│   │   └──────────────────┬─────────────────────┘                  │  │
│   └──────────────────────┼───────────────────────────────────────┘  │
│                           │  (stdin/stdout — subprocess pipe)        │
│                           ▼                                          │
│   ┌──────────────────────────────────────────────────────────────┐  │
│   │                     mcp_server.py                            │  │
│   │                                                              │  │
│   │   FastMCP server exposing 3 tools:                          │  │
│   │   ┌─────────────────┐  ┌──────────────────┐  ┌──────────┐   │  │
│   │   │  create_table   │  │   insert_user    │  │get_users │   │  │
│   │   │  (table_name)   │  │  (name, email)   │  │   ()     │   │  │
│   │   └────────┬────────┘  └────────┬─────────┘  └────┬─────┘   │  │
│   └────────────┼────────────────────┼────────────────┼──────────┘  │
│                │                    │                │               │
│                └────────────────────┼────────────────┘               │
│                                     │                                 │
│                                     ▼                                 │
│   ┌──────────────────────────────────────────────────────────────┐  │
│   │                     db_connector.py                          │  │
│   │                                                              │  │
│   │   mysql.connector → MySQL Database "aravindh"               │  │
│   │                                                              │  │
│   │   • create_table(table_name)  → CREATE TABLE IF NOT EXISTS  │  │
│   │   • insert_user(name, email)  → INSERT INTO users           │  │
│   │   • get_users()               → SELECT * FROM users         │  │
│   └──────────────────────────────────────────────────────────────┘  │
│                                     │                                 │
│                                     ▼                                 │
│                    ┌────────────────────────────┐                    │
│                    │    MySQL Server (local)     │                    │
│                    │    Database: aravindh       │                    │
│                    │    Table:    users          │                    │
│                    └────────────────────────────┘                    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Request Flow (Step-by-Step)

```
User types: "add user John john@example.com"
        │
        ▼
[mcp_client.py] sends to Ollama/Mistral:
    SYSTEM_PROMPT + "User: add user John john@example.com"
        │
        ▼
[Mistral LLM] returns:
    CMD:INSERT name="John" email="john@example.com"
        │
        ▼
[mcp_client.py] regex matches CMD:INSERT
    → calls: session.call_tool("insert_user", {"name": "John", "email": "..."})
        │
        ▼  (via MCP stdio pipe)
[mcp_server.py] receives tool call
    → calls: insert_user("John", "john@example.com")
        │
        ▼
[db_connector.py] executes:
    INSERT INTO users (name, email) VALUES ('John', 'john@example.com')
        │
        ▼
[MySQL] → stores row → returns rowcount
        │
        ▼
[mcp_server.py] → "User inserted successfully."
        │
        ▼
[mcp_client.py] prints: 🔧 Result: User inserted successfully.
```

---

## ⚙️ Setup & Installation

### 1. Install Ollama and Pull Mistral

```bash
# Install Ollama (macOS/Linux)
curl -fsSL https://ollama.com/install.sh | sh

# Pull the Mistral model locally
ollama pull mistral

# Verify it's running
ollama run mistral "hello"
```

Ollama serves the model at `http://127.0.0.1:11434` by default.

### 2. Clone the Repo and Install Python Dependencies

```bash
git clone <your-repo-url>
cd <repo-folder>

pip install anthropic mcp mysql-connector-python python-dotenv openai google-genai httpx
```

### 3. Set Up Your `.env` File

```env
# MySQL credentials
DB_HOST=localhost
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password

# Optional — only needed for Claude/OpenAI/Gemini clients
CLAUDE_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GEMINI_KEY=AIza...
```

### 4. Create the MySQL Database

```sql
CREATE DATABASE aravindh;
```

---

## 🚀 Running the App

### Local Mistral Version (Primary)

```bash
# Make sure Ollama is running in the background
ollama serve

# Run the MCP client
python mcp_client.py
```

### Cloud LLM Versions (Optional)

```bash
python claude_client.py    # Claude (Anthropic)
python openai_client.py    # GPT-4.1-mini (OpenAI)
python gemini_client.py    # Gemini Flash (Google)
```

---

## 💬 Example Interactions

```
You: create table users
🤖 AI Action: Create Table 'users'
🔧 Result: Table 'users' created successfully.

You: add user Alice alice@example.com
🤖 AI Action: Add User (Alice, alice@example.com)
🔧 Result: User inserted successfully.

You: list all users
🤖 AI Action: List Users
🔧 Result: [{'id': 1, 'name': 'Alice', 'email': 'alice@example.com'}]
```

---

## 🔑 Key Concepts

| Component | Role |
|---|---|
| **Ollama** | Runs Mistral locally via HTTP API at port 11434 |
| **Mistral** | LLM that parses user intent and outputs structured `CMD:` commands |
| **MCP (Model Context Protocol)** | Standardized protocol for LLMs to call tools via stdio subprocess |
| **mcp_client.py** | Orchestrates the LLM → tool decision loop |
| **mcp_server.py** | Hosts tools as MCP-compatible endpoints |
| **db_connector.py** | Raw MySQL operations, separated from tool logic |
| **FastMCP** | Python framework that simplifies building MCP servers |

---

## 🛠️ Tool Reference

| Tool Name | Parameters | Description |
|---|---|---|
| `create_table` | `table_name: str = "users"` | Creates table if it doesn't exist |
| `insert_user` | `name: str, email: str` | Inserts a new user row |
| `get_users` | *(none)* | Returns all users as a list |

---

## 📦 Dependencies

```
anthropic
openai
google-genai
mcp
mysql-connector-python
python-dotenv
httpx
```

---

## 🧩 Multi-Client Support

This repo supports **four different LLM backends** all connecting to the same MCP tool layer:

```
Claude Client   ──┐
OpenAI Client   ──┤──► mcp_tool.py  ──► db_connector.py ──► MySQL
Gemini Client   ──┘

Mistral Client  ──────► mcp_server.py ──► db_connector.py ──► MySQL
```

> The Mistral path uses a more robust MCP `ClientSession` pattern; the others use a simpler `stdio_client` with keyword-based routing.

---

## 📝 Notes

- The `.env` file is **git-ignored** — never commit your credentials.
- Mistral runs **fully offline** once pulled — no API key or internet needed.
- Email field has a `UNIQUE` constraint — duplicate emails will fail gracefully.
- Table names are validated as alphanumeric to prevent SQL injection.
