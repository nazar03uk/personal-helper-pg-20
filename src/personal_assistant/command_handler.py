from personal_assistant.addressbook import Name, Address, Email, Birthday, Record
from personal_assistant.notes import Note
from personal_assistant.validator import (
    ask_str, ask_int, ask_existing_contact,
    ask_phone, ask_existing_note, ask_tag, ask_field
)


# --- Обробники контактів ---
def handle_add_contact(book):
    """Додавання нового контакту."""
    name = ask_str("Ім'я* (або 'exit'):")
    if not name or book.has_contact(name):
        print("❗ Контакт з таким ім’ям уже існує." if name else "")
        return False

    phone_obj = ask_phone(book)
    if phone_obj is None:
        return False

    rec = Record(Name(name))
    rec.add_phone(phone_obj)
    book.add_record(rec)
    print("✅ Контакт створено.")
    return True


def handle_add_field(rec, field_type, prompt, setter_name):
    """Універсальний додаток поля (адреса, email, день народження)."""
    value = ask_field(prompt, field_type, allow_empty=isinstance(field_type, Address))
    if value is None:
        return False
    getattr(rec, setter_name)(value)
    print(f"✅ {field_type.__name__} збережено.")
    return True


def handle_edit_phone(book):
    rec = ask_existing_contact(book)
    if not rec:
        return False
    if not rec.phones:
        print("❗ У контакту немає телефонів.")
        return False

    while True:
        new_value = ask_str("Новий телефон (або 'exit'):")
        if new_value is None:
            return False
        try:
            exists = book.find_by_phone(new_value)
            if exists and exists is not rec:
                print(f"❗ Номер уже використовується '{exists.name.value}'.")
                continue
            old = rec.phones[0].value
            rec.edit_phone(old, new_value)
            break
        except Exception as e:
            print(f"⚠️ {e}")

    print("✅ Телефон змінено.")
    return True


def handle_delete_contact(book):
    rec = ask_existing_contact(book)
    if not rec:
        return False
    book.delete_record(rec.name.value)
    print("🗑️ Контакт видалено.")
    return True


def handle_search(book):
    q = ask_str("Пошук:")
    res = book.search(q)
    print(*res, sep="\n") if res else print("Нічого не знайдено.")
    return False


def handle_birthdays(book):
    days = ask_int("Кількість днів (або 'exit'):")
    if days is None:
        return False
    res = book.birthdays_within(days)
    if res:
        for rec, d in res:
            print(f"{rec.name.value}: через {d} дн.")
    else:
        print("Немає.")
    return False


# --- Обробники нотаток ---
def handle_add_note(notes):
    text = ask_str("Текст:")
    tags = ask_str("Теги через кому (або пусто):", allow_empty=True)
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
    idx = notes.add_note(Note(text, tag_list))
    print(f"✅ Нотатку #{idx} збережено.")
    return True


def handle_edit_note(notes):
    idx, _ = ask_existing_note(notes)
    if idx is None:
        return False
    new_text = ask_str("Новий текст:")
    notes.edit_note(idx, new_text)
    print("✏️ Змінено.")
    return True


def handle_delete_note(notes):
    idx, _ = ask_existing_note(notes)
    if idx is None:
        return False
    notes.delete_note(idx)
    print("🗑️ Нотатку видалено.")
    return True


def handle_tag(notes, add=True):
    idx, note = ask_existing_note(notes)
    if idx is None:
        return False
    tag = ask_tag(note, existing_required=not add)
    if tag is None:
        return False
    (notes.add_tag if add else notes.remove_tag)(idx, tag)
    print(f"🏷️ Тег {'додано' if add else 'видалено'}.")
    return True


def handle_find_notes(notes):
    q = ask_str("Пошук:")
    res = notes.search(q)
    print(*[f"{i}. {n}" for i, n in res], sep="\n") if res else print("Немає.")
    return False


def handle_notes_by_tag(notes):
    while True:
        tag = ask_str("Тег (або 'exit'):")
        if tag is None:
            return False
        res = notes.filter_by_tag(tag)
        if not res:
            print("❗ Немає нотаток з таким тегом. Спробуйте ще раз.")
            continue
        print(*[f"{i}. {n}" for i, n in res], sep="\n")
        return False


# --- Головний маршрутизатор ---
def handle_command(cmd: str, book, notes) -> bool:
    """Повертає True, якщо дані змінювались (для автозбереження)."""
    try:
        contact_cmds = {
            "add": lambda: handle_add_contact(book),
            "add-address": lambda: handle_add_field(ask_existing_contact(book), Address, "Адреса (або 'exit'):", "set_address"),
            "email": lambda: handle_add_field(ask_existing_contact(book), Email, "Email (або 'exit'):", "set_email"),
            "add-birthday": lambda: handle_add_field(ask_existing_contact(book), Birthday, "Дата ДД.ММ.РРРР (або 'exit'):", "set_birthday"),
            "edit-phone": lambda: handle_edit_phone(book),
            "delete": lambda: handle_delete_contact(book),
            "show": lambda: print(book),
            "show-contact": lambda: print(book.get(ask_str("Ім'я:")) or "❗ Контакт не знайдено."),
            "find": lambda: handle_search(book),
            "birthdays": lambda: handle_birthdays(book),
        }

        note_cmds = {
            "add-note": lambda: handle_add_note(notes),
            "edit-note": lambda: handle_edit_note(notes),
            "delete-note": lambda: handle_delete_note(notes),
            "add-tag": lambda: handle_tag(notes, add=True),
            "remove-tag": lambda: handle_tag(notes, add=False),
            "find-note": lambda: handle_find_notes(notes),
            "show-notes": lambda: print(notes),
            "show-notes-by-tag": lambda: handle_notes_by_tag(notes),
        }

        if cmd in contact_cmds:
            result = contact_cmds[cmd]()
        elif cmd in note_cmds:
            result = note_cmds[cmd]()
        else:
            print("❗ Невідома команда.")
            return False

        return bool(result)
    except Exception as e:
        print("⚠️ Помилка:", e)
        return False
