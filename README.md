# Proyecto FastAPI - Platform

Este proyecto es una aplicación desarrollada en FastAPI que incluye validación de datos con Pydantic.

## Requisitos previos

- **Python 3.12**
- **pip**

## Configuración del entorno de desarrollo

Para comenzar, es necesario crear y activar un entorno virtual para gestionar las dependencias del proyecto.

### 1. Crear el entorno de desarrollo

```bash
python3.12 -m venv env
```

### 2. Activar el entorno de desarrollo

```bash
source env/bin/activate
```

### 3. Instalar las librerías

```bash
pip install -r pipfiles.txt
```

## Ejecutar el proyecto

### 1. Ejecutar en modo local (PC)

```bash
ENV=pc uvicorn main:app --reload
ENV=pc uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Ejecutar en modo producción

```bash
ENV=prod uvicorn main:app --reload
```

### 2. Ejecutar en modo qa

```bash
ENV=qa uvicorn main:app --reload
```


## Comandos Docker y Docker Compose

### Eliminar todos los contenedores existentes

```bash
docker rm $(docker ps -aq)
```

### Docker Compose - Ambiente local

- **Crear y construir contenedor**:

```bash
sudo docker-compose -f docker-compose.local.yml up --build
```

- **Iniciar el contenedor sin construir**:

```bash
sudo docker-compose -f docker-compose.local.yml up
```

### Docker Compose - Ambiente QA

- **Crear y construir contenedor en QA**:

```bash
sudo docker-compose -f docker-compose.qa.yml up --build
```


### Docker Compose - Ambiente PROD

- **Crear y construir contenedor en QA**:

```bash
sudo docker-compose -f docker-compose.prod.yml up --build
```


docker build -f Dockerfile.qa -t nombre_de_tu_imagen .

subir imagen de docker a docker-hub que sea compatible con la arq de linux del servidor

0. docker buildx create --use
1. docker buildx build --platform linux/amd64 -f Dockerfile.qa -t andresleonleon/backend-platform-qa:v5 --load .
2. docker inspect andresleonleon/backend-platform-qa:v5 
3. docker push andresleonleon/backend-platform-qa:v4 


---

## Claude Code Agents

Este proyecto incluye agentes personalizados para Claude Code en `.claude/agents/`.

### Agentes Disponibles

- **backend-developer-platform**: Especializado en crear Entity Flows (CRUD) y Business Flows complejos
- **database-expert-platform**: Especializado en PostgreSQL, SQLAlchemy, migraciones y optimización de queries
- **code-reviewer-platform**: Especializado en revisar código siguiendo Clean Architecture y patrones del proyecto

### Instalar agentes de forma global

Para usar los agentes desde cualquier proyecto, copia todos los agentes a tu directorio global:

```bash
cp -r .claude/agents ~/.claude/
```

### Instalar agentes de forma local (solo este proyecto)

Si prefieres que los agentes estén disponibles solo en este proyecto, ya están configurados en `.claude/agents/` y puedes invocarlos directamente.

### Uso

En una conversación de Claude Code, invócalos con:

```
@backend-developer-platform <tu solicitud>
@database-expert-platform <tu solicitud>
@code-reviewer-platform <tu solicitud>
```

**Ejemplos:**

```
@backend-developer-platform Necesito crear una nueva entidad "Product" con CRUD completo

@database-expert-platform Optimiza este query que está lento: SELECT * FROM user WHERE platform_id = '...'

@code-reviewer-platform Revisa este código y verifica que cumple con Clean Architecture
```

### Documentación

Para más información sobre qué hace cada agente y cuándo usarlo, consulta:

- **Guía completa**: `.claude/README.md`
- **Agentes**: `.claude/agents/`

---







