"""Daily News MCP 服务入口点。"""

import sys

# psycopg3 async 在 Windows 上需要 SelectorEventLoop（不支持 ProactorEventLoop）
if sys.platform == "win32":
    import asyncio, selectors  # noqa: E401
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )

from daily_news_mcp.app import mcp

# 导入 tools 模块触发所有 @mcp.tool() 装饰器注册
import daily_news_mcp.tools  # noqa: F401


def main():
    """运行 MCP 服务器（默认使用 stdio 传输）。"""
    mcp.run()


if __name__ == "__main__":
    main()
