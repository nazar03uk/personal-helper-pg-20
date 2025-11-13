from personal_assistant.addressbook import Phone


def ask_str(prompt: str, allow_empty: bool = False) -> str | None:
    """Запитує рядок. Підтримує 'exit' та обов’язковість введення."""
    while True:
        value = input(f"{prompt} ").strip()
        if value.lower() == "exit":
            return None
        if not value and not allow_empty:
            print("❗ Значення не може бути порожнім. Спробуйте ще раз.")
            continue
        return value


def ask_int(prompt: str) -> int | None:
    """Запитує ціле число. Повертає None при 'exit'."""
    while True:
        value = input(f"{prompt} ").strip()
        if value.lower() == "exit":
            return None
        if not value.isdigit():
            print("❗ Має бути число. Спробуйте ще раз.")
            continue
        return int(value)


# --- Універсальний хелпер для повторного запиту з конструктором ---
def ask_field(prompt: str, constructor, allow_empty: bool = False):
    """Універсальний запит поля (наприклад Email, Birthday, Phone).Повторює введення, поки не буде валідне значення."""
    while True:
        value = ask_str(prompt, allow_empty=allow_empty)
        if value is None:
            return None
        try:
            return constructor(value)
        except Exception as e:
            print(f"⚠️ {e}")


def ask_existing_contact(book):
    """Запитує ім’я контакту, який має існувати."""
    while True:
        name = ask_str("Ім'я (або 'exit'):")
        if name is None:
            return None
        rec = book.get(name)
        if rec:
            return rec
        print("❗ Контакт не знайдено. Спробуйте ще раз.")


def ask_phone(book, allow_existing: bool = False):
    """Запитує телефон у форматі +380XXXXXXXXX (валідація через клас Phone)."""
    while True:
        phone = ask_str("Телефон у форматі +380XXXXXXXXX (або 'exit'):")
        if phone is None:
            return None
        try:
            exists = book.find_by_phone(phone)
            if exists and not allow_existing:
                print(f"❗ Номер уже пов'язаний з контактом '{exists.name.value}'.")
                continue
            return Phone(phone)
        except Exception as e:
            print(f"⚠️ {e}. Спробуйте ще раз.")


def ask_existing_note(notes):
    """Запитує ID існуючої нотатки."""
    while True:
        idx = ask_int("ID нотатки (або 'exit'):")
        if idx is None:
            return None
        note = notes.get(idx)
        if note:
            return idx, note
        print("❗ Нотатку не знайдено. Спробуйте ще раз.")


def ask_tag(note, existing_required: bool = False):
    """Запитує тег:['якщо existing_required=True — тег має існувати','якщо False — не повинен повторюватися.']"""
    while True:
        tag = ask_str("Тег (або 'exit'):")
        if tag is None:
            return None

        if existing_required and tag not in note.tags:
            print("❗ Тег не існує. Спробуйте ще раз.")
            continue

        if not existing_required and tag in note.tags:
            print("❗ Такий тег уже є. Спробуйте інший.")
            continue

        return tag
