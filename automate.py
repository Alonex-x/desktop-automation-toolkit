#!/usr/bin/env python3
"""
Desktop Automation Toolkit - Automatización de tareas de archivos para desarrolladores y sysadmins.
"""
import os
import shutil
import argparse
import logging
import json
import subprocess
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

RULES_FILENAME = "automate_rules.json"


def get_rules_path():
    """Devuelve la ruta esperada del archivo de reglas, junto al script."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, RULES_FILENAME)


def load_rules():
    """
    Carga las reglas desde automate_rules.json.
    Si el archivo no existe o está mal formado, retorna una lista vacía
    y se conserva el comportamiento por defecto del script.
    """
    rules_path = get_rules_path()

    if not os.path.exists(rules_path):
        logging.info(f"No se encontró {RULES_FILENAME}. Usando comportamiento por defecto.")
        return []

    try:
        with open(rules_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        rules = data.get("rules", [])
        if not isinstance(rules, list):
            raise ValueError("La clave 'rules' debe ser una lista.")
        logging.info(f"Se cargaron {len(rules)} regla(s) desde {RULES_FILENAME}.")
        return rules
    except (json.JSONDecodeError, ValueError, OSError) as e:
        logging.warning(f"No se pudo leer {RULES_FILENAME} ({e}). Usando comportamiento por defecto.")
        return []


def _extension_matches(filename, value):
    """Compara la extensión del archivo contra un valor (string o lista de strings)."""
    ext = os.path.splitext(filename)[1].lower()  # incluye el punto, ej: ".torrent"
    if isinstance(value, list):
        return ext in [v.lower() for v in value]
    return ext == value.lower()


def match_rule(filename, rules):
    """
    Evalúa las reglas en orden y retorna la primera que coincida con el archivo,
    o None si ninguna coincide.
    """
    for rule in rules:
        condition = rule.get("condition", {})
        cond_type = condition.get("type")

        if cond_type == "extension":
            value = condition.get("value")
            if value and _extension_matches(filename, value):
                return rule
        # Punto de extensión: aquí se pueden añadir más tipos de condición
        # (ej. "name_contains", "size_greater_than") en el futuro.

    return None


def apply_rule_action(rule, file_path, base_path, dry_run=False):
    """
    Ejecuta la acción definida en una regla sobre un archivo.
    Retorna True si el archivo fue "consumido" por la regla (delete/move/ignore),
    en cuyo caso el llamador no debe aplicar el comportamiento por defecto.
    """
    action = rule.get("action")
    rule_name = rule.get("name", "(sin nombre)")

    if action == "delete":
        if dry_run:
            print(f"[DRY RUN] Regla '{rule_name}' eliminaría: {file_path}")
        else:
            os.remove(file_path)
            logging.info(f"Regla '{rule_name}': eliminado {file_path}")
        return True

    elif action == "move":
        destination = rule.get("destination")
        if not destination:
            logging.error(f"Regla '{rule_name}': acción 'move' sin 'destination' definido. Se omite el archivo.")
            return True
        dest_dir = os.path.join(base_path, destination)
        try:
            if dry_run:
                print(f"[DRY RUN] Regla '{rule_name}' movería {file_path} -> {dest_dir}/")
            else:
                os.makedirs(dest_dir, exist_ok=True)
                shutil.move(file_path, os.path.join(dest_dir, os.path.basename(file_path)))
                logging.info(f"Regla '{rule_name}': movido {file_path} -> {dest_dir}/")
        except OSError as e:
            logging.error(f"Regla '{rule_name}': no se pudo mover {file_path} ({e}). Se omite el archivo.")
        return True

    elif action == "ignore":
        if dry_run:
            print(f"[DRY RUN] Regla '{rule_name}' ignora: {file_path}")
        else:
            logging.info(f"Regla '{rule_name}': ignorado {file_path}")
        return True

    else:
        logging.warning(f"Regla '{rule_name}': acción desconocida '{action}'. Se ignora la regla.")
        return False


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
    """Elimina archivos temporales y logs antiguos, respetando reglas personalizadas."""
    rules = load_rules()
    now = datetime.now().timestamp()
    deleted_count = 0

    for root, _, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)

            # 1. Evaluar reglas personalizadas primero (tienen prioridad).
            rule = match_rule(file, rules)
            if rule:
                consumed = apply_rule_action(rule, file_path, path, dry_run)
                if consumed:
                    continue  # La regla ya decidió qué hacer con este archivo.

            # 2. Comportamiento por defecto si ninguna regla aplicó.
            if file.endswith((".tmp", ".log", ".bak", "~")):
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
    """Organiza archivos en subcarpetas por extensión, respetando reglas personalizadas."""
    rules = load_rules()
    moved_count = 0

    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if not os.path.isfile(item_path):
            continue

        # 1. Evaluar reglas personalizadas primero (tienen prioridad).
        rule = match_rule(item, rules)
        if rule:
            consumed = apply_rule_action(rule, item_path, path, dry_run)
            if consumed:
                continue  # La regla ya decidió qué hacer con este archivo.

        # 2. Comportamiento por defecto si ninguna regla aplicó.
        ext = item.split(".")[-1].lower() if "." in item else "sin_extension"
        dest_dir = os.path.join(path, ext)
        if not dry_run:
            os.makedirs(dest_dir, exist_ok=True)
            shutil.move(item_path, os.path.join(dest_dir, item))
            logging.info(f"Movido: {item} -> {ext}/")
        moved_count += 1

    logging.info(f"Organización completada. Archivos movidos: {moved_count}")


def backup_directory(source, destination, compress=False):
    """Respaldar directorio completo con opción de comprimir. No se ve afectado por las reglas."""
    if compress:
        # Crear archivo tar.gz
        backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"
        backup_path = os.path.join(destination, backup_name)
        # Usamos subprocess.run en lugar de os.system para evitar inyección de comandos
        subprocess.run(["tar", "-czf", backup_path, source], check=True)
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
