from src.infrastructure.web.mcp_routes.business.server import mcp
from src.core.classes.mcp_client import McpClient


@mcp.tool()
async def login(email: str, password: str, language: str = "ES") -> str:
    """Autenticar usuario en la plataforma Goluti. Retorna access_token y refresh_token."""
    client = McpClient(language=language)
    return await client.post("/auth/login", {"email": email, "password": password})


@mcp.tool()
async def logout(token: str, language: str = "ES") -> str:
    """Cerrar sesion del usuario autenticado."""
    client = McpClient(token=token, language=language)
    return await client.post("/auth/logout")


@mcp.tool()
async def refresh_token(token: str, language: str = "ES") -> str:
    """Renovar token JWT expirado. Retorna nuevo access_token."""
    client = McpClient(token=token, language=language)
    return await client.post("/auth/refresh_token")


@mcp.tool()
async def create_api_token(token: str, rol_id: str, language: str = "ES") -> str:
    """Generar API token de larga duracion para un rol especifico."""
    client = McpClient(token=token, language=language)
    return await client.post("/auth/create-api-token", {"rol_id": rol_id})


@mcp.tool()
async def create_user_internal(
    token: str,
    email: str,
    password: str,
    identification: str,
    first_name: str,
    last_name: str,
    language_id: str,
    currency_id: str,
    location_rol_json: str,
    phone: str = "",
    token_expiration_minutes: int = 60,
    refresh_token_expiration_minutes: int = 1440,
    language: str = "ES",
) -> str:
    """Crear usuario interno (solo ADMIN).
    location_rol_json: JSON array de objetos con location_id y rol_id.
    Ejemplo: [{"location_id":"uuid","rol_id":"uuid"}]
    """
    import json
    client = McpClient(token=token, language=language)
    return await client.post("/auth/create-user-internal", {
        "email": email,
        "password": password,
        "identification": identification,
        "first_name": first_name,
        "last_name": last_name,
        "language_id": language_id,
        "currency_id": currency_id,
        "location_rol": json.loads(location_rol_json),
        "phone": phone,
        "token_expiration_minutes": token_expiration_minutes,
        "refresh_token_expiration_minutes": refresh_token_expiration_minutes,
    })


@mcp.tool()
async def update_user_internal(
    token: str,
    user_id: str,
    password: str = "",
    email: str = "",
    identification: str = "",
    first_name: str = "",
    last_name: str = "",
    phone: str = "",
    state: bool = None,
    rol_id: str = "",
    language: str = "ES",
) -> str:
    """Actualizar datos de un usuario interno. Solo enviar los campos que se quieran cambiar."""
    client = McpClient(token=token, language=language)
    data = {}
    if password: data["password"] = password
    if email: data["email"] = email
    if identification: data["identification"] = identification
    if first_name: data["first_name"] = first_name
    if last_name: data["last_name"] = last_name
    if phone: data["phone"] = phone
    if state is not None: data["state"] = state
    if rol_id: data["rol_id"] = rol_id
    return await client.put(f"/auth/update-user-internal/{user_id}", data)


@mcp.tool()
async def delete_user_internal(token: str, user_id: str, language: str = "ES") -> str:
    """Eliminar usuario interno. Solo ADMIN."""
    client = McpClient(token=token, language=language)
    return await client.delete(f"/auth/delete-user-internal/{user_id}")


@mcp.tool()
async def create_user_external(
    email: str,
    password: str,
    identification: str,
    first_name: str,
    last_name: str,
    language_id: str,
    currency_id: str,
    country_id: str = "",
    phone: str = "",
    token_expiration_minutes: int = 60,
    refresh_token_expiration_minutes: int = 1440,
    language: str = "ES",
) -> str:
    """Registrar usuario externo (auto-registro). No requiere autenticacion."""
    client = McpClient(language=language)
    data = {
        "email": email,
        "password": password,
        "identification": identification,
        "first_name": first_name,
        "last_name": last_name,
        "language_id": language_id,
        "currency_id": currency_id,
        "token_expiration_minutes": token_expiration_minutes,
        "refresh_token_expiration_minutes": refresh_token_expiration_minutes,
    }
    if country_id: data["country_id"] = country_id
    if phone: data["phone"] = phone
    return await client.post("/auth/create-user-external", data)


@mcp.tool()
async def delete_user_external(token: str, user_id: str, language: str = "ES") -> str:
    """Eliminar usuario externo."""
    client = McpClient(token=token, language=language)
    return await client.delete(f"/auth/delete-user-external/{user_id}")


@mcp.tool()
async def list_users_internal(
    token: str,
    skip: int = 0,
    limit: int = 10,
    name_filter: str = "",
    email_filter: str = "",
    language: str = "ES",
) -> str:
    """Listar usuarios internos con paginacion y filtros opcionales."""
    client = McpClient(token=token, language=language)
    filters = []
    if name_filter:
        filters.append({"field": "first_name", "condition": "like", "value": name_filter})
    if email_filter:
        filters.append({"field": "email", "condition": "like", "value": email_filter})
    return await client.post("/auth/users-internal", {
        "skip": skip, "limit": limit, "filters": filters or None
    })


@mcp.tool()
async def list_users_external(
    token: str,
    skip: int = 0,
    limit: int = 10,
    name_filter: str = "",
    email_filter: str = "",
    language: str = "ES",
) -> str:
    """Listar usuarios externos con paginacion y filtros opcionales."""
    client = McpClient(token=token, language=language)
    filters = []
    if name_filter:
        filters.append({"field": "first_name", "condition": "like", "value": name_filter})
    if email_filter:
        filters.append({"field": "email", "condition": "like", "value": email_filter})
    return await client.post("/auth/users-external", {
        "skip": skip, "limit": limit, "filters": filters or None
    })


@mcp.tool()
async def create_company(
    company_name: str,
    company_nit: str,
    location_name: str,
    location_address: str,
    location_phone: str,
    location_email: str,
    location_country_id: str,
    admin_email: str,
    admin_password: str,
    admin_first_name: str,
    admin_last_name: str,
    admin_identification: str,
    admin_phone: str,
    admin_language_id: str,
    admin_currency_id: str,
    admin_rol_id: str,
    company_inactivity_time: int = 30,
    location_city_id: str = "",
    location_latitude: str = "",
    location_longitude: str = "",
    location_google_place_id: str = "",
    language: str = "ES",
) -> str:
    """Crear compania completa con ubicacion y usuario administrador."""
    client = McpClient(language=language)
    company = {"name": company_name, "nit": company_nit, "inactivity_time": company_inactivity_time}
    location = {
        "country_id": location_country_id,
        "name": location_name,
        "address": location_address,
        "phone": location_phone,
        "email": location_email,
    }
    if location_city_id: location["city_id"] = location_city_id
    if location_latitude: location["latitude"] = location_latitude
    if location_longitude: location["longitude"] = location_longitude
    if location_google_place_id: location["google_place_id"] = location_google_place_id
    admin_user = {
        "email": admin_email,
        "password": admin_password,
        "first_name": admin_first_name,
        "last_name": admin_last_name,
        "identification": admin_identification,
        "phone": admin_phone,
        "language_id": admin_language_id,
        "currency_id": admin_currency_id,
        "rol_id": admin_rol_id,
    }
    return await client.post("/auth/create-company", {
        "company": company, "location": location, "admin_user": admin_user
    })


@mcp.tool()
async def delete_company(token: str, company_id: str, language: str = "ES") -> str:
    """Eliminar compania y todos sus datos asociados. ACCION DESTRUCTIVA."""
    client = McpClient(token=token, language=language)
    return await client.delete(f"/auth/delete-company/{company_id}")
