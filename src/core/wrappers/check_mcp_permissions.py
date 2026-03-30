from typing import List


def check_mcp_permissions(permissions: List[str]):
    """Anota permisos requeridos en una tool MCP. No altera ejecución."""
    def decorator(func):
        func._mcp_permissions = permissions
        return func
    return decorator
