from enum import Enum


class KEYS_MESSAGES(str, Enum):
    CORE_QUERY_MADE = "core_query_made"
    CORE_SAVED_INFORMATION = "core_saved_information"
    CORE_UPDATED_INFORMATION = "core_updated_information"
    CORE_DELETION_PERFORMED = "core_deletion_performed"
    CORE_RECORD_NOT_FOUND_TO_DELETE = "core_record_not_found_to_delete"
    CORE_NO_RESULTS_FOUND = "core_no_results_found"
    CORE_RECORD_NOT_FOUND = "core_record_not_found"
    CORE_ERROR_SAVING_RECORD = "core_error_saving_record"
    CORE_UPDATE_FAILED = "core_update_failed"
    
    AUTH_CREATE_USER_LANGUAGE_NOT_FOUND = "auth_create_user_language_not_found"
    AUTH_CREATE_USER_CURRENCY_NOT_FOUND = "auth_create_user_currency_not_found"
    AUTH_CREATE_USER_EMPTY_LOCATION_ROL = "auth_create_user_empty_location_rol"
    AUTH_CREATE_USER_LOCATION_NOT_FOUND = "auth_create_user_location_not_found"
    AUTH_CREATE_USER_ROL_NOT_FOUND = "auth_create_user_rol_not_found"
    AUTH_CREATE_USER_DUPLICATE_COMBINATION = "auth_create_user_duplicate_combination"
    AUTH_CREATE_USER_EMAIL_ALREADY_EXISTS = "auth_create_user_email_already_exists"
    AUTH_CREATE_USER_SUCCESS = "auth_create_user_success"
    
    AUTH_CREATE_USER_EXTERNAL_LANGUAGE_NOT_FOUND = "auth_create_user_external_language_not_found"
    AUTH_CREATE_USER_EXTERNAL_CURRENCY_NOT_FOUND = "auth_create_user_external_currency_not_found"
    AUTH_CREATE_USER_EXTERNAL_EMAIL_ALREADY_EXISTS = "auth_create_user_external_email_already_exists"
    AUTH_CREATE_USER_EXTERNAL_IDENTIFICATION_ALREADY_EXISTS = "auth_create_user_external_identification_already_exists"
    AUTH_CREATE_USER_EXTERNAL_SUCCESS = "auth_create_user_external_success"
    
    # Create Company Flow
    CREATE_COMPANY_NIT_ALREADY_EXISTS = "create_company_nit_already_exists"
    CREATE_COMPANY_EMAIL_ALREADY_EXISTS = "create_company_email_already_exists"
    CREATE_COMPANY_COUNTRY_NOT_FOUND = "create_company_country_not_found"
    CREATE_COMPANY_LANGUAGE_NOT_FOUND = "create_company_language_not_found"
    CREATE_COMPANY_CURRENCY_NOT_FOUND = "create_company_currency_not_found"
    CREATE_COMPANY_ROL_NOT_FOUND = "create_company_rol_not_found"
    CREATE_COMPANY_NO_MENU_TEMPLATES = "create_company_no_menu_templates"
    CREATE_COMPANY_ERROR_CLONING_MENUS = "create_company_error_cloning_menus"
    CREATE_COMPANY_ERROR_CREATING_LOCATION = "create_company_error_creating_location"
    CREATE_COMPANY_ERROR_CREATING_ADMIN = "create_company_error_creating_admin"
    CREATE_COMPANY_SUCCESS = "create_company_success"
    CREATE_COMPANY_RECAPTCHA_FAILED = "create_company_recaptcha_failed"
    
    # Delete User Internal Flow
    AUTH_DELETE_USER_NOT_FOUND = "auth_delete_user_not_found"
    AUTH_DELETE_USER_CANNOT_DELETE_SELF = "auth_delete_user_cannot_delete_self"
    AUTH_DELETE_USER_HAS_ACTIVE_RELATIONS = "auth_delete_user_has_active_relations"
    AUTH_DELETE_USER_NOT_IN_LOCATION = "auth_delete_user_not_in_location"
    AUTH_DELETE_USER_ERROR_FETCHING_ROLES = "auth_delete_user_error_fetching_roles"
    AUTH_DELETE_USER_NO_ROLES_FOUND = "auth_delete_user_no_roles_found"
    AUTH_DELETE_USER_SOFT_DELETED = "auth_delete_user_soft_deleted"
    AUTH_DELETE_USER_ERROR_SOFT_DELETE = "auth_delete_user_error_soft_delete"
    AUTH_DELETE_USER_SUCCESS = "auth_delete_user_success"
    AUTH_DELETE_USER_ERROR_DELETING_ROLES = "auth_delete_user_error_deleting_roles"
    AUTH_DELETE_USER_ERROR_DELETING_USER = "auth_delete_user_error_deleting_user"
    AUTH_DELETE_USER_ERROR_DELETING_PLATFORM = "auth_delete_user_error_deleting_platform"
    AUTH_DELETE_USER_LAST_ADMIN = "auth_delete_user_last_admin"
    
    # Delete User External Flow
    AUTH_DELETE_USER_EXTERNAL_NOT_FOUND = "auth_delete_user_external_not_found"
    AUTH_DELETE_USER_EXTERNAL_UNAUTHORIZED = "auth_delete_user_external_unauthorized"
    AUTH_DELETE_USER_EXTERNAL_HAS_ACTIVE_RELATIONS = "auth_delete_user_external_has_active_relations"
    AUTH_DELETE_USER_EXTERNAL_SOFT_DELETED = "auth_delete_user_external_soft_deleted"
    AUTH_DELETE_USER_EXTERNAL_ERROR_SOFT_DELETE = "auth_delete_user_external_error_soft_delete"
    AUTH_DELETE_USER_EXTERNAL_SUCCESS = "auth_delete_user_external_success"
    AUTH_DELETE_USER_EXTERNAL_ERROR_DELETING_USER = "auth_delete_user_external_error_deleting_user"
    AUTH_DELETE_USER_EXTERNAL_ERROR_DELETING_PLATFORM = "auth_delete_user_external_error_deleting_platform"
    
    # Delete Company Flow
    DELETE_COMPANY_NOT_FOUND = "delete_company_not_found"
    DELETE_COMPANY_UNAUTHORIZED = "delete_company_unauthorized"
    DELETE_COMPANY_HAS_ACTIVE_RELATIONS = "delete_company_has_active_relations"
    DELETE_COMPANY_ERROR_DELETING_USERS = "delete_company_error_deleting_users"
    DELETE_COMPANY_ERROR_DELETING_MENUS = "delete_company_error_deleting_menus"
    DELETE_COMPANY_ERROR_DELETING_LOCATIONS = "delete_company_error_deleting_locations"
    DELETE_COMPANY_ERROR_DELETING_COMPANY = "delete_company_error_deleting_company"
    DELETE_COMPANY_SOFT_DELETED = "delete_company_soft_deleted"
    DELETE_COMPANY_ERROR_SOFT_DELETE = "delete_company_error_soft_delete"
    DELETE_COMPANY_SUCCESS = "delete_company_success"
    
    # Users Internal Flow
    AUTH_USERS_INTERNAL_LOCATION_REQUIRED = "auth_users_internal_location_required"
    AUTH_USERS_INTERNAL_LOCATION_MISMATCH = "auth_users_internal_location_mismatch"
    
    # Update User Internal Flow
    AUTH_UPDATE_USER_NOT_FOUND = "auth_update_user_not_found"
    AUTH_UPDATE_USER_NOT_IN_LOCATION = "auth_update_user_not_in_location"
    AUTH_UPDATE_USER_CANNOT_DEMOTE_SELF = "auth_update_user_cannot_demote_self"
    AUTH_UPDATE_USER_LAST_ADMIN = "auth_update_user_last_admin"
    AUTH_UPDATE_USER_ROL_NOT_FOUND = "auth_update_user_rol_not_found"
    AUTH_UPDATE_USER_ERROR_FETCHING_ROLES = "auth_update_user_error_fetching_roles"
    AUTH_UPDATE_USER_ERROR = "auth_update_user_error"
    AUTH_UPDATE_USER_ERROR_UPDATING_ROL = "auth_update_user_error_updating_rol"
    AUTH_UPDATE_USER_SUCCESS = "auth_update_user_success"