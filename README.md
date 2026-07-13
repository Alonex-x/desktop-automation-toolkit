# Desktop Automation Toolkit

[![Python](https://img.shields.io/badge/Python-3.6+-blue?logo=python)](https://python.org)

Conjunto de herramientas de línea de comandos para automatizar tareas repetitivas de archivos en sistemas Linux/Unix. Ideal para desarrolladores y administradores de sistemas que buscan productividad sin depender de interfaces gráficas.

## Funcionalidades

- **`clean`**: Elimina archivos temporales (`.tmp`, `.log`, `.bak`) más antiguos de un umbral configurable.
- **`organize`**: Organiza automáticamente archivos en subcarpetas por su extensión.
- **`backup`**: Crea respaldos completos de directorios, con opción de comprimir.

## Uso

```bash
# Limpiar archivos temporales con más de 30 días
python automate.py clean /home/usuario/Downloads --days 30

# Organizar automáticamente una carpeta (sin borrar nada en modo dry-run)
python automate.py organize /home/usuario/Documentos --dry-run

# Respaldar un directorio comprimido
python automate.py backup /home/usuario/proyecto /home/usuario/backups --compress
```

## Requisitos

- Python 3.6 o superior.
- Solo utiliza módulos estándar de Python (`os`, `shutil`, `argparse`, `logging`, `datetime`). No requiere instalar dependencias externas.
- Compatible con Linux, macOS y WSL.

## Contribuciones

Las contribuciones son bienvenidas. Si encuentras un error o tienes una idea para mejorar el proyecto, abre un *issue* o envía un *pull request*.

