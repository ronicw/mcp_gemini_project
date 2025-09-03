# MCP Gemini Project

This project integrates Google Gemini models with the Model Context Protocol (MCP) to enable tool-augmented AI agent workflows.

## Features
- Connects to a local MCP server and lists available tools
- Uses Google Gemini models (e.g., gemini-2.5-pro) for natural language queries
- Supports tool-calling via MCP (e.g., weather, knowledge base)
- Async Python client (gemini_client.py) for interacting with Gemini models and MCP tools
- MCP server (gemini_server.py) exposing tools such as weather and knowledge base queries
- Unit tests in test_gemini_client.py

## Requirements
- Python 3.13+
- `google-generativeai` (latest)
- `python-dotenv`
- MCP Python package
- All dependencies should be installed in a virtual environment (see `gemini_agent_env/`)

## Setup
1. Clone the repository
2. Create and activate a Python virtual environment:
   ```powershell
   python -m venv gemini_agent_env
   .\gemini_agent_env\Scripts\activate
   ```
3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
4. Add your Gemini API key to a `.env` file:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

## Usage
1. Start the MCP server:
   ```powershell
   python gemini_server.py
   ```
2. Run the Gemini client:
   ```powershell
   python gemini_client.py
   ```

## File Structure
- `gemini_client.py` — Async client for Gemini and MCP tools
- `gemini_server.py` — MCP server exposing tools
- `tets_gemini_client.py` — Unit tests for the client
- `data/knowledge_base.json` — Example knowledge base for tool queries
- `gemini_agent_env/` — Python virtual environment

## Example Query
```
What are the different Mortgage Types that FannieMae will buy?
```

## License
MIT
