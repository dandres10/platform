import json
import httpx
from typing import Any, Dict, Optional, Type, Union
from pydantic import BaseModel
from src.core.config import settings
from src.core.models.response import Response

TIMEOUT = 30.0

_shared_clients: Dict[str, httpx.AsyncClient] = {}


def _get_shared_client(base_url: str) -> httpx.AsyncClient:
    if base_url not in _shared_clients or _shared_clients[base_url].is_closed:
        _shared_clients[base_url] = httpx.AsyncClient(
            base_url=base_url,
            timeout=TIMEOUT,
            limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
        )
    return _shared_clients[base_url]


class McpClient:
    def __init__(self, token: str = None, language: str = "ES"):
        self.base_url = f"http://localhost:{settings.app_port}"
        self.headers = {"language": language.lower()}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    def _to_dict(self, data: Union[Dict[str, Any], BaseModel]) -> Dict[str, Any]:
        if isinstance(data, BaseModel):
            return data.model_dump(mode="json")
        return data

    def _client(self) -> httpx.AsyncClient:
        return _get_shared_client(self.base_url)

    def _handle_response(self, response: httpx.Response) -> str:
        if response.status_code >= 400:
            return json.dumps({"error": True, "status": response.status_code, "detail": response.text})
        return response.text

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> str:
        response = await self._client().get(endpoint, headers=self.headers, params=params)
        return self._handle_response(response)

    async def post(self, endpoint: str, data: Optional[Union[Dict[str, Any], BaseModel]] = None) -> str:
        json_data = self._to_dict(data) if data else None
        response = await self._client().post(endpoint, headers=self.headers, json=json_data)
        return self._handle_response(response)

    async def put(self, endpoint: str, data: Union[Dict[str, Any], BaseModel]) -> str:
        json_data = self._to_dict(data)
        response = await self._client().put(endpoint, headers=self.headers, json=json_data)
        return self._handle_response(response)

    async def delete(self, endpoint: str) -> str:
        response = await self._client().delete(endpoint, headers=self.headers)
        return self._handle_response(response)

    @staticmethod
    def parse_response(raw: str, response_type: Type) -> Response:
        """Parsea la respuesta raw. Si es error HTTP, retorna error compatible con el tipo."""
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = {"error": True, "detail": "Invalid response"}
        if isinstance(data, dict) and data.get("error"):
            error_msg = data.get("detail", "Error")
            error_json = json.dumps({
                "message_type": "STATIC",
                "notification_type": "ERROR",
                "message": error_msg,
                "response": None,
            })
            return response_type.model_validate_json(error_json)
        return response_type.model_validate_json(raw)
