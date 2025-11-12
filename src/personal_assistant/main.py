import difflib
from personal_assistant.storage import (
    load_addressbook, save_addressbook, load_notes, save_notes,
    ABOOK_FILE, NOTES_FILE
)
from personal_assistant.command_handler import handle_command

SAVE_EVERY = 1  # автозбереження кожні N дій

COMMANDS = {
    "add", "add-address", "email", "add-birthday", "edit-phone", "remove-phone",
    "delete", "show", "show-contact", "find", "birthdays",
    "add-note", "edit-note", "delete-note", "add-tag", "remove-tag",
    "find-note", "show-notes", "show-notes-by-tag", "help", "exit", "close"
}

HELP_TEXT = {
    "add": "Створити новий контакт (ім’я має бути унікальним).",
    "add-address": "Додати/оновити адресу контакту.",
    "email": "Додати/оновити email.",
    "add-birthday": "Додати/оновити день народження.",
    "edit-phone": "Змінити номер телефону (перевірка унікальності).",
    "remove-phone": "Видалити номер телефону.",
    "delete": "Видалити контакт.",
    "show": "Показати всі контакти.",
    "show-contact": "Показати один контакт.",
    "find": "Пошук контактів.",
    "birthdays": "Дні народження у найближчі N днів.",
    "add-note": "Додати нотатку.",
    "edit-note": "Редагувати текст нотатки.",
    "delete-note": "Видалити нотатку.",
    "add-tag": "Додати тег до нотатки.",
    "remove-tag": "Видалити тег з нотатки.",
    "find-note": "Пошук нотаток за текстом/тегами.",
    "show-notes": "Показати всі нотатки.",
    "show-notes-by-tag": "Показати нотатки певного тегу.",
    "help": "Показати список команд.",
    "exit/close": "Зберегти та вийти."
}


def print_help() -> None:
    print("\nКоманди:")
    for k in sorted(HELP_TEXT.keys()):
        print(f"  {k:<20} — {HELP_TEXT[k]}")
    print()


def suggest_command(command: str) -> str | None:
    close = difflib.get_close_matches(command, COMMANDS, n=1, cutoff=0.6)
    return close[0] if close else None


def show_save_paths() -> None:
    print("\nДані збережено:")
    print(f" • Адресна книга: {ABOOK_FILE}")
    print(f" • Нотатки:       {NOTES_FILE}\n")


def main() -> None:
    book = load_addressbook()
    notes = load_notes()
    action_count = 0

    print("👋 Персональний помічник. Введіть 'help' для списку команд.")

    while True:
        try:
            command = input(">>> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nЗавершення...")
            break

        if not command:
            continue

        if command in {"exit", "close"}:
            break

        if command == "help":
            print_help()
            continue

        if command not in COMMANDS:
            suggestion = suggest_command(command)
            if suggestion:
                print(f"❓ Невідома команда. Можливо, ви мали на увазі: '{suggestion}'")
            else:
                print("❗ Невідома команда. Введіть 'help'.")
            continue

        changed = handle_command(command, book, notes)
        if changed:
            action_count += 1
            if action_count >= SAVE_EVERY:
                save_addressbook(book)
                save_notes(notes)
                show_save_paths()
                action_count = 0

    save_addressbook(book)
    save_notes(notes)
    show_save_paths()
    print("До зустрічі 👋")


if __name__ == "__main__":
    main()
