from  .base import BaseTool
from typing import Dict

class ToolRegistry:
    _tools:Dict[str,BaseTool]={}

    @classmethod
    def register(cls,tool_class):
        tool=tool_class()
        cls._tools[tool.name]=tool
        return tool_class
    
    @classmethod
    def get_tools(cls)->Dict[str,BaseTool]:
        return cls._tools
    
    @classmethod
    def get_for_llm(cls):
        return [
            {
                "type":"function",
                "function":{
                    "name":tool.name,
                    "description":tool.description,
                    "parameters":tool.parameters

                }
            }
            for tool in cls._tools.values()
        ]
registry=ToolRegistry()