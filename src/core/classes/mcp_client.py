import json
import httpx
from typing import Any, Dict, Optional, Union
from pydantic import BaseModel
from src.core.config import settings

TIMEOUT = 30.0


class McpClient:
    def __init__(self, token: str = None, language: str = "ES"):
        self.base_url = f"http://localhost:{settings.app_port}"
        self.headers = {"language": language}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    def _to_dict(self, data: Union[Dict[str, Any], BaseModel]) -> Dict[str, Any]:
        if isinstance(data, BaseModel):
            return data.model_dump(mode="json")
        return data

    def _handle_response(self, response: httpx.Response) -> str:
        if response.status_code >= 400:
            return json.dumps({"error": True, "status": response.status_code, "detail": response.text})
        return response.text

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> str:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.get(
                f"{self.base_url}{endpoint}", headers=self.headers, params=params
            )
            return self._handle_response(response)

    async def post(self, endpoint: str, data: Optional[Union[Dict[str, Any], BaseModel]] = None) -> str:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            json_data = self._to_dict(data) if data else None
            response = await client.post(
                f"{self.base_url}{endpoint}", headers=self.headers, json=json_data
            )
            return self._handle_response(response)

    async def put(self, endpoint: str, data: Union[Dict[str, Any], BaseModel]) -> str:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            json_data = self._to_dict(data)
            response = await client.put(
                f"{self.base_url}{endpoint}", headers=self.headers, json=json_data
            )
            return self._handle_response(response)

    async def delete(self, endpoint: str) -> str:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.delete(
                f"{self.base_url}{endpoint}", headers=self.headers
            )
            return self._handle_response(response)
