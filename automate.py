#!/usr/bin/env python3
"""
Desktop Automation Toolkit - Automatización de tareas de archivos para desarrolladores y sysadmins.
"""
import os
import shutil
import argparse
import logging
from datetime import datetime

# Configuración de logging
LOG_FILE = os.path.expanduser("~/.automate_toolkit.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

def setup_argparse():
    parser = argparse.ArgumentParser(description="Desktop Automation Toolkit")
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    # Comando: clean
    clean_parser = subparsers.add_parser("clean", help="Eliminar archivos temporales")
    clean_parser.add_argument("path", help="Directorio a limpiar")
    clean_parser.add_argument("--days", type=int, default=30, help="Eliminar archivos más antiguos de N días (default: 30)")
    clean_parser.add_argument("--dry-run", action="store_true", help="Solo mostrar lo que se eliminaría sin borrar realmente")

    # Comando: organize
    org_parser = subparsers.add_parser("organize", help="Organizar archivos por extensión")
    org_parser.add_argument("path", help="Directorio a organizar")
    org_parser.add_argument("--dry-run", action="store_true", help="Solo mostrar lo que se movería sin reorganizar realmente")

    # Comando: backup
    backup_parser = subparsers.add_parser("backup", help="Respaldar un directorio")
    backup_parser.add_argument("source", help="Directorio origen")
    backup_parser.add_argument("destination", help="Directorio destino del respaldo")
    backup_parser.add_argument("--compress", action="store_true", help="Crear archivo comprimido en lugar de copiar")

    return parser.parse_args()

def clean_temp_files(path, days=30, dry_run=False):
    """Elimina archivos temporales y logs antiguos."""
    now = datetime.now().timestamp()
    deleted_count = 0
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith((".tmp", ".log", ".bak", "~")):
                file_path = os.path.join(root, file)
                file_age = now - os.path.getmtime(file_path)
                if file_age > days * 86400:
                    if dry_run:
                        print(f"[DRY RUN] Eliminaría: {file_path}")
                    else:
                        os.remove(file_path)
                        logging.info(f"Eliminado: {file_path}")
                        deleted_count += 1
    logging.info(f"Limpieza completada. Archivos eliminados: {deleted_count}")

def organize_by_extension(path, dry_run=False):
    """Organiza archivos en subcarpetas por extensión."""
    moved_count = 0
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isfile(item_path):
            ext = item.split(".")[-1].lower() if "." in item else "sin_extension"
            dest_dir = os.path.join(path, ext)
            if not dry_run:
                os.makedirs(dest_dir, exist_ok=True)
                shutil.move(item_path, os.path.join(dest_dir, item))
                logging.info(f"Movido: {item} -> {ext}/")
            moved_count += 1
    logging.info(f"Organización completada. Archivos movidos: {moved_count}")

def backup_directory(source, destination, compress=False):
    """Respaldar directorio completo con opción de comprimir."""
    if compress:
        # Crear archivo tar.gz
        backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"
        backup_path = os.path.join(destination, backup_name)
        os.system(f"tar -czf {backup_path} {source}")
        logging.info(f"Respaldo comprimido creado en: {backup_path}")
    else:
        # Copia recursiva
        dest_dir = os.path.join(destination, os.path.basename(source.rstrip("/")))
        shutil.copytree(source, dest_dir)
        logging.info(f"Respaldo copiado en: {dest_dir}")

def main():
    args = setup_argparse()
    if args.command == "clean":
        clean_temp_files(args.path, args.days, args.dry_run)
    elif args.command == "organize":
        organize_by_extension(args.path, args.dry_run)
    elif args.command == "backup":
        backup_directory(args.source, args.destination, args.compress)
    else:
        print("Usa --help para ver los comandos disponibles.")

if __name__ == "__main__":
    main()
