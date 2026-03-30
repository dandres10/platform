from src.infrastructure.web.mcp_routes.business.server import mcp
from src.core.classes.mcp_client import McpClient
from src.core.wrappers.check_mcp_roles import check_mcp_roles
from src.core.wrappers.check_mcp_permissions import check_mcp_permissions
from src.core.enums.rol_type import ROL_TYPE
from src.core.enums.permission_type import PERMISSION_TYPE
from src.core.models.response import Response
from src.domain.models.business.auth.login.auth_login_response import AuthLoginResponse
from src.domain.models.business.auth.logout.auth_logout_response import AuthLogoutResponse
from src.domain.models.business.auth.refresh_token.auth_refresh_token_response import AuthRefreshTokenResponse
from src.domain.models.business.auth.create_api_token.create_api_token_response import CreateApiTokenResponse
from src.domain.models.business.auth.create_user_internal.create_user_internal_response import CreateUserInternalResponse
from src.domain.models.business.auth.update_user_internal.update_user_internal_response import UpdateUserInternalResponse
from src.domain.models.business.auth.delete_user_internal.delete_user_internal_response import DeleteUserInternalResponse
from src.domain.models.business.auth.create_user_external.create_user_external_response import CreateUserExternalResponse
from src.domain.models.business.auth.delete_user_external.delete_user_external_response import DeleteUserExternalResponse
from src.domain.models.business.auth.list_users_by_location.user_by_location_item import UserByLocationItem
from src.domain.models.business.auth.list_users_external.user_external_item import UserExternalItem
from src.domain.models.business.auth.create_company.create_company_response import CreateCompanyResponse
from src.domain.models.business.auth.delete_company.delete_company_response import DeleteCompanyResponse


@mcp.tool()
@check_mcp_roles([])
@check_mcp_permissions([])
async def login(email: str, password: str, language: str = "ES") -> Response[AuthLoginResponse]:
    """Autenticar usuario con email y password. Retorna access_token y refresh_token. No requiere autenticacion previa.
Endpoint: POST platform /auth/login"""
    client = McpClient(language=language)
    raw = await client.post("/auth/login", {"email": email, "password": password})
    return McpClient.parse_response(raw, Response[AuthLoginResponse])


@mcp.tool()
@check_mcp_roles([])
@check_mcp_permissions([])
async def logout(token: str, language: str = "ES") -> Response[AuthLogoutResponse]:
    """Cerrar sesion del usuario actual.
Endpoint: POST platform /auth/logout"""
    client = McpClient(token=token, language=language)
    raw = await client.post("/auth/logout")
    return McpClient.parse_response(raw, Response[AuthLogoutResponse])


@mcp.tool()
@check_mcp_roles([])
@check_mcp_permissions([])
async def refresh_token(token: str, language: str = "ES") -> Response[AuthRefreshTokenResponse]:
    """Renovar access_token expirado. Usar cuando el token actual ya no es valido.
Endpoint: POST platform /auth/refresh_token"""
    client = McpClient(token=token, language=language)
    raw = await client.post("/auth/refresh_token")
    return McpClient.parse_response(raw, Response[AuthRefreshTokenResponse])


@mcp.tool()
@check_mcp_roles([])
@check_mcp_permissions([])
async def create_api_token(token: str, rol_id: str, language: str = "ES") -> Response[CreateApiTokenResponse]:
    """Generar API token de larga duracion. Necesita rol_id.
Endpoint: POST platform /auth/create-api-token"""
    client = McpClient(token=token, language=language)
    raw = await client.post("/auth/create-api-token", {"rol_id": rol_id})
    return McpClient.parse_response(raw, Response[CreateApiTokenResponse])


@mcp.tool()
@check_mcp_roles([ROL_TYPE.ADMIN.value])
@check_mcp_permissions([PERMISSION_TYPE.SAVE.value])
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
) -> Response[CreateUserInternalResponse]:
    """Crear usuario interno (colaborador/admin). Solo ADMIN. Necesita datos personales + location_rol_json con asignaciones de sede y rol.
    location_rol_json: JSON array de objetos con location_id y rol_id.
    Ejemplo: [{"location_id":"uuid","rol_id":"uuid"}]
Endpoint: POST platform /auth/create-user-internal"""
    import json
    client = McpClient(token=token, language=language)
    raw = await client.post("/auth/create-user-internal", {
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
    return McpClient.parse_response(raw, Response[CreateUserInternalResponse])


@mcp.tool()
@check_mcp_roles([ROL_TYPE.ADMIN.value])
@check_mcp_permissions([PERMISSION_TYPE.UPDATE.value])
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
) -> Response[UpdateUserInternalResponse]:
    """Actualizar usuario interno. Solo ADMIN. Enviar solo campos a cambiar. Necesita user_id.
Endpoint: PUT platform /auth/update-user-internal/{user_id}"""
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
    raw = await client.put(f"/auth/update-user-internal/{user_id}", data)
    return McpClient.parse_response(raw, Response[UpdateUserInternalResponse])


@mcp.tool()
@check_mcp_roles([ROL_TYPE.ADMIN.value])
@check_mcp_permissions([PERMISSION_TYPE.DELETE.value])
async def delete_user_internal(token: str, user_id: str, language: str = "ES") -> Response[DeleteUserInternalResponse]:
    """Eliminar usuario interno. Solo ADMIN. Necesita user_id.
Endpoint: DELETE platform /auth/delete-user-internal/{user_id}"""
    client = McpClient(token=token, language=language)
    raw = await client.delete(f"/auth/delete-user-internal/{user_id}")
    return McpClient.parse_response(raw, Response[DeleteUserInternalResponse])


@mcp.tool()
@check_mcp_roles([])
@check_mcp_permissions([])
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
) -> Response[CreateUserExternalResponse]:
    """Registrar usuario externo (cliente). No requiere autenticacion. Necesita datos personales completos + identification + language_id + currency_id.
Endpoint: POST platform /auth/create-user-external"""
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
    raw = await client.post("/auth/create-user-external", data)
    return McpClient.parse_response(raw, Response[CreateUserExternalResponse])


@mcp.tool()
@check_mcp_roles([ROL_TYPE.USER.value])
@check_mcp_permissions([PERMISSION_TYPE.DELETE.value])
async def delete_user_external(token: str, user_id: str, language: str = "ES") -> Response[DeleteUserExternalResponse]:
    """Eliminar usuario externo. Necesita user_id.
Endpoint: DELETE platform /auth/delete-user-external/{user_id}"""
    client = McpClient(token=token, language=language)
    raw = await client.delete(f"/auth/delete-user-external/{user_id}")
    return McpClient.parse_response(raw, Response[DeleteUserExternalResponse])


@mcp.tool()
@check_mcp_roles([ROL_TYPE.ADMIN.value, ROL_TYPE.USER.value, ROL_TYPE.COLLA.value])
@check_mcp_permissions([PERMISSION_TYPE.READ.value])
async def list_users_internal(
    token: str,
    skip: int = 0,
    limit: int = 10,
    name_filter: str = "",
    email_filter: str = "",
    language: str = "ES",
) -> Response[list[UserByLocationItem]]:
    """Buscar usuarios internos. Filtrable por nombre o email. Paginado con skip/limit.
Endpoint: POST platform /auth/users-internal"""
    client = McpClient(token=token, language=language)
    filters = []
    if name_filter:
        filters.append({"field": "first_name", "condition": "like", "value": name_filter})
    if email_filter:
        filters.append({"field": "email", "condition": "like", "value": email_filter})
    raw = await client.post("/auth/users-internal", {
        "skip": skip, "limit": limit, "filters": filters or None
    })
    return McpClient.parse_response(raw, Response[list[UserByLocationItem]])


@mcp.tool()
@check_mcp_roles([ROL_TYPE.ADMIN.value, ROL_TYPE.USER.value, ROL_TYPE.COLLA.value])
@check_mcp_permissions([PERMISSION_TYPE.READ.value])
async def list_users_external(
    token: str,
    skip: int = 0,
    limit: int = 10,
    name_filter: str = "",
    email_filter: str = "",
    language: str = "ES",
) -> Response[list[UserExternalItem]]:
    """Buscar usuarios externos (clientes). Filtrable por nombre o email. Paginado con skip/limit.
Endpoint: POST platform /auth/users-external"""
    client = McpClient(token=token, language=language)
    filters = []
    if name_filter:
        filters.append({"field": "first_name", "condition": "like", "value": name_filter})
    if email_filter:
        filters.append({"field": "email", "condition": "like", "value": email_filter})
    raw = await client.post("/auth/users-external", {
        "skip": skip, "limit": limit, "filters": filters or None
    })
    return McpClient.parse_response(raw, Response[list[UserExternalItem]])


@mcp.tool()
@check_mcp_roles([])
@check_mcp_permissions([])
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
) -> Response[CreateCompanyResponse]:
    """Onboarding completo: crea empresa + primera sede + usuario admin en una sola llamada. Necesita datos de empresa, ubicacion y admin.
Endpoint: POST platform /auth/create-company"""
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
    raw = await client.post("/auth/create-company", {
        "company": company, "location": location, "admin_user": admin_user
    })
    return McpClient.parse_response(raw, Response[CreateCompanyResponse])


@mcp.tool()
@check_mcp_roles([ROL_TYPE.ADMIN.value])
@check_mcp_permissions([PERMISSION_TYPE.DELETE.value])
async def delete_company(token: str, company_id: str, language: str = "ES") -> Response[DeleteCompanyResponse]:
    """Eliminar compania y todos sus datos asociados. ACCION DESTRUCTIVA. Necesita company_id.
Endpoint: DELETE platform /auth/delete-company/{company_id}"""
    client = McpClient(token=token, language=language)
    raw = await client.delete(f"/auth/delete-company/{company_id}")
    return McpClient.parse_response(raw, Response[DeleteCompanyResponse])
