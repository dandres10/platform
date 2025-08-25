import httpx
from typing import Dict, Any, Optional
from src.core.models.config import Config
from src.core.config import settings
import asyncio
import json

class MCPController:
    """
    Controller for MCP (Model Context Protocol) service
    Acts as a proxy to the external backend platform API
    """
    
    def __init__(self):
        self.base_url = settings.mcp_base_url
        self.timeout = settings.mcp_timeout
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        config: Config,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Generic method to make HTTP requests to the external API
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            config: Application config
            data: Request body data
            headers: Request headers
        
        Returns:
            Dict containing the API response
        """
        url = f"{self.base_url}{endpoint}"
        
        # Default headers
        request_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Add API key if configured
        if settings.mcp_api_key:
            request_headers["X-API-Key"] = settings.mcp_api_key
        
        # Add custom headers if provided
        if headers:
            request_headers.update(headers)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if method.upper() == "GET":
                    response = await client.get(url, headers=request_headers)
                elif method.upper() == "POST":
                    response = await client.post(url, json=data, headers=request_headers)
                elif method.upper() == "PUT":
                    response = await client.put(url, json=data, headers=request_headers)
                elif method.upper() == "DELETE":
                    response = await client.delete(url, headers=request_headers)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                # Handle response
                if response.status_code >= 400:
                    return {
                        "error": True,
                        "status_code": response.status_code,
                        "message": f"External API error: {response.text}",
                        "details": response.text
                    }
                
                try:
                    return response.json()
                except json.JSONDecodeError:
                    return {
                        "error": True,
                        "message": "Invalid JSON response from external API",
                        "raw_response": response.text
                    }
                    
        except httpx.TimeoutException:
            return {
                "error": True,
                "message": "Request timeout to external API",
                "timeout": self.timeout
            }
        except httpx.RequestError as e:
            return {
                "error": True,
                "message": f"Request error: {str(e)}",
                "exception_type": type(e).__name__
            }
        except Exception as e:
            return {
                "error": True,
                "message": f"Unexpected error: {str(e)}",
                "exception_type": type(e).__name__
            }
    
    # Auth methods
    async def auth_login(
        self, 
        config: Config, 
        request_data: Dict[str, Any], 
        language: str
    ) -> Dict[str, Any]:
        """Login endpoint proxy"""
        headers = {"language": language}
        return await self._make_request(
            method="POST",
            endpoint="/auth/login",
            config=config,
            data=request_data,
            headers=headers
        )
    
    async def auth_refresh_token(
        self, 
        config: Config, 
        language: str, 
        authorization: str
    ) -> Dict[str, Any]:
        """Refresh token endpoint proxy"""
        headers = {
            "language": language,
            "Authorization": authorization
        }
        return await self._make_request(
            method="POST",
            endpoint="/auth/refresh_token",
            config=config,
            headers=headers
        )
    
    async def auth_logout(
        self, 
        config: Config, 
        language: str, 
        authorization: str
    ) -> Dict[str, Any]:
        """Logout endpoint proxy"""
        headers = {
            "language": language,
            "Authorization": authorization
        }
        return await self._make_request(
            method="POST",
            endpoint="/auth/logout",
            config=config,
            headers=headers
        )
    
    async def auth_create_api_token(
        self, 
        config: Config, 
        request_data: Dict[str, Any], 
        language: str, 
        authorization: str
    ) -> Dict[str, Any]:
        """Create API token endpoint proxy"""
        headers = {
            "language": language,
            "Authorization": authorization
        }
        return await self._make_request(
            method="POST",
            endpoint="/auth/create-api-token",
            config=config,
            data=request_data,
            headers=headers
        )
    
    # API Token methods
    async def api_token_save(
        self, 
        config: Config, 
        request_data: Dict[str, Any], 
        language: str, 
        authorization: str
    ) -> Dict[str, Any]:
        """Save API token endpoint proxy"""
        headers = {
            "language": language,
            "Authorization": authorization
        }
        return await self._make_request(
            method="POST",
            endpoint="/api-token",
            config=config,
            data=request_data,
            headers=headers
        )
    
    async def api_token_update(
        self, 
        config: Config, 
        request_data: Dict[str, Any], 
        language: str, 
        authorization: str
    ) -> Dict[str, Any]:
        """Update API token endpoint proxy"""
        headers = {
            "language": language,
            "Authorization": authorization
        }
        return await self._make_request(
            method="PUT",
            endpoint="/api-token",
            config=config,
            data=request_data,
            headers=headers
        )
    
    async def api_token_list(
        self, 
        config: Config, 
        request_data: Dict[str, Any], 
        language: str, 
        authorization: str
    ) -> Dict[str, Any]:
        """List API tokens endpoint proxy"""
        headers = {
            "language": language,
            "Authorization": authorization
        }
        return await self._make_request(
            method="POST",
            endpoint="/api-token/list",
            config=config,
            data=request_data,
            headers=headers
        )
    
    async def api_token_delete(
        self, 
        config: Config, 
        id: str, 
        language: str, 
        authorization: str
    ) -> Dict[str, Any]:
        """Delete API token endpoint proxy"""
        headers = {
            "language": language,
            "Authorization": authorization
        }
        return await self._make_request(
            method="DELETE",
            endpoint=f"/api-token/{id}",
            config=config,
            headers=headers
        )
    
    async def api_token_read(
        self, 
        config: Config, 
        id: str, 
        language: str, 
        authorization: str
    ) -> Dict[str, Any]:
        """Read API token endpoint proxy"""
        headers = {
            "language": language,
            "Authorization": authorization
        }
        return await self._make_request(
            method="GET",
            endpoint=f"/api-token/{id}",
            config=config,
            headers=headers
        )
    
    # Currency Location methods
    async def currency_location_save(
        self, 
        config: Config, 
        request_data: Dict[str, Any], 
        language: str, 
        authorization: str
    ) -> Dict[str, Any]:
        """Save currency location endpoint proxy"""
        headers = {
            "language": language,
            "Authorization": authorization
        }
        return await self._make_request(
            method="POST",
            endpoint="/currency-location",
            config=config,
            data=request_data,
            headers=headers
        )
    
    async def currency_location_update(
        self, 
        config: Config, 
        request_data: Dict[str, Any], 
        language: str, 
        authorization: str
    ) -> Dict[str, Any]:
        """Update currency location endpoint proxy"""
        headers = {
            "language": language,
            "Authorization": authorization
        }
        return await self._make_request(
            method="PUT",
            endpoint="/currency-location",
            config=config,
            data=request_data,
            headers=headers
        )
    
    async def currency_location_list(
        self, 
        config: Config, 
        request_data: Dict[str, Any], 
        language: str, 
        authorization: str
    ) -> Dict[str, Any]:
        """List currency locations endpoint proxy"""
        headers = {
            "language": language,
            "Authorization": authorization
        }
        return await self._make_request(
            method="POST",
            endpoint="/currency-location/list",
            config=config,
            data=request_data,
            headers=headers
        )
    
    async def currency_location_delete(
        self, 
        config: Config, 
        id: str, 
        language: str, 
        authorization: str
    ) -> Dict[str, Any]:
        """Delete currency location endpoint proxy"""
        headers = {
            "language": language,
            "Authorization": authorization
        }
        return await self._make_request(
            method="DELETE",
            endpoint=f"/currency-location/{id}",
            config=config,
            headers=headers
        )
    
    async def currency_location_read(
        self, 
        config: Config, 
        id: str, 
        language: str, 
        authorization: str
    ) -> Dict[str, Any]:
        """Read currency location endpoint proxy"""
        headers = {
            "language": language,
            "Authorization": authorization
        }
        return await self._make_request(
            method="GET",
            endpoint=f"/currency-location/{id}",
            config=config,
            headers=headers
        )
    
    # User methods
    async def user_save(
        self, 
        config: Config, 
        request_data: Dict[str, Any], 
        language: str, 
        authorization: str
    ) -> Dict[str, Any]:
        """Save user endpoint proxy"""
        headers = {
            "language": language,
            "Authorization": authorization
        }
        return await self._make_request(
            method="POST",
            endpoint="/user",
            config=config,
            data=request_data,
            headers=headers
        )
    
    async def user_update(
        self, 
        config: Config, 
        request_data: Dict[str, Any], 
        language: str, 
        authorization: str
    ) -> Dict[str, Any]:
        """Update user endpoint proxy"""
        headers = {
            "language": language,
            "Authorization": authorization
        }
        return await self._make_request(
            method="PUT",
            endpoint="/user",
            config=config,
            data=request_data,
            headers=headers
        )
    
    async def user_list(
        self, 
        config: Config, 
        request_data: Dict[str, Any], 
        language: str, 
        authorization: str
    ) -> Dict[str, Any]:
        """List users endpoint proxy"""
        headers = {
            "language": language,
            "Authorization": authorization
        }
        return await self._make_request(
            method="POST",
            endpoint="/user/list",
            config=config,
            data=request_data,
            headers=headers
        )
    
    async def user_delete(
        self, 
        config: Config, 
        id: str, 
        language: str, 
        authorization: str
    ) -> Dict[str, Any]:
        """Delete user endpoint proxy"""
        headers = {
            "language": language,
            "Authorization": authorization
        }
        return await self._make_request(
            method="DELETE",
            endpoint=f"/user/{id}",
            config=config,
            headers=headers
        )
    
    async def user_read(
        self, 
        config: Config, 
        id: str, 
        language: str, 
        authorization: str
    ) -> Dict[str, Any]:
        """Read user endpoint proxy"""
        headers = {
            "language": language,
            "Authorization": authorization
        }
        return await self._make_request(
            method="GET",
            endpoint=f"/user/{id}",
            config=config,
            headers=headers
        )
