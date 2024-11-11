from pydantic import UUID4
from src.core.config import settings
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.models.params_ws import ParamsWS
from src.core.models.response import Response
from src.core.methods.get_config import get_config, get_config_ws
from src.core.enums.permission_type import PERMISSION_TYPE
from src.core.models.ws_request import WSRequest
from src.core.wrappers.check_permissions import check_permissions
from src.core.wrappers.execute_transaction import execute_transaction_route
from fastapi import APIRouter, Depends, status, WebSocket, WebSocketDisconnect
from src.domain.models.entities.user.index import (
    UserDelete,
    UserRead,
    UserSave,
    UserUpdate,
)
from src.infrastructure.web.controller.entities.user_controller import (
    UserController,
)
import asyncio


user_router = APIRouter(
    prefix="/user", tags=["User"], responses={404: {"description": "Not found"}}
)

user_controller = UserController()


@user_router.post("", status_code=status.HTTP_200_OK, response_model=Response)
@check_permissions([PERMISSION_TYPE.SAVE.value])
@execute_transaction_route(enabled=settings.has_track)
async def save(params: UserSave, config: Config = Depends(get_config)) -> Response:
    return await user_controller.save(config=config, params=params)


@user_router.put("", status_code=status.HTTP_200_OK, response_model=Response)
@check_permissions([PERMISSION_TYPE.UPDATE.value])
@execute_transaction_route(enabled=settings.has_track)
async def update(params: UserUpdate, config: Config = Depends(get_config)) -> Response:
    return await user_controller.update(config=config, params=params)


@user_router.post("/list", status_code=status.HTTP_200_OK, response_model=Response)
@check_permissions([PERMISSION_TYPE.LIST.value])
@execute_transaction_route(enabled=settings.has_track)
async def list(params: Pagination, config: Config = Depends(get_config)) -> Response:
    return await user_controller.list(config=config, params=params)


@user_router.delete("/{id}", status_code=status.HTTP_200_OK, response_model=Response)
@check_permissions([PERMISSION_TYPE.DELETE.value])
@execute_transaction_route(enabled=settings.has_track)
async def delete(id: UUID4, config: Config = Depends(get_config)) -> Response:
    build_params = UserDelete(id=id)
    return await user_controller.delete(config=config, params=build_params)


@user_router.get("/{id}", status_code=status.HTTP_200_OK, response_model=Response)
@check_permissions([PERMISSION_TYPE.READ.value])
@execute_transaction_route(enabled=settings.has_track)
async def read(id: UUID4, config: Config = Depends(get_config)) -> Response:
    build_params = UserRead(id=id)
    return await user_controller.read(config=config, params=build_params)


@user_router.websocket("/traceability_by_code_websocket")
async def traceability_by_code_websocket(websocket: WebSocket):
    token = websocket.query_params.get("token")
    language = websocket.query_params.get("language")
    traceability_code = websocket.query_params.get("traceability_code")
    company_id = websocket.query_params.get("company_id")
    config: Config = await get_config_ws(
        ws_resquest=WSRequest(language=language, token=token)
    )

    if not token or not language or not traceability_code:
        await websocket.close(code=1008)
        return

    await websocket.accept()

    pagination_params = ParamsWS(limit=0, offset=0)
    last_data = None

    async def receive_messages():
        nonlocal pagination_params
        try:
            while True:
                message = await websocket.receive_text()
                print("Mensaje recibido del cliente:", message)

                try:
                    params = ParamsWS.model_validate_json(message)
                    pagination_params = params
                    print("Paginación actualizada:", pagination_params)
                except ValueError:
                    print("Mensaje no válido para actualizar la paginación")

                await websocket.send_text("data")
        except WebSocketDisconnect:
            print("Cliente desconectado al recibir mensaje.")
            return

    receive_task = asyncio.create_task(receive_messages())

    try:
        while True:

            result = [
                {
                    "key": "2a608d44-e45f-4ce4-a4fa-e0d0969b44e6",
                    "tracking_code": "2a608d44-e45f-4ce4-a4fa-e0d0969b44e6",
                    "update": "2024-11-06 08:45:45.845186",
                    "data": [
                        {"name": "email", "value": "marlon@goluti.com"},
                        {"name": "nombre", "value": "marlon"},
                        {"name": "nit", "value": "123123123"},
                        {"name": "password", "value": "marlon"},
                    ],
                    "events": [
                        {
                            "id": "72763b66-c9d5-4880-88a1-bef336873225",
                            "name": "mail_registration",
                            "code": "MAIL_REG",
                            "order": 1,
                            "event_executed": True,
                            "data_by_event": [
                                {"name": "email", "value": "marlon@goluti.com"},
                                {"name": "nombre", "value": "marlon"},
                            ],
                        },
                        {
                            "id": "c8e2065d-b11e-4b8a-b6df-b44d5d2896c2",
                            "name": "opening_link",
                            "code": "OPEN_LINK",
                            "order": 2,
                            "event_executed": True,
                            "data_by_event": [{"name": "nit", "value": "123123123"}],
                        },
                        {
                            "id": "aa2fdc48-ba8a-459b-8a3a-8d94d2781ca4",
                            "name": "company_contact_information",
                            "code": "COMP_INFO",
                            "order": 3,
                            "event_executed": False,
                            "data_by_event": [],
                        },
                        {
                            "id": "3764ec6a-ef18-4e74-bb6b-54fcdb1dfa12",
                            "name": "nit_validation",
                            "code": "NIT_VAL",
                            "order": 4,
                            "event_executed": False,
                            "data_by_event": [],
                        },
                        {
                            "id": "efb331e4-71da-4558-9104-ae9d9010796c",
                            "name": "data_processing",
                            "code": "DATA_PROC",
                            "order": 5,
                            "event_executed": False,
                            "data_by_event": [],
                        },
                        {
                            "id": "131051aa-913a-46d6-9418-5c34c2199c20",
                            "name": "metamap_flow",
                            "code": "META_FLOW",
                            "order": 6,
                            "event_executed": False,
                            "data_by_event": [],
                        },
                        {
                            "id": "5b3374af-1492-4018-b7ae-9713f3665b53",
                            "name": "create_password",
                            "code": "CREATE_PASS",
                            "order": 7,
                            "event_executed": True,
                            "data_by_event": [{"name": "password", "value": "marlon"}],
                        },
                    ],
                },
                {
                    "key": "95b1bf87-324b-40dc-9aca-8b812f9012f4",
                    "tracking_code": "95b1bf87-324b-40dc-9aca-8b812f9012f4",
                    "update": "2024-11-06 08:48:44.659444",
                    "data": [
                        {"name": "edad", "value": "27"},
                        {"name": "direccion", "value": "calle 100"},
                        {"name": "password", "value": "marlon"},
                    ],
                    "events": [
                        {
                            "id": "72763b66-c9d5-4880-88a1-bef336873225",
                            "name": "mail_registration",
                            "code": "MAIL_REG",
                            "order": 1,
                            "event_executed": True,
                            "data_by_event": [{"name": "edad", "value": "27"}],
                        },
                        {
                            "id": "c8e2065d-b11e-4b8a-b6df-b44d5d2896c2",
                            "name": "opening_link",
                            "code": "OPEN_LINK",
                            "order": 2,
                            "event_executed": True,
                            "data_by_event": [
                                {"name": "direccion", "value": "calle 100"}
                            ],
                        },
                        {
                            "id": "aa2fdc48-ba8a-459b-8a3a-8d94d2781ca4",
                            "name": "company_contact_information",
                            "code": "COMP_INFO",
                            "order": 3,
                            "event_executed": False,
                            "data_by_event": [],
                        },
                        {
                            "id": "3764ec6a-ef18-4e74-bb6b-54fcdb1dfa12",
                            "name": "nit_validation",
                            "code": "NIT_VAL",
                            "order": 4,
                            "event_executed": False,
                            "data_by_event": [],
                        },
                        {
                            "id": "efb331e4-71da-4558-9104-ae9d9010796c",
                            "name": "data_processing",
                            "code": "DATA_PROC",
                            "order": 5,
                            "event_executed": False,
                            "data_by_event": [],
                        },
                        {
                            "id": "131051aa-913a-46d6-9418-5c34c2199c20",
                            "name": "metamap_flow",
                            "code": "META_FLOW",
                            "order": 6,
                            "event_executed": False,
                            "data_by_event": [],
                        },
                        {
                            "id": "5b3374af-1492-4018-b7ae-9713f3665b53",
                            "name": "create_password",
                            "code": "CREATE_PASS",
                            "order": 7,
                            "event_executed": True,
                            "data_by_event": [{"name": "password", "value": "marlon"}],
                        },
                    ],
                },
                {
                    "key": "b6f9f603-4874-436c-be3f-415045fbde85",
                    "tracking_code": "b6f9f603-4874-436c-be3f-415045fbde85",
                    "update": "2024-11-06 10:45:10.330511",
                    "data": [
                        {"name": "email", "value": "marlon"},
                        {"name": "password", "value": "marlon"},
                    ],
                    "events": [
                        {
                            "id": "72763b66-c9d5-4880-88a1-bef336873225",
                            "name": "mail_registration",
                            "code": "MAIL_REG",
                            "order": 1,
                            "event_executed": True,
                            "data_by_event": [
                                {"name": "email", "value": "marlon"},
                                {"name": "password", "value": "marlon"},
                            ],
                        },
                        {
                            "id": "c8e2065d-b11e-4b8a-b6df-b44d5d2896c2",
                            "name": "opening_link",
                            "code": "OPEN_LINK",
                            "order": 2,
                            "event_executed": False,
                            "data_by_event": [],
                        },
                        {
                            "id": "aa2fdc48-ba8a-459b-8a3a-8d94d2781ca4",
                            "name": "company_contact_information",
                            "code": "COMP_INFO",
                            "order": 3,
                            "event_executed": True,
                            "data_by_event": [],
                        },
                        {
                            "id": "3764ec6a-ef18-4e74-bb6b-54fcdb1dfa12",
                            "name": "nit_validation",
                            "code": "NIT_VAL",
                            "order": 4,
                            "event_executed": False,
                            "data_by_event": [],
                        },
                        {
                            "id": "efb331e4-71da-4558-9104-ae9d9010796c",
                            "name": "data_processing",
                            "code": "DATA_PROC",
                            "order": 5,
                            "event_executed": False,
                            "data_by_event": [],
                        },
                        {
                            "id": "131051aa-913a-46d6-9418-5c34c2199c20",
                            "name": "metamap_flow",
                            "code": "META_FLOW",
                            "order": 6,
                            "event_executed": False,
                            "data_by_event": [],
                        },
                        {
                            "id": "5b3374af-1492-4018-b7ae-9713f3665b53",
                            "name": "create_password",
                            "code": "CREATE_PASS",
                            "order": 7,
                            "event_executed": False,
                            "data_by_event": [],
                        },
                    ],
                },
                {
                    "key": "aec9e079-0bec-490e-9944-a0765d139d75",
                    "tracking_code": "aec9e079-0bec-490e-9944-a0765d139d75",
                    "update": "2024-11-05 22:34:45.394912",
                    "data": [{"name": "password", "value": "marlon"}],
                    "events": [
                        {
                            "id": "72763b66-c9d5-4880-88a1-bef336873225",
                            "name": "mail_registration",
                            "code": "MAIL_REG",
                            "order": 1,
                            "event_executed": False,
                            "data_by_event": [],
                        },
                        {
                            "id": "c8e2065d-b11e-4b8a-b6df-b44d5d2896c2",
                            "name": "opening_link",
                            "code": "OPEN_LINK",
                            "order": 2,
                            "event_executed": False,
                            "data_by_event": [],
                        },
                        {
                            "id": "aa2fdc48-ba8a-459b-8a3a-8d94d2781ca4",
                            "name": "company_contact_information",
                            "code": "COMP_INFO",
                            "order": 3,
                            "event_executed": False,
                            "data_by_event": [],
                        },
                        {
                            "id": "3764ec6a-ef18-4e74-bb6b-54fcdb1dfa12",
                            "name": "nit_validation",
                            "code": "NIT_VAL",
                            "order": 4,
                            "event_executed": True,
                            "data_by_event": [{"name": "password", "value": "marlon"}],
                        },
                        {
                            "id": "efb331e4-71da-4558-9104-ae9d9010796c",
                            "name": "data_processing",
                            "code": "DATA_PROC",
                            "order": 5,
                            "event_executed": True,
                            "data_by_event": [{"name": "password", "value": "marlon"}],
                        },
                        {
                            "id": "131051aa-913a-46d6-9418-5c34c2199c20",
                            "name": "metamap_flow",
                            "code": "META_FLOW",
                            "order": 6,
                            "event_executed": True,
                            "data_by_event": [{"name": "password", "value": "marlon"}],
                        },
                        {
                            "id": "5b3374af-1492-4018-b7ae-9713f3665b53",
                            "name": "create_password",
                            "code": "CREATE_PASS",
                            "order": 7,
                            "event_executed": True,
                            "data_by_event": [{"name": "password", "value": "marlon"}],
                        },
                    ],
                },
                {
                    "key": "1bae0771-fd73-4ae2-9bf3-0ab13baa3201",
                    "tracking_code": "1bae0771-fd73-4ae2-9bf3-0ab13baa3201",
                    "update": "2024-11-05 23:22:42.488625",
                    "data": [{"name": "password", "value": "marlon"}],
                    "events": [
                        {
                            "id": "72763b66-c9d5-4880-88a1-bef336873225",
                            "name": "mail_registration",
                            "code": "MAIL_REG",
                            "order": 1,
                            "event_executed": True,
                            "data_by_event": [{"name": "password", "value": "marlon"}],
                        },
                        {
                            "id": "c8e2065d-b11e-4b8a-b6df-b44d5d2896c2",
                            "name": "opening_link",
                            "code": "OPEN_LINK",
                            "order": 2,
                            "event_executed": True,
                            "data_by_event": [{"name": "password", "value": "marlon"}],
                        },
                        {
                            "id": "aa2fdc48-ba8a-459b-8a3a-8d94d2781ca4",
                            "name": "company_contact_information",
                            "code": "COMP_INFO",
                            "order": 3,
                            "event_executed": True,
                            "data_by_event": [{"name": "password", "value": "marlon"}],
                        },
                        {
                            "id": "3764ec6a-ef18-4e74-bb6b-54fcdb1dfa12",
                            "name": "nit_validation",
                            "code": "NIT_VAL",
                            "order": 4,
                            "event_executed": True,
                            "data_by_event": [{"name": "password", "value": "marlon"}],
                        },
                        {
                            "id": "efb331e4-71da-4558-9104-ae9d9010796c",
                            "name": "data_processing",
                            "code": "DATA_PROC",
                            "order": 5,
                            "event_executed": True,
                            "data_by_event": [{"name": "password", "value": "marlon"}],
                        },
                        {
                            "id": "131051aa-913a-46d6-9418-5c34c2199c20",
                            "name": "metamap_flow",
                            "code": "META_FLOW",
                            "order": 6,
                            "event_executed": False,
                            "data_by_event": [],
                        },
                        {
                            "id": "5b3374af-1492-4018-b7ae-9713f3665b53",
                            "name": "create_password",
                            "code": "CREATE_PASS",
                            "order": 7,
                            "event_executed": False,
                            "data_by_event": [],
                        },
                    ],
                },
                {
                    "key": "1bae0771-fd73-4ae2-9bf3-0ab13baa3202",
                    "tracking_code": "1bae0771-fd73-4ae2-9bf3-0ab13baa3202",
                    "update": "2024-11-05 23:23:50.228587",
                    "data": [{"name": "password", "value": "marlon"}],
                    "events": [
                        {
                            "id": "72763b66-c9d5-4880-88a1-bef336873225",
                            "name": "mail_registration",
                            "code": "MAIL_REG",
                            "order": 1,
                            "event_executed": False,
                            "data_by_event": [],
                        },
                        {
                            "id": "c8e2065d-b11e-4b8a-b6df-b44d5d2896c2",
                            "name": "opening_link",
                            "code": "OPEN_LINK",
                            "order": 2,
                            "event_executed": False,
                            "data_by_event": [],
                        },
                        {
                            "id": "aa2fdc48-ba8a-459b-8a3a-8d94d2781ca4",
                            "name": "company_contact_information",
                            "code": "COMP_INFO",
                            "order": 3,
                            "event_executed": False,
                            "data_by_event": [],
                        },
                        {
                            "id": "3764ec6a-ef18-4e74-bb6b-54fcdb1dfa12",
                            "name": "nit_validation",
                            "code": "NIT_VAL",
                            "order": 4,
                            "event_executed": False,
                            "data_by_event": [],
                        },
                        {
                            "id": "efb331e4-71da-4558-9104-ae9d9010796c",
                            "name": "data_processing",
                            "code": "DATA_PROC",
                            "order": 5,
                            "event_executed": True,
                            "data_by_event": [{"name": "password", "value": "marlon"}],
                        },
                        {
                            "id": "131051aa-913a-46d6-9418-5c34c2199c20",
                            "name": "metamap_flow",
                            "code": "META_FLOW",
                            "order": 6,
                            "event_executed": False,
                            "data_by_event": [],
                        },
                        {
                            "id": "5b3374af-1492-4018-b7ae-9713f3665b53",
                            "name": "create_password",
                            "code": "CREATE_PASS",
                            "order": 7,
                            "event_executed": False,
                            "data_by_event": [],
                        },
                    ],
                },
                {
                    "key": "1bae0771-fd73-4ae2-9bf3-0ab13baa3203",
                    "tracking_code": "1bae0771-fd73-4ae2-9bf3-0ab13baa3203",
                    "update": "2024-11-06 08:43:55.676076",
                    "data": [{"name": "password", "value": "marlon"}],
                    "events": [
                        {
                            "id": "72763b66-c9d5-4880-88a1-bef336873225",
                            "name": "mail_registration",
                            "code": "MAIL_REG",
                            "order": 1,
                            "event_executed": True,
                            "data_by_event": [{"name": "password", "value": "marlon"}],
                        },
                        {
                            "id": "c8e2065d-b11e-4b8a-b6df-b44d5d2896c2",
                            "name": "opening_link",
                            "code": "OPEN_LINK",
                            "order": 2,
                            "event_executed": True,
                            "data_by_event": [{"name": "password", "value": "marlon"}],
                        },
                        {
                            "id": "aa2fdc48-ba8a-459b-8a3a-8d94d2781ca4",
                            "name": "company_contact_information",
                            "code": "COMP_INFO",
                            "order": 3,
                            "event_executed": True,
                            "data_by_event": [{"name": "password", "value": "marlon"}],
                        },
                        {
                            "id": "3764ec6a-ef18-4e74-bb6b-54fcdb1dfa12",
                            "name": "nit_validation",
                            "code": "NIT_VAL",
                            "order": 4,
                            "event_executed": True,
                            "data_by_event": [{"name": "password", "value": "marlon"}],
                        },
                        {
                            "id": "efb331e4-71da-4558-9104-ae9d9010796c",
                            "name": "data_processing",
                            "code": "DATA_PROC",
                            "order": 5,
                            "event_executed": True,
                            "data_by_event": [{"name": "password", "value": "marlon"}],
                        },
                        {
                            "id": "131051aa-913a-46d6-9418-5c34c2199c20",
                            "name": "metamap_flow",
                            "code": "META_FLOW",
                            "order": 6,
                            "event_executed": False,
                            "data_by_event": [],
                        },
                        {
                            "id": "5b3374af-1492-4018-b7ae-9713f3665b53",
                            "name": "create_password",
                            "code": "CREATE_PASS",
                            "order": 7,
                            "event_executed": True,
                            "data_by_event": [{"name": "password", "value": "marlon"}],
                        },
                    ],
                },
            ]

            current_data = result

            if current_data != last_data:
                current_data = [data for data in current_data]
                try:
                    await websocket.send_json(current_data)
                    last_data = current_data
                except WebSocketDisconnect:
                    print("El cliente desconectó el WebSocket.")
                    break
                except RuntimeError as e:
                    break

            await asyncio.sleep(1)

    except Exception as e:
        print("WebSocket error general:", e)
    finally:
        receive_task.cancel()
