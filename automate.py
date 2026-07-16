#!/usr/bin/env python3
"""
Desktop Automation Toolkit - File automation for developers and sysadmins.
"""
import os
import shutil
import argparse
import logging
import json
import subprocess
from datetime import datetime

# Logging configuration
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
    """Returns the expected path for the rules file, next to this script."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, RULES_FILENAME)


def load_rules():
    """
    Load rules from automate_rules.json.
    If the file doesn't exist or is malformed, returns an empty list
    and falls back to default behavior.
    """
    rules_path = get_rules_path()

    if not os.path.exists(rules_path):
        logging.info(f"{RULES_FILENAME} not found. Using default behavior.")
        return []

    try:
        with open(rules_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        rules = data.get("rules", [])
        if not isinstance(rules, list):
            raise ValueError("The 'rules' key must be a list.")
        logging.info(f"Loaded {len(rules)} rule(s) from {RULES_FILENAME}.")
        return rules
    except (json.JSONDecodeError, ValueError, OSError) as e:
        logging.warning(f"Could not read {RULES_FILENAME} ({e}). Using default behavior.")
        return []


def _extension_matches(filename, value):
    """Checks if the file extension matches a value (string or list of strings)."""
    ext = os.path.splitext(filename)[1].lower()
    if isinstance(value, list):
        return ext in [v.lower() for v in value]
    return ext == value.lower()


def match_rule(filename, rules):
    """
    Evaluates rules in order and returns the first one that matches the file,
    or None if no rule matches.
    """
    for rule in rules:
        condition = rule.get("condition", {})
        cond_type = condition.get("type")

        if cond_type == "extension":
            value = condition.get("value")
            if value and _extension_matches(filename, value):
                return rule
        # Extension point: more condition types can be added here
        # (e.g. "name_contains", "size_greater_than") in the future.

    return None


def apply_rule_action(rule, file_path, base_path, dry_run=False):
    """
    Executes the action defined in a rule on a file.
    Returns True if the file was "consumed" by the rule (delete/move/ignore),
    meaning the caller should skip the default behavior.
    """
    action = rule.get("action")
    rule_name = rule.get("name", "(unnamed)")

    if action == "delete":
        if dry_run:
            print(f"[DRY RUN] Rule '{rule_name}' would delete: {file_path}")
        else:
            os.remove(file_path)
            logging.info(f"Rule '{rule_name}': deleted {file_path}")
        return True

    elif action == "move":
        destination = rule.get("destination")
        if not destination:
            logging.error(f"Rule '{rule_name}': 'move' action without 'destination'. Skipping file.")
            return True
        dest_dir = os.path.join(base_path, destination)
        try:
            if dry_run:
                print(f"[DRY RUN] Rule '{rule_name}' would move {file_path} -> {dest_dir}/")
            else:
                os.makedirs(dest_dir, exist_ok=True)
                shutil.move(file_path, os.path.join(dest_dir, os.path.basename(file_path)))
                logging.info(f"Rule '{rule_name}': moved {file_path} -> {dest_dir}/")
        except OSError as e:
            logging.error(f"Rule '{rule_name}': could not move {file_path} ({e}). Skipping file.")
        return True

    elif action == "ignore":
        if dry_run:
            print(f"[DRY RUN] Rule '{rule_name}' ignores: {file_path}")
        else:
            logging.info(f"Rule '{rule_name}': ignored {file_path}")
        return True

    else:
        logging.warning(f"Rule '{rule_name}': unknown action '{action}'. Ignoring this rule.")
        return False


def setup_argparse():
    parser = argparse.ArgumentParser(description="Desktop Automation Toolkit")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # clean command
    clean_parser = subparsers.add_parser("clean", help="Delete old temporary files")
    clean_parser.add_argument("path", help="Directory to clean")
    clean_parser.add_argument("--days", type=int, default=30, help="Delete files older than N days (default: 30)")
    clean_parser.add_argument("--dry-run", action="store_true", help="Only show what would be deleted without actually removing anything")

    # organize command
    org_parser = subparsers.add_parser("organize", help="Organize files by extension")
    org_parser.add_argument("path", help="Directory to organize")
    org_parser.add_argument("--dry-run", action="store_true", help="Only show what would be moved without actually reorganizing anything")

    # backup command
    backup_parser = subparsers.add_parser("backup", help="Backup a directory")
    backup_parser.add_argument("source", help="Source directory")
    backup_parser.add_argument("destination", help="Backup destination directory")
    backup_parser.add_argument("--compress", action="store_true", help="Create a compressed archive instead of copying")

    return parser.parse_args()


def clean_temp_files(path, days=30, dry_run=False):
    """Delete old temporary and log files, respecting custom rules."""
    rules = load_rules()
    now = datetime.now().timestamp()
    deleted_count = 0

    for root, _, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)

            # 1. Evaluate custom rules first (they have priority).
            rule = match_rule(file, rules)
            if rule:
                consumed = apply_rule_action(rule, file_path, path, dry_run)
                if consumed:
                    continue

            # 2. Default behavior if no rule matched.
            if file.endswith((".tmp", ".log", ".bak", "~")):
                file_age = now - os.path.getmtime(file_path)
                if file_age > days * 86400:
                    if dry_run:
                        print(f"[DRY RUN] Would delete: {file_path}")
                    else:
                        os.remove(file_path)
                        logging.info(f"Deleted: {file_path}")
                        deleted_count += 1

    logging.info(f"Cleanup completed. Files deleted: {deleted_count}")


def organize_by_extension(path, dry_run=False):
    """Organize files into subfolders by extension, respecting custom rules."""
    rules = load_rules()
    moved_count = 0

    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if not os.path.isfile(item_path):
            continue

        # 1. Evaluate custom rules first (they have priority).
        rule = match_rule(item, rules)
        if rule:
            consumed = apply_rule_action(rule, item_path, path, dry_run)
            if consumed:
                continue

        # 2. Default behavior if no rule matched.
        ext = item.split(".")[-1].lower() if "." in item else "no_extension"
        dest_dir = os.path.join(path, ext)
        if not dry_run:
            os.makedirs(dest_dir, exist_ok=True)
            shutil.move(item_path, os.path.join(dest_dir, item))
            logging.info(f"Moved: {item} -> {ext}/")
        moved_count += 1

    logging.info(f"Organization completed. Files moved: {moved_count}")


def backup_directory(source, destination, compress=False):
    """Backup a complete directory. Not affected by custom rules."""
    if compress:
        backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz"
        backup_path = os.path.join(destination, backup_name)
        subprocess.run(["tar", "-czf", backup_path, source], check=True)
        logging.info(f"Compressed backup created at: {backup_path}")
    else:
        dest_dir = os.path.join(destination, os.path.basename(source.rstrip("/")))
        shutil.copytree(source, dest_dir)
        logging.info(f"Backup copied to: {dest_dir}")


def main():
    args = setup_argparse()
    if args.command == "clean":
        clean_temp_files(args.path, args.days, args.dry_run)
    elif args.command == "organize":
        organize_by_extension(args.path, args.dry_run)
    elif args.command == "backup":
        backup_directory(args.source, args.destination, args.compress)
    else:
        print("Use --help to see available commands.")


if __name__ == "__main__":
    main()
