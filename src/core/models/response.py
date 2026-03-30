from typing import Generic, List, TypeVar, Union

from fastapi.responses import JSONResponse
from pydantic import BaseModel
from src.core.enums.message_type import MESSAGE_TYPE
from src.core.enums.notification_type import NOTIFICATION_TYPE

T = TypeVar("T")


class Response(BaseModel, Generic[T]):
    message_type: MESSAGE_TYPE
    notification_type: NOTIFICATION_TYPE
    message: str
    response: Union[T, List[Union[T, None]], None] = None

    def to_http_response(self, status_code: int = 200) -> "JSONResponse | Response[T]":
        if status_code == 200:
            return self
        return JSONResponse(
            status_code=status_code,
            content=self.model_dump(mode="json"),
        )

    @classmethod
    def success(
        cls,
        response: Union[T, List[Union[T, None]], None] = None,
        message: str = "",
        message_type: str = MESSAGE_TYPE.NONE.value,
    ) -> "Response[T]":
        return cls(
            response=response,
            message_type=message_type,
            notification_type=NOTIFICATION_TYPE.SUCCESS.value,
            message=message,
        )

    @classmethod
    def success_temporary_message(
        cls,
        response: Union[T, List[Union[T, None]], None] = None,
        message: str = "",
        message_type: str = MESSAGE_TYPE.TEMPORARY.value,
    ) -> "Response[T]":
        return cls(
            response=response,
            message_type=message_type,
            notification_type=NOTIFICATION_TYPE.SUCCESS.value,
            message=message,
        )

    @classmethod
    def info(
        cls,
        response: Union[T, List[Union[T, None]], None] = None,
        message: str = "",
        message_type: str = MESSAGE_TYPE.STATIC.value,
    ) -> "Response[T]":
        return cls(
            response=response,
            message_type=message_type,
            notification_type=NOTIFICATION_TYPE.INFO.value,
            message=message,
        )

    @classmethod
    def warning(
        cls,
        response: Union[T, List[Union[T, None]], None] = None,
        message: str = "",
        message_type: str = MESSAGE_TYPE.TEMPORARY.value,
    ) -> "Response[T]":
        return cls(
            response=response,
            message_type=message_type,
            notification_type=NOTIFICATION_TYPE.WARNING.value,
            message=message,
        )

    @classmethod
    def error(
        cls,
        response: Union[T, List[Union[T, None]], None] = None,
        message: str = "",
        message_type: str = MESSAGE_TYPE.STATIC.value,
    ) -> "Response[T]":
        return cls(
            response=response,
            message_type=message_type,
            notification_type=NOTIFICATION_TYPE.ERROR.value,
            message=message,
        )
