from typing import List
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Request,
    status,
    WebSocket,
    WebSocketDisconnect,
)
from src.core.config import settings
from src.core.enums.permission_type import PERMISSION_TYPE
from sqlalchemy.future import select
import asyncio
from src.infrastructure.database.config.async_config_db import async_session_db
from src.infrastructure.database.entities.currency_entity import CurrencyEntity


example_router = APIRouter(
    prefix="/websocket",
    tags=["Websockets"],
    responses={404: {"description": "Not found"}},
)


@example_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(code=1008)  # Cerrar con código de error de autenticación
        return

    await websocket.accept()  # Acepta la conexión del cliente

    last_data = None  # Variable para almacenar el último estado de los datos
    try:
        async with async_session_db() as db:  # Sesión de base de datos dentro del bucle de conexión
            while True:
                # Recibe un mensaje del cliente
                message = await websocket.receive_text()
                print("Mensaje recibido del cliente:", message)

                # Procesar el mensaje, si es necesario (aquí solo se imprime)
                # Luego, puedes responder al cliente si lo deseas
                await websocket.send_text(f"Mensaje recibido: {message}")
                # Ejecuta una consulta para verificar cambios
                stmt = select(CurrencyEntity)
                result = await db.execute(stmt)
                current_data = result.scalars().all()

                # Si hay cambios, envía los datos al cliente
                if current_data != last_data:
                    current_data = [  # Convierte cada instancia en un diccionario
                        {"id": str(currency.id), "name": currency.name}
                        for currency in current_data
                    ]
                    try:
                        await websocket.send_json(
                            current_data
                        )  # Envía el cambio en formato JSON
                        last_data = current_data  # Actualiza el último estado
                    except WebSocketDisconnect:
                        """print("El cliente desconectó el WebSocket.")"""
                        break  # Sal del bucle si el WebSocket está cerrado
                    except RuntimeError as e:
                        """print("Error de Runtime en WebSocket:", e)"""
                        break  # Sal del bucle si ocurre cualquier otro error de envío

                await asyncio.sleep(3)  # Intervalo de verificación en segundos
    except Exception as e:
        print("WebSocket error general:", e)
