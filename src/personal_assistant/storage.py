import pickle
from pathlib import Path

from personal_assistant.addressbook import AddressBook
from personal_assistant.notes import NotesBook

# Зберігаємо у домашній папці користувача
APP_DIR = Path.home() / ".personal_assistant"
APP_DIR.mkdir(parents=True, exist_ok=True)

ABOOK_FILE = APP_DIR / "addressbook.pkl"
NOTES_FILE = APP_DIR / "notes.pkl"


# --- Міграція старих шляхів pickle ---
class FixImportUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        # Якщо pickle посилається на стару структуру:
        if module == "addressbook":
            module = "personal_assistant.addressbook"
        if module == "notes":
            module = "personal_assistant.notes"
        return super().find_class(module, name)


def pickle_load_fixed(file):
    with file.open("rb") as f:
        return FixImportUnpickler(f).load()


# --- Адресна книга ---
def save_addressbook(book: AddressBook) -> None:
    with ABOOK_FILE.open("wb") as f:
        pickle.dump(book, f)


def load_addressbook() -> AddressBook:
    if ABOOK_FILE.exists():
        try:
            return pickle_load_fixed(ABOOK_FILE)
        except Exception:
            pass
    return AddressBook()


# --- Нотатки ---
def save_notes(notes: NotesBook) -> None:
    with NOTES_FILE.open("wb") as f:
        pickle.dump(notes, f)


def load_notes() -> NotesBook:
    if NOTES_FILE.exists():
        try:
            return pickle_load_fixed(NOTES_FILE)
        except Exception:
            pass
    return NotesBook()
