"""新闻工具 — 通过 REST API 获取新闻数据。

使用 GET /open/free_* 接口作为数据源。
"""

from mcp.server.fastmcp import Context

from daily_news_mcp.app import mcp


@mcp.tool()
async def get_news_categories(ctx: Context) -> dict:
    """Get all available news categories and subcategories.

    Returns a list of categories, each containing subcategories,
    for use with the get_hot_news tool.
    """
    api = ctx.request_context.lifespan_context.api
    try:
        result = await api.get_free_categories()
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e) or repr(e)}


@mcp.tool()
async def get_hot_news(
    category: str,
    ctx: Context,
    subcategory: str = "",
) -> dict:
    """Get hot news and tweets by category.

    Args:
        category: Category key (required). Use get_news_categories to list available keys.
        subcategory: Subcategory key (optional).

    Returns:
        Combined news articles and tweets for the given category.
    """
    api = ctx.request_context.lifespan_context.api
    try:
        result = await api.get_free_hot(
            category=category,
            subcategory=subcategory,
        )
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e) or repr(e)}
