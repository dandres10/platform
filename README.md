# Proyecto FastAPI - Platform

Este proyecto es una aplicación desarrollada en FastAPI que incluye validación de datos con Pydantic.

## Requisitos previos

- Python 3.11
- pip

## Configuración del entorno de desarrollo

Para comenzar, necesitas crear y activar un entorno virtual para gestionar las dependencias del proyecto.

### Crear el entorno de desarrollo

```bash
python3.11 -m venv env
```

# correr el aplicativo

## crear el entorno de desarrollo

```bash
python3.11 -m venv env
```

## activar el entorno de desarrollo

```bash
source env/bin/activate
```

## instalar las librerias

```bash
pip install -r pipfiles.txt
```

## ejecutar el proyecto en modo pruebas

```bash
ENV=qa uvicorn main:app --reload
```

## ejecutar el proyecto en modo produccion

```bash
ENV=production uvicorn main:app --reload
```
