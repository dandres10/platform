import os
from openai import OpenAI
import subprocess

client = OpenAI(
    api_key="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"  # Asegúrate de mantener segura tu API Key
)

# Lista de carpetas y archivos a excluir
EXCLUDE_LIST = [
    "ia",
    "env",
    "__pycache__",
    ".gitignore",
    ".git",
    "conversation_log.txt",
    "Dockerfile",
]

def split_text_into_chunks(text, chunk_size=3000):
    """Divide un texto en partes más pequeñas."""
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def interact_with_chatgpt(prompt, knowledge_base=None):
    # Si knowledge_base no se pasa o está vacío, cargar desde el archivo
    if not knowledge_base:
        if os.path.exists("conversation_log.txt"):
            with open("conversation_log.txt", "r") as file:
                knowledge_base = file.read()
        else:
            # Si no hay archivo y no se ha explorado, devolver un mensaje de error
            return "No se ha explorado el proyecto ni se ha encontrado una base de conocimiento. Por favor, ejecuta el comando 'explorar' primero."

    # Dividir la base de conocimiento en chunks
    chunks = split_text_into_chunks(knowledge_base)

    # Inicializa la conversación con la primera parte de la base de conocimiento
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # O "gpt-4" si tienes acceso
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": chunks[0]},
        ],
        max_tokens=150,
    )



    # Itera sobre los chunks restantes para continuar la conversación
    for chunk in chunks[1:]:
        print("load...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": chunk},
            ],
            max_tokens=150,
        )

    # Finalmente, añade el prompt del usuario y procesa la respuesta final
    final_prompt = f"{chunks[-1]}\n\n{prompt}"
    final_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": final_prompt},
        ],
        max_tokens=150,
    )

    return final_response.choices[0].message.content.strip()

def should_exclude(path, exclude_list):
    """Verifica si el archivo o directorio debe ser excluido basado en la ruta relativa."""
    # Convierte la ruta en una lista de componentes para una comparación más precisa
    normalized_path = os.path.normpath(path).split(os.sep)
    for exclude in exclude_list:
        if exclude in normalized_path:
            return True
    return False

# Función para explorar la estructura del proyecto, excluyendo ciertas carpetas y archivos
def explore_directory(path="."):
    structure = {}

    for root, dirs, files in os.walk(path):
        # Filtrar directorios que están en la lista de exclusión
        dirs[:] = [d for d in dirs if not should_exclude(os.path.relpath(os.path.join(root, d), path), EXCLUDE_LIST)]
        # Filtrar archivos que están en la lista de exclusión
        files = [f for f in files if not should_exclude(os.path.relpath(os.path.join(root, f), path), EXCLUDE_LIST)]

        relative_path = os.path.relpath(root, path)

        # Leer y agregar el contenido de los archivos
        file_contents = {}
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                file_contents[file] = content
            except UnicodeDecodeError:
                print(f"Warning: No se pudo decodificar {file_path} como UTF-8, omitiendo el archivo.")
            except Exception as e:
                print(f"Error al leer el archivo {file_path}: {e}")

        # Solo agregar directorios que tienen archivos después de filtrar
        if file_contents:
            structure[relative_path] = file_contents

    return structure

# Función para crear un resumen de la arquitectura y añadirlo al archivo de conversación
def create_knowledge_base_and_log(structure):
    knowledge_base = "Aquí está la estructura del proyecto y un resumen de los contenidos:\n\n"
    
    for directory, files in structure.items():
        knowledge_base += f"Directorio: {directory}\n"
        for file_name, content in files.items():
            knowledge_base += f"  Archivo: {file_name}\n    Contenido: {content}\n\n"
    
    # Guardar esta información en el archivo de conversación
    with open("conversation_log.txt", "a") as file:
        file.write(knowledge_base + "\n")
    
    return knowledge_base

# Función para ejecutar comandos del sistema
def execute_command(command):
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return result.stdout.decode("utf-8")
    except subprocess.CalledProcessError as e:
        return f"An error occurred: {e.stderr.decode('utf-8')}"

# Función para leer el contenido de archivos
def read_file_content(file_path):
    if not os.path.exists(file_path):
        return {"error": "File not found"}

    with open(file_path, "r") as file:
        content = file.read()

    return content

# Funciones específicas para ejecutar
def some_function():
    return "Este es el resultado de ejecutar some_function."

def another_function():
    return "Este es el resultado de ejecutar another_function."

# Función para ejecutar funciones específicas
def execute_function(func_name):
    functions = {
        "some_function": some_function,
        "another_function": another_function,
    }

    if func_name in functions:
        return functions[func_name]()
    else:
        return "Función no encontrada."

# Función para guardar la conversación en un archivo
def save_conversation(user_input, response):
    with open("conversation_log.txt", "a") as file:
        file.write(f"Tú: {user_input}\n")
        file.write(f"ChatGPT: {response}\n\n")

# Función principal
def main():
    print("ChatGPT CLI. Escribe 'exit' para salir.")
    print(
        "Comandos disponibles: 'explorar', 'leer archivo <ruta>', 'ejecuta <comando>', 'ejecuta función <nombre>'"
    )

    while True:
        user_input = input("Tú: ")

        if user_input.lower() == "exit":
            break

        if user_input.startswith("explorar"):
            structure = explore_directory()
            knowledge_base = create_knowledge_base_and_log(structure)
            response = "Estructura explorada y añadida a la base de conocimiento."
            print(response)
            save_conversation(user_input, response)

        elif user_input.startswith("leer archivo "):
            file_path = user_input.replace("leer archivo ", "")
            content = read_file_content(file_path)
            response = (
                content if isinstance(content, str) else "Error leyendo el archivo."
            )
            print(response)
            save_conversation(user_input, response)

        elif user_input.startswith("ejecuta función "):
            func_name = user_input.replace("ejecuta función ", "")
            output = execute_function(func_name)
            print(f"Resultado: {output}")
            save_conversation(user_input, output)

        elif user_input.startswith("ejecuta "):
            command = user_input.replace("ejecuta ", "")
            output = execute_command(command)
            print(f"Resultado: {output}")
            save_conversation(user_input, output)

        else:
            response = interact_with_chatgpt(user_input)
            print(f"ChatGPT: {response}")
            save_conversation(user_input, response)

if __name__ == "__main__":
    main()