import getpass
import json
import os
from pathlib import Path

from app import TEACHERS_FILE, hash_password


def main():
    username = input("Teacher username: ").strip()
    if not username:
        raise SystemExit("Username cannot be empty")

    password = getpass.getpass("Password (at least 12 characters): ")
    if len(password) < 12:
        raise SystemExit("Password must be at least 12 characters")
    if password != getpass.getpass("Confirm password: "):
        raise SystemExit("Passwords do not match")

    try:
        teachers = json.loads(TEACHERS_FILE.read_text(encoding="utf-8"))
    except FileNotFoundError:
        teachers = {}
    except (OSError, json.JSONDecodeError) as error:
        raise SystemExit("Unable to read teacher credentials") from error

    if not isinstance(teachers, dict):
        raise SystemExit("Teacher credentials file must contain a JSON object")
    if username in teachers and input("Replace this teacher account? [y/N] ").lower() != "y":
        raise SystemExit("Account was not changed")

    teachers[username] = hash_password(password)
    TEACHERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary_file = TEACHERS_FILE.with_name(TEACHERS_FILE.name + ".tmp")
    temporary_file.write_text(json.dumps(teachers, indent=2) + "\n", encoding="utf-8")
    os.chmod(temporary_file, 0o600)
    os.replace(temporary_file, TEACHERS_FILE)
    print(f"Teacher account saved in {TEACHERS_FILE}")


if __name__ == "__main__":
    main()