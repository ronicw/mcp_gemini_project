import unittest
from unittest.mock import AsyncMock, patch
import os
import sys
import asyncio
from unittest.mock import Mock

# Import the client class
from gemini_client import MCPGeminiClient

class TestMCPGeminiClient(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        os.environ["GEMINI_API_KEY"] = "test-key"
        self.client = MCPGeminiClient(model="gemini-2.5-pro")

    @patch("gemini_client.ClientSession")
    @patch("gemini_client.stdio_client")
    async def test_connect_to_server(self, mock_stdio_client, mock_ClientSession):
        mock_stdio_client.return_value.__aenter__.return_value = (AsyncMock(), AsyncMock())
        mock_ClientSession.return_value.__aenter__.return_value = AsyncMock()
        await self.client.connect_to_server("gemini-server.py")
        self.assertIsNotNone(self.client.session)

    @patch.object(MCPGeminiClient, "get_mcp_tools", new_callable=AsyncMock)
    async def test_process_query(self, mock_get_mcp_tools):
        mock_get_mcp_tools.return_value = [AsyncMock()]
        mock_response = AsyncMock()
        mock_response.candidates = [AsyncMock()]
        mock_response.candidates[0].content.parts = [AsyncMock()]
        mock_response.candidates[0].content.parts[0].text = "Test response"
        self.client.model.generate_content = Mock(return_value=mock_response)
        # Mock session and call_tool
        mock_session = AsyncMock()
        mock_call_tool_result = AsyncMock()
        mock_call_tool_result.content = [AsyncMock()]
        mock_call_tool_result.content[0].text = "Tool result"
        mock_session.call_tool.return_value = mock_call_tool_result
        self.client.session = mock_session
        result = await self.client.process_query("Test query")
        self.assertEqual(result, "Test response")

    async def test_cleanup(self):
        self.client.exit_stack.aclose = AsyncMock()
        await self.client.cleanup()
        self.client.exit_stack.aclose.assert_awaited()

if __name__ == "__main__":
    unittest.main()
