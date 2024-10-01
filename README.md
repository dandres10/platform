# Proyecto FastAPI - Platform

Este proyecto es una aplicación desarrollada en FastAPI que incluye validación de datos con Pydantic.

## Requisitos previos

- **Python 3.11**
- **pip**

## Configuración del entorno de desarrollo

Para comenzar, es necesario crear y activar un entorno virtual para gestionar las dependencias del proyecto.

### 1. Crear el entorno de desarrollo

```bash
python3.11 -m venv env
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
```

### 2. Ejecutar en modo producción

```bash
ENV=production uvicorn main:app --reload
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


docker build -f Dockerfile.qa -t nombre_de_tu_imagen .

subir imagen de docker a docker-hub que sea compatible con la arq de linux del servidor

0. docker buildx create --use
1. docker buildx build --platform linux/amd64 -f Dockerfile.qa -t andresleonleon/backend-platform-qa:v5 --load .
2. docker inspect andresleonleon/backend-platform-qa:v5 
3. docker push andresleonleon/backend-platform-qa:v4 


---









