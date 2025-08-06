"""
Base tool class for CRY-A-4MCP MCP tools.

This module provides the abstract base class that all MCP tools
should inherit from, ensuring consistent interface and behavior.
"""

import json
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import structlog
from pydantic import BaseModel, ValidationError

from ..config import Settings


class ToolError(Exception):
    """Base exception for tool errors."""
    pass


class ToolValidationError(ToolError):
    """Exception raised when tool input validation fails."""
    pass


class ToolExecutionError(ToolError):
    """Exception raised when tool execution fails."""
    pass


class BaseTool(ABC):
    """
    Abstract base class for all CRY-A-4MCP tools.
    
    This class provides common functionality for tool initialization,
    input validation, error handling, and logging.
    """
    
    def __init__(self, settings: Settings) -> None:
        """Initialize the tool."""
        self.settings = settings
        self.logger = structlog.get_logger(self.__class__.__name__)
        self._initialized = False
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description."""
        pass
    
    @property
    @abstractmethod
    def input_schema(self) -> Dict[str, Any]:
        """JSON schema for tool input validation."""
        pass
    
    async def initialize(self) -> None:
        """
        Initialize the tool.
        
        This method is called once when the server starts.
        Override in subclasses to perform tool-specific initialization.
        """
        if self._initialized:
            return
        
        self.logger.info("Initializing tool", tool_name=self.name)
        await self._initialize_impl()
        self._initialized = True
        self.logger.info("Tool initialized", tool_name=self.name)
    
    async def _initialize_impl(self) -> None:
        """
        Tool-specific initialization implementation.
        
        Override this method in subclasses to perform initialization.
        """
        pass
    
    def validate_input(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate tool input arguments.
        
        Args:
            arguments: Raw input arguments
            
        Returns:
            Validated arguments
            
        Raises:
            ToolValidationError: If validation fails
        """
        try:
            # Basic JSON schema validation would go here
            # For now, just return the arguments as-is
            return arguments
        except Exception as e:
            raise ToolValidationError(f"Input validation failed: {str(e)}") from e
    
    async def execute(self, arguments: Dict[str, Any]) -> str:
        """
        Execute the tool with given arguments.
        
        Args:
            arguments: Tool input arguments
            
        Returns:
            Tool execution result as JSON string
            
        Raises:
            ToolError: If execution fails
        """
        if not self._initialized:
            raise ToolExecutionError("Tool not initialized")
        
        try:
            # Validate input
            validated_args = self.validate_input(arguments)
            
            # Log execution start
            self.logger.info(
                "Executing tool",
                tool_name=self.name,
                arguments_keys=list(validated_args.keys()),
            )
            
            # Execute tool-specific logic
            result = await self._execute_impl(validated_args)
            
            # Log execution success
            self.logger.info(
                "Tool execution completed",
                tool_name=self.name,
                success=True,
            )
            
            # Return result as JSON string
            if isinstance(result, str):
                return result
            else:
                return json.dumps(result, indent=2, default=str)
                
        except ToolError:
            # Re-raise tool errors as-is
            raise
        except Exception as e:
            # Wrap other exceptions
            self.logger.error(
                "Tool execution failed",
                tool_name=self.name,
                error=str(e),
                exc_info=True,
            )
            raise ToolExecutionError(f"Tool execution failed: {str(e)}") from e
    
    @abstractmethod
    async def _execute_impl(self, arguments: Dict[str, Any]) -> Any:
        """
        Tool-specific execution implementation.
        
        Args:
            arguments: Validated input arguments
            
        Returns:
            Tool execution result
        """
        pass

