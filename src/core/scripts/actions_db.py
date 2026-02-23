#!/usr/bin/env python3
"""
Herramienta de base de datos para backends Goluti.

Subcomandos:
    migrate   — Ejecutar una migración SQL
    rollback  — Ejecutar rollback de una migración
    status    — Ver historial de migraciones ejecutadas
    query     — Ejecutar una consulta SQL ad-hoc

Uso:
    ENV=qa python src/core/scripts/actions_db.py migrate --version 62
    ENV=qa python src/core/scripts/actions_db.py rollback --version 62
    ENV=qa python src/core/scripts/actions_db.py migrate --version 62 --dry-run
    ENV=qa python src/core/scripts/actions_db.py status
    ENV=qa python src/core/scripts/actions_db.py query --sql "SELECT * FROM menu LIMIT 5"
    ENV=qa python src/core/scripts/actions_db.py query --file queries/check_menus.sql

Formato estándar de migración:
    --RUN
    SQL de migración aquí
    --FIN RUN

    --ROLLBACK
    SQL de rollback aquí
    --FIN ROLLBACK
"""

import argparse
import os
import re
import subprocess
import sys

from dotenv import load_dotenv


# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------

def get_project_root():
    """Obtiene la raíz del proyecto (donde está el .env)."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # src/core/scripts/ → 3 niveles arriba
    return os.path.normpath(os.path.join(script_dir, "..", "..", ".."))


def load_env():
    project_root = get_project_root()
    env = os.getenv("ENV", "pc")
    env_file = os.path.join(project_root, f".env.{env}")
    if not os.path.exists(env_file):
        print(f"ERROR: No se encontró {env_file}")
        sys.exit(1)
    load_dotenv(env_file)
    return env


def get_db_config():
    required = ["DATABASE_USER", "DATABASE_PASSWORD", "DATABASE_HOST", "DATABASE_NAME"]
    config = {}
    for key in required:
        value = os.getenv(key, "")
        if not value:
            print(f"ERROR: Variable {key} no definida en el .env")
            sys.exit(1)
        config[key] = value
    config["DATABASE_PORT"] = os.getenv("DATABASE_PORT", "5432")
    config["DATABASE_SCHEMA"] = os.getenv("DATABASE_SCHEMA", "")
    return config


def get_project_name():
    return os.path.basename(get_project_root())


# ---------------------------------------------------------------------------
# psql
# ---------------------------------------------------------------------------

def find_psql():
    """Busca psql en PATH o en ubicaciones conocidas de Homebrew."""
    from shutil import which
    psql = which("psql")
    if psql:
        return psql
    brew_paths = [
        "/opt/homebrew/opt/postgresql@16/bin/psql",
        "/opt/homebrew/opt/postgresql@17/bin/psql",
        "/usr/local/opt/postgresql@16/bin/psql",
    ]
    for path in brew_paths:
        if os.path.exists(path):
            return path
    print("ERROR: psql no encontrado. Instalar con: brew install postgresql@16")
    sys.exit(1)


def build_conn_str(db_config):
    schema = db_config["DATABASE_SCHEMA"]
    base = (
        f"postgresql://{db_config['DATABASE_USER']}:{db_config['DATABASE_PASSWORD']}"
        f"@{db_config['DATABASE_HOST']}:{db_config['DATABASE_PORT']}"
        f"/{db_config['DATABASE_NAME']}"
    )
    if schema:
        return f"{base}?options=-csearch_path%3D{schema}"
    return base


def run_psql_sql(db_config, sql, dry_run=False, quiet=False):
    """Ejecuta SQL inline contra PostgreSQL."""
    if dry_run:
        print("\n--- DRY RUN ---")
        print(sql)
        print("--- FIN DRY RUN ---\n")
        return True

    cmd = [
        find_psql(), build_conn_str(db_config),
        "--single-transaction",
        "--set", "ON_ERROR_STOP=on",
        "-c", sql,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout and not quiet:
        print(result.stdout)
    if result.stderr and not quiet:
        print(result.stderr, file=sys.stderr)
    return result.returncode == 0


def run_psql_file(db_config, filepath, dry_run=False):
    """Ejecuta un archivo SQL completo contra PostgreSQL."""
    if dry_run:
        with open(filepath, "r") as f:
            print("\n--- DRY RUN ---")
            print(f.read())
            print("--- FIN DRY RUN ---\n")
        return True

    cmd = [
        find_psql(), build_conn_str(db_config),
        "--single-transaction",
        "--set", "ON_ERROR_STOP=on",
        "-f", filepath,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode == 0


def run_psql_query(db_config, sql):
    """Ejecuta una consulta y muestra resultados formateados."""
    cmd = [
        find_psql(), build_conn_str(db_config),
        "--pset=pager=off",
        "-c", sql,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode == 0


# ---------------------------------------------------------------------------
# Migraciones: parsing
# ---------------------------------------------------------------------------

def get_migration_path(version):
    path = os.path.join(get_project_root(), f"migrations/changelog-v{version}.sql")
    if not os.path.exists(path):
        print(f"ERROR: No se encontró {path}")
        sys.exit(1)
    return path


def extract_run_sql(filepath):
    """Extrae SQL del bloque --RUN ... --FIN RUN."""
    with open(filepath, "r") as f:
        content = f.read()

    block_pattern = re.compile(
        r"^--\s*RUN\s*$\n(.*?)^--\s*FIN RUN",
        re.MULTILINE | re.DOTALL,
    )
    blocks = block_pattern.findall(content)
    if blocks:
        return "\n".join(block.strip() for block in blocks if block.strip())
    return None


def extract_rollback_sql(filepath):
    """Extrae SQL de rollback (formato bloque o legacy por línea)."""
    with open(filepath, "r") as f:
        content = f.read()
        lines = content.splitlines()

    rollback_statements = []

    # Formato 1: bloque --ROLLBACK ... --FIN ROLLBACK
    block_pattern = re.compile(
        r"^--\s*ROLLBACK\s*$\n(.*?)^--\s*FIN ROLLBACK",
        re.MULTILINE | re.DOTALL,
    )
    blocks = block_pattern.findall(content)
    if blocks:
        for block in blocks:
            sql = block.strip()
            if sql:
                rollback_statements.append(sql)
        return "\n".join(rollback_statements)

    # Formato 2 (legacy): --ROLLBACK SQL;
    for line in lines:
        match = re.match(r"^--\s*ROLLBACK\s+(.+)$", line)
        if match:
            sql = match.group(1).strip()
            if sql:
                rollback_statements.append(sql)

    if rollback_statements:
        return "\n".join(rollback_statements)
    return None


# ---------------------------------------------------------------------------
# Migraciones: tracking
# ---------------------------------------------------------------------------

HISTORY_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS migration_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    version INTEGER NOT NULL,
    env VARCHAR(20) NOT NULL,
    action VARCHAR(10) NOT NULL,
    executed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    filename VARCHAR(200) NOT NULL
);
"""


def ensure_history_table(db_config):
    return run_psql_sql(db_config, HISTORY_TABLE_SQL, quiet=True)


def record_migration(db_config, version, env, action, filename):
    sql = (
        f"INSERT INTO migration_history (version, env, action, filename) "
        f"VALUES ({version}, '{env}', '{action}', '{filename}');"
    )
    return run_psql_sql(db_config, sql, quiet=True)


def check_already_executed(db_config, version, env, action):
    psql = find_psql()
    sql = (
        f"SELECT COUNT(*) FROM migration_history "
        f"WHERE version = {version} AND env = '{env}' AND action = '{action}';"
    )
    cmd = [
        psql, build_conn_str(db_config),
        "--tuples-only", "--no-align",
        "-c", sql,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return False
    count = result.stdout.strip()
    return count.isdigit() and int(count) > 0


# ---------------------------------------------------------------------------
# Subcomandos
# ---------------------------------------------------------------------------

def print_header(db_config, env, extra=None):
    print(f"{'=' * 60}")
    print(f"  Proyecto:   {get_project_name()}")
    print(f"  ENV:        {env}")
    print(f"  Host:       {db_config['DATABASE_HOST']}")
    print(f"  Database:   {db_config['DATABASE_NAME']}")
    print(f"  Schema:     {db_config['DATABASE_SCHEMA'] or '(default)'}")
    if extra:
        for key, value in extra.items():
            print(f"  {key}:  {value}")
    print(f"{'=' * 60}")


def cmd_migrate(args, env, db_config):
    filepath = get_migration_path(args.version)
    filename = os.path.basename(filepath)

    print_header(db_config, env, {"Migración": filename, "Acción": "MIGRATE"})

    if not args.dry_run:
        ensure_history_table(db_config)
        if not args.force and check_already_executed(db_config, args.version, env, "MIGRATE"):
            print(f"\n⚠ v{args.version} ya fue ejecutada (MIGRATE) en env '{env}'.")
            print(f"  Usa --force para ejecutar de nuevo.")
            sys.exit(0)

        confirm = input(f"\n¿Ejecutar migración v{args.version}? (yes/no): ")
        if confirm.lower() != "yes":
            print("Cancelado.")
            sys.exit(0)

    run_sql = extract_run_sql(filepath)
    if run_sql:
        success = run_psql_sql(db_config, run_sql, dry_run=args.dry_run)
    else:
        success = run_psql_file(db_config, filepath, dry_run=args.dry_run)

    if success:
        if not args.dry_run:
            record_migration(db_config, args.version, env, "MIGRATE", filename)
        print(f"\n✓ Migración v{args.version} completada exitosamente")
    else:
        print(f"\n✗ Error ejecutando migración")
        sys.exit(1)


def cmd_rollback(args, env, db_config):
    filepath = get_migration_path(args.version)
    filename = os.path.basename(filepath)

    print_header(db_config, env, {"Migración": filename, "Acción": "ROLLBACK"})

    rollback_sql = extract_rollback_sql(filepath)
    if not rollback_sql:
        print("ERROR: No se encontró SQL de rollback en el archivo")
        sys.exit(1)

    if not args.dry_run:
        ensure_history_table(db_config)
        if not args.force and check_already_executed(db_config, args.version, env, "ROLLBACK"):
            print(f"\n⚠ v{args.version} ya fue ejecutada (ROLLBACK) en env '{env}'.")
            print(f"  Usa --force para ejecutar de nuevo.")
            sys.exit(0)

        confirm = input(f"\n¿Ejecutar ROLLBACK v{args.version}? (yes/no): ")
        if confirm.lower() != "yes":
            print("Cancelado.")
            sys.exit(0)

    success = run_psql_sql(db_config, rollback_sql, dry_run=args.dry_run)

    if success:
        if not args.dry_run:
            record_migration(db_config, args.version, env, "ROLLBACK", filename)
        print(f"\n✓ Rollback v{args.version} completada exitosamente")
    else:
        print(f"\n✗ Error ejecutando rollback")
        sys.exit(1)


def cmd_status(args, env, db_config):
    print(f"{'=' * 60}")
    print(f"  Proyecto:   {get_project_name()}")
    print(f"  ENV:        {env}")
    print(f"  Database:   {db_config['DATABASE_NAME']}")
    print(f"  Schema:     {db_config['DATABASE_SCHEMA'] or '(default)'}")
    print(f"{'=' * 60}\n")

    ensure_history_table(db_config)
    sql = (
        "SELECT version, env, action, "
        "TO_CHAR(executed_at, 'YYYY-MM-DD HH24:MI:SS') as executed_at, "
        "filename "
        "FROM migration_history "
        "ORDER BY version, executed_at;"
    )
    run_psql_query(db_config, sql)


def cmd_query(args, env, db_config):
    if args.file:
        filepath = args.file
        if not os.path.isabs(filepath):
            filepath = os.path.join(get_project_root(), filepath)
        if not os.path.exists(filepath):
            print(f"ERROR: No se encontró {filepath}")
            sys.exit(1)
        with open(filepath, "r") as f:
            sql = f.read()
    elif args.sql:
        sql = args.sql
    else:
        print("ERROR: Debes pasar --sql o --file")
        sys.exit(1)

    schema = db_config["DATABASE_SCHEMA"]
    print(f"  [{get_project_name()}] ENV={env} | Schema={schema or '(default)'}\n")

    run_psql_query(db_config, sql)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Herramienta de base de datos para backends Goluti",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Subcomando a ejecutar")

    # migrate
    p_migrate = subparsers.add_parser("migrate", help="Ejecutar una migración")
    p_migrate.add_argument("--version", "-v", required=True, type=int,
                           help="Versión del changelog (ej: 62)")
    p_migrate.add_argument("--dry-run", "-d", action="store_true",
                           help="Mostrar SQL sin ejecutar")
    p_migrate.add_argument("--force", "-f", action="store_true",
                           help="Ejecutar aunque ya se haya corrido en este env")

    # rollback
    p_rollback = subparsers.add_parser("rollback", help="Ejecutar rollback de una migración")
    p_rollback.add_argument("--version", "-v", required=True, type=int,
                            help="Versión del changelog (ej: 62)")
    p_rollback.add_argument("--dry-run", "-d", action="store_true",
                            help="Mostrar SQL sin ejecutar")
    p_rollback.add_argument("--force", "-f", action="store_true",
                            help="Ejecutar aunque ya se haya corrido en este env")

    # status
    subparsers.add_parser("status", help="Ver historial de migraciones ejecutadas")

    # query
    p_query = subparsers.add_parser("query", help="Ejecutar consulta SQL")
    p_query.add_argument("--sql", "-q", type=str,
                         help="SQL a ejecutar (inline)")
    p_query.add_argument("--file", type=str,
                         help="Archivo SQL a ejecutar")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    env = load_env()
    db_config = get_db_config()

    commands = {
        "migrate": cmd_migrate,
        "rollback": cmd_rollback,
        "status": cmd_status,
        "query": cmd_query,
    }
    commands[args.command](args, env, db_config)


if __name__ == "__main__":
    main()
