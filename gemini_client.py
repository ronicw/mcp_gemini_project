import asyncio
import json
from contextlib import AsyncExitStack
from typing import Any, Dict, List, Optional
import os

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import google.generativeai as genai
from google.generativeai import types

# Load environment variables (e.g., GEMINI_API_KEY)
load_dotenv(".env")

class MCPGeminiClient:
    """Client for interacting with Gemini models using MCP tools."""

    def __init__(self, model: str = "gemini-2.5-pro"):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.model_name = model
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel(self.model_name)
        self.stdio: Optional[Any] = None
        self.write: Optional[Any] = None

    async def connect_to_server(self, server_script_path: str = "gemini_server.py"):
        server_params = StdioServerParameters(
            command="python",
            args=[server_script_path],
        )
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        await self.session.initialize()

        tools_result = await self.session.list_tools()
        def strip_title(schema):
            if isinstance(schema, dict):
                return {k: strip_title(v) for k, v in schema.items() if k != "title"}
            elif isinstance(schema, list):
                return [strip_title(item) for item in schema]
            else:
                return schema
        print("\nConnected to server with tools:")
        for tool in tools_result.tools:
            print(f"  - {tool.name}: {tool.description}  Parameters: {json.dumps(strip_title(tool.inputSchema), indent=4)}")

    async def get_mcp_tools(self) -> List[types.Tool]:
        tools_result = await self.session.list_tools()
        def strip_title(schema):
            if isinstance(schema, dict):
                return {k: strip_title(v) for k, v in schema.items() if k != "title"}
            elif isinstance(schema, list):
                return [strip_title(item) for item in schema]
            else:
                return schema
            
        return [
            types.Tool(
                function_declarations=[
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": strip_title(tool.inputSchema),
                    }
                ]
            )
            for tool in tools_result.tools
        ]

    async def process_query(self, query: str) -> str:
        tools = await self.get_mcp_tools()

        response = self.model.generate_content(
            [query],
            generation_config=types.GenerationConfig(temperature=0),
            tools=tools,
        )

        part = response.candidates[0].content.parts[0]

        messages = [query]

        if hasattr(part, "function_call"):
            function_call = part.function_call
            result = await self.session.call_tool(function_call.name, arguments=function_call.args)

            messages.append(result.content[0].text)

            final_response = self.model.generate_content(
                messages,
                generation_config=types.GenerationConfig(temperature=0),
                tools=tools,
            )
            return final_response.candidates[0].content.parts[0].text

        return part.text

    async def cleanup(self):
        await self.exit_stack.aclose()

async def main():
    client = MCPGeminiClient(model="gemini-2.5-flash")  # or "gemini-4o" if supported
    # client = MCPGeminiClient(model="gemini-2.5-pro")
    await client.connect_to_server("gemini_server.py")

    query = "What are the different Mortgage Types that Fannie Mae will buy?"
    response = await client.process_query(query)
    print(f"\n{query}\nResponse: {response}")

    # Test weather query with specific coordinates
    city = "Hyderabad"
    latitude = 17.3850
    longitude = 78.4867
    weather_prompt = f"What is the weather like in {city} whose latitude is {latitude} and longitude is {longitude}?"
    response = await client.process_query(weather_prompt)
    print(f"\n{weather_prompt}\nResponse: {response}")

    city = "Osage,Iowa"
    weather_prompt = f"What is the weather like in {city}?"
    response = await client.process_query(weather_prompt)
    print(f"\n{weather_prompt}\nResponse: {response}") 

    await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
