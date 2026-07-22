# Desktop Automation Toolkit

A Python tool that automates file organization using JSON rules. Define conditions (by extension, name pattern) and actions (move, delete, ignore) to keep directories clean without manual effort.

## Features
- Rule-based automation: define conditions and actions in a JSON file.
- Organize command: apply rules to a target directory.
- Dry-run mode: preview every action safely before committing changes.

## Usage
# Organize files by extension (with dry-run preview)
python -m src.main organize /path/to/directory --rules rules.json --dry-run

# Apply rules for real
python -m src.main organize /path/to/directory --rules rules.json

This is part of my self-taught developer portfolio. If you have ideas for new rule types, features, or improvements, pull requests and issues are genuinely welcome.
