"""MCP-enabled agent base class."""

from typing import Dict, Any, Optional, List
import asyncio
from abc import ABC

from src.agents.base.base_agent import BaseAgent, AgentRole
from src.utils import get_logger

# Note: In production, we would import the actual MCP client
# For now, we'll create a mock interface
class MCPClient:
    """Mock MCP client for development."""
    def __init__(self, server_config: Dict[str, Any]):
        self.server_config = server_config
        self.logger = get_logger("MCPClient")
    
    async def initialize(self) -> None:
        """Initialize MCP connection."""
        self.logger.info(f"Initializing MCP server: {self.server_config}")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call an MCP tool."""
        self.logger.info(f"Calling tool {tool_name} with args: {arguments}")
        # Mock implementation
        return {"status": "success", "result": "mock_result"}
    
    async def close(self) -> None:
        """Close MCP connection."""
        self.logger.info("Closing MCP connection")


class MCPSession:
    """Context manager for MCP sessions."""
    def __init__(self, client: MCPClient):
        self.client = client
    
    async def __aenter__(self):
        await self.client.initialize()
        return self.client
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.close()


class MCPEnabledAgent(BaseAgent, ABC):
    """Base class for agents with MCP capabilities."""
    
    def __init__(
        self,
        agent_id: str,
        role: AgentRole,
        llm_provider: Optional[str] = None,
        mcp_servers: Optional[Dict[str, Dict[str, Any]]] = None,
    ):
        super().__init__(agent_id, role, llm_provider)
        
        self.mcp_servers = mcp_servers or {}
        self.mcp_clients: Dict[str, MCPClient] = {}
        
        # Initialize MCP clients
        for server_name, config in self.mcp_servers.items():
            self.mcp_clients[server_name] = MCPClient(config)
            
        self.logger.info(f"MCP-enabled agent initialized with {len(self.mcp_servers)} servers")
    
    async def use_mcp_tool(
        self,
        server_name: str,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Any:
        """
        Use an MCP tool from a specific server.
        
        Args:
            server_name: Name of the MCP server
            tool_name: Name of the tool to call
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        if server_name not in self.mcp_clients:
            raise ValueError(f"MCP server '{server_name}' not configured")
        
        client = self.mcp_clients[server_name]
        
        try:
            async with MCPSession(client) as session:
                result = await session.call_tool(tool_name, arguments)
                self.logger.info(f"MCP tool {tool_name} executed successfully")
                return result
        except Exception as e:
            self.logger.error(f"Error executing MCP tool {tool_name}: {str(e)}")
            raise
    
    async def list_available_tools(self, server_name: Optional[str] = None) -> Dict[str, List[str]]:
        """
        List available tools from MCP servers.
        
        Args:
            server_name: Optional specific server name
            
        Returns:
            Dictionary of server names to tool lists
        """
        available_tools = {}
        
        servers = {server_name: self.mcp_clients[server_name]} if server_name else self.mcp_clients
        
        for name, client in servers.items():
            # In real implementation, this would query the MCP server
            # For now, return mock data based on server type
            if "filesystem" in name:
                available_tools[name] = ["read_file", "write_file", "list_directory", "create_directory"]
            elif "git" in name:
                available_tools[name] = ["status", "add", "commit", "push", "pull", "log", "diff"]
            elif "shell" in name:
                available_tools[name] = ["execute_command"]
            elif "puppeteer" in name:
                available_tools[name] = ["navigate", "click", "screenshot", "evaluate"]
            else:
                available_tools[name] = []
        
        return available_tools
    
    async def cleanup(self) -> None:
        """Cleanup agent resources including MCP connections."""
        # Close all MCP connections
        for client in self.mcp_clients.values():
            try:
                await client.close()
            except Exception as e:
                self.logger.error(f"Error closing MCP client: {str(e)}")
        
        # Call parent cleanup
        await super().cleanup()
        
        self.logger.info("MCP-enabled agent cleanup completed")
    
    # Common MCP operations for convenience
    
    async def read_file(self, file_path: str) -> str:
        """Read a file using MCP filesystem server."""
        return await self.use_mcp_tool(
            "filesystem",
            "read_file",
            {"path": file_path}
        )
    
    async def write_file(self, file_path: str, content: str) -> None:
        """Write a file using MCP filesystem server."""
        await self.use_mcp_tool(
            "filesystem",
            "write_file",
            {"path": file_path, "content": content}
        )
    
    async def execute_command(self, command: str, cwd: Optional[str] = None) -> Dict[str, Any]:
        """Execute a shell command using MCP shell server."""
        args = {"command": command}
        if cwd:
            args["cwd"] = cwd
            
        return await self.use_mcp_tool(
            "shell",
            "execute_command",
            args
        )
    
    async def git_operation(self, operation: str, **kwargs) -> Any:
        """Perform a git operation using MCP git server."""
        return await self.use_mcp_tool(
            "git",
            operation,
            kwargs
        )