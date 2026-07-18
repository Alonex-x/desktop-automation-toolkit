```markdown
# Desktop Automation Toolkit

![Python](https://img.shields.io/badge/Python-3.6+-blue?logo=python)

A Python command-line tool to automate file management tasks. Organize messy folders, clean up old temporary files, and create compressed backups — all from the terminal. It also includes a custom JSON rules engine so you can define your own automation logic without modifying the script.

## Features

- **`organize`** – Automatically sort files into subfolders by extension.
- **`clean`** – Remove old temporary files (`.tmp`, `.log`, `.bak`, `~`) older than a configurable threshold.
- **`backup`** – Create full directory backups, with optional compression.
- **Custom rules engine** – Define rules in `automate_rules.json` to delete, move, or ignore files based on their extension. Rules are evaluated before the default behavior.
- **Dry-run mode** – Preview every action safely before committing changes.

## Usage

```bash
# Organize files by extension (with dry-run preview)
python automate.py organize /home/user/Documents --dry-run

# Clean up temporary files older than 30 days
python automate.py clean /home/user/Downloads --days 30

# Backup a directory with compression
python automate.py backup /home/user/project /home/user/backups --compress
```

## Custom Rules Engine

The toolkit supports an optional JSON rules engine through an `automate_rules.json` file placed in the same folder as `automate.py`. Rules let you automate specific actions without touching the source code.

### How it works

- Rules are evaluated in order. The first match is applied.
- If no rule matches, the default command behavior takes over.
- The `backup` command ignores rules entirely.

### JSON structure

```json
{
  "rules": [
    {
      "name": "Rule name (for logging)",
      "description": "What this rule does",
      "condition": {
        "type": "extension",
        "value": ".torrent"
      },
      "action": "delete"
    }
  ]
}
```

### Supported actions

| Action   | Description                                | Extra field required |
|----------|--------------------------------------------|----------------------|
| `delete` | Remove the file permanently.               | None                 |
| `move`   | Move the file to a subfolder.              | `"destination"`      |
| `ignore` | Skip the file without any further action.  | None                 |

### Supported conditions (current)

| Condition type | Match logic                              | Example value          |
|----------------|------------------------------------------|------------------------|
| `extension`    | Matches file extensions.                 | `".torrent"` or `[".jpg", ".png"]` |

*Planned: `name_contains`, `size_greater_than`, `date_older_than`.*

### Example `automate_rules.json`

```json
{
  "rules": [
    {
      "name": "Delete old torrents",
      "description": "Remove any .torrent file found.",
      "condition": {
        "type": "extension",
        "value": ".torrent"
      },
      "action": "delete"
    },
    {
      "name": "Group images into 'Photos'",
      "description": "Move all image files to a Photos folder.",
      "condition": {
        "type": "extension",
        "value": [".jpg", ".jpeg", ".png", ".gif"]
      },
      "action": "move",
      "destination": "Photos"
    },
    {
      "name": "Ignore system files",
      "description": "Skip .sys and .dll files.",
      "condition": {
        "type": "extension",
        "value": [".sys", ".dll"]
      },
      "action": "ignore"
    }
  ]
}
```

### Error handling

- Missing or malformed JSON? The script logs a warning and falls back to default behavior.
- A `move` rule that fails (e.g., unwritable destination) logs an error and skips the file.

## Requirements

- Python 3.6 or newer.
- Standard library only — no external dependencies.
- Compatible with Linux, macOS, and Windows (WSL).

## Feedback & Contributions

This is part of my self-taught developer portfolio. If you have ideas for new rule types, features, or improvements, pull requests and issues are genuinely welcome. Also, if you need help with automation, scraping, or WordPress, feel free to reach out.
```

