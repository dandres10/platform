from typing import List


def check_mcp_roles(roles: List[str]):
    """Anota roles permitidos en una tool MCP. No altera ejecución."""
    def decorator(func):
        func._mcp_roles = roles
        return func
    return decorator
