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