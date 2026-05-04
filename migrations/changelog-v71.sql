-- liquibase formatted sql
-- changeset spec-006-t9-translations:1746576000000-71

-- SPEC-006 T9

-- ============================================
-- MIGRACION: Traducciones para auth completeness
--
-- Agrega keys de:
-- 1. Email templates: welcome, reset password (subject + body
--    con placeholders {{name}} / {{reset_link}}).
-- 2. Errores y mensajes de los 4 flujos auth: register,
--    change_password, forgot_password, reset_password.
--
-- Context: backend (consistente con resto de mensajes invocados
-- por Message.get_message).
-- ============================================

--RUN

INSERT INTO translation (id, "key", language_code, translation, context, state, created_date, updated_date) VALUES
-- Email welcome (es+en)
(uuid_generate_v4(), 'email_welcome_subject', 'es', 'Bienvenido a Goluti', 'backend', true, now(), now()),
(uuid_generate_v4(), 'email_welcome_subject', 'en', 'Welcome to Goluti', 'backend', true, now(), now()),
(uuid_generate_v4(), 'email_welcome_body', 'es', 'Hola {{name}}, tu cuenta ya está activa. Puedes iniciar sesión en cualquier momento.', 'backend', true, now(), now()),
(uuid_generate_v4(), 'email_welcome_body', 'en', 'Hello {{name}}, your account is now active. You can sign in anytime.', 'backend', true, now(), now()),

-- Email reset password (es+en)
(uuid_generate_v4(), 'email_reset_password_subject', 'es', 'Restablece tu contraseña', 'backend', true, now(), now()),
(uuid_generate_v4(), 'email_reset_password_subject', 'en', 'Reset your password', 'backend', true, now(), now()),
(uuid_generate_v4(), 'email_reset_password_body', 'es', 'Hola {{name}}, haz click en el siguiente enlace para restablecer tu contraseña: {{reset_link}}. El enlace es válido por 1 hora.', 'backend', true, now(), now()),
(uuid_generate_v4(), 'email_reset_password_body', 'en', 'Hello {{name}}, click the link below to reset your password: {{reset_link}}. This link is valid for 1 hour.', 'backend', true, now(), now()),

-- Register flow
(uuid_generate_v4(), 'auth_register_email_already_exists', 'es', 'El correo ya está registrado', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_register_email_already_exists', 'en', 'Email is already registered', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_register_rol_user_not_found', 'es', 'Rol USER no encontrado', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_register_rol_user_not_found', 'en', 'USER role not found', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_register_success', 'es', 'Registro exitoso', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_register_success', 'en', 'Registration successful', 'backend', true, now(), now()),

-- Change password flow
(uuid_generate_v4(), 'auth_change_password_user_not_found', 'es', 'Usuario no encontrado', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_change_password_user_not_found', 'en', 'User not found', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_change_password_old_incorrect', 'es', 'La contraseña actual es incorrecta', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_change_password_old_incorrect', 'en', 'Current password is incorrect', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_change_password_success', 'es', 'Contraseña actualizada', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_change_password_success', 'en', 'Password updated', 'backend', true, now(), now()),

-- Forgot password flow (mensaje genérico, no leakea si email existe o no)
(uuid_generate_v4(), 'auth_forgot_password_generic', 'es', 'Si el correo existe, recibirás un enlace para restablecer tu contraseña', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_forgot_password_generic', 'en', 'If the email exists, you will receive a link to reset your password', 'backend', true, now(), now()),

-- Reset password flow
(uuid_generate_v4(), 'auth_reset_password_token_invalid', 'es', 'Token inválido', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_reset_password_token_invalid', 'en', 'Invalid token', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_reset_password_token_expired', 'es', 'El token ha expirado', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_reset_password_token_expired', 'en', 'Token has expired', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_reset_password_token_already_used', 'es', 'El token ya fue utilizado', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_reset_password_token_already_used', 'en', 'Token has already been used', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_reset_password_success', 'es', 'Contraseña restablecida', 'backend', true, now(), now()),
(uuid_generate_v4(), 'auth_reset_password_success', 'en', 'Password reset', 'backend', true, now(), now());

--FIN RUN

--ROLLBACK
DELETE FROM translation WHERE "key" IN (
    'email_welcome_subject',
    'email_welcome_body',
    'email_reset_password_subject',
    'email_reset_password_body',
    'auth_register_email_already_exists',
    'auth_register_rol_user_not_found',
    'auth_register_success',
    'auth_change_password_user_not_found',
    'auth_change_password_old_incorrect',
    'auth_change_password_success',
    'auth_forgot_password_generic',
    'auth_reset_password_token_invalid',
    'auth_reset_password_token_expired',
    'auth_reset_password_token_already_used',
    'auth_reset_password_success'
);
--FIN ROLLBACK
