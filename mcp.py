from typing import Dict, List, Optional, Type, Callable
import json
from dataclasses import dataclass


@dataclass
class ToolConfig:
    """工具配置参数类"""
    tool_name: str
    description: str
    parameters: Dict[str, str]  # 参数名: 描述
    required_params: List[str]  # 必填参数
    handler: Optional[Callable] = None  # 工具处理函数


class MCPTool:
    """MCP工具基类"""
    def __init__(self, config: ToolConfig):
        self.config = config
        self.validate_config()

    def validate_config(self):
        """验证配置是否合法"""
        if not self.config.tool_name:
            raise ValueError("工具名称不能为空")
        if not self.config.parameters:
            raise ValueError(f"工具{self.config.tool_name}未定义参数")
        for param in self.config.required_params:
            if param not in self.config.parameters:
                raise ValueError(f"工具{self.config.tool_name}缺少必填参数: {param}")

    def call(self, **kwargs) -> Dict:
        """调用工具"""
        # 验证输入参数
        for param in self.config.required_params:
            if param not in kwargs:
                return {"status": "error", "message": f"缺少必填参数: {param}"}

        # 调用处理函数
        if not self.config.handler:
            return {"status": "error", "message": "未设置工具处理函数"}

        try:
            result = self.config.handler(** kwargs)
            return {"status": "success", "result": result}
        except Exception as e:
            return {"status": "error", "message": str(e)}


class ToolRegistry:
    """工具注册表，管理所有可用的MCP工具"""
    _instance = None
    _tools: Dict[str, MCPTool] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def register_tool(self, tool: MCPTool) -> None:
        """注册工具"""
        if tool.config.tool_name in self._tools:
            raise ValueError(f"工具{tool.config.tool_name}已存在")
        self._tools[tool.config.tool_name] = tool

    def get_tool(self, tool_name: str) -> Optional[MCPTool]:
        """获取工具"""
        return self._tools.get(tool_name)

    def list_tools(self) -> List[str]:
        """列出所有工具"""
        return list(self._tools.keys())


class MCPService:
    """MCP服务主类，负责配置和调用工具"""
    def __init__(self):
        self.registry = ToolRegistry()

    def configure_tool(self, config: ToolConfig) -> Dict:
        """配置并注册工具"""
        try:
            tool = MCPTool(config)
            self.registry.register_tool(tool)
            return {"status": "success", "message": f"工具{config.tool_name}配置成功"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def call_tool(self, tool_name: str, **kwargs) -> Dict:
        """调用已配置的工具"""
        tool = self.registry.get_tool(tool_name)
        if not tool:
            return {"status": "error", "message": f"工具{tool_name}未找到"}
        return tool.call(** kwargs)

    def get_tool_config(self, tool_name: str) -> Optional[ToolConfig]:
        """获取工具配置"""
        tool = self.registry.get_tool(tool_name)
        return tool.config if tool else None


# 示例用法
if __name__ == "__main__":
    # 创建MCP服务
    mcp_service = MCPService()

    # 示例工具1: 加法工具
    def add_handler(a: int, b: int) -> int:
        return a + b

    add_config = ToolConfig(
        tool_name="add",
        description="两数相加工具",
        parameters={"a": "第一个数", "b": "第二个数"},
        required_params=["a", "b"],
        handler=add_handler
    )
    print(mcp_service.configure_tool(add_config))

    # 调用加法工具
    print(mcp_service.call_tool("add", a=1, b=2))

    # 示例工具2: JSON格式化工具
    def json_format_handler(data: Dict) -> str:
        return json.dumps(data, indent=2, ensure_ascii=False)

    json_config = ToolConfig(
        tool_name="json_format",
        description="JSON格式化工具",
        parameters={"data": "需要格式化的字典数据"},
        required_params=["data"],
        handler=json_format_handler
    )
    print(mcp_service.configure_tool(json_config))

    # 调用JSON格式化工具
    print(mcp_service.call_tool("json_format", data={"name": "MCP", "version": "1.0"}))

    # 列出所有工具
    print("已注册工具:", mcp_service.registry.list_tools())