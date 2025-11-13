import pickle
from pathlib import Path
from personal_assistant.addressbook import AddressBook
from personal_assistant.notes import NotesBook


# --- Шлях до папки застосунку ---
APP_DIR = Path.home() / ".personal_assistant"
APP_DIR.mkdir(parents=True, exist_ok=True)

ABOOK_FILE = APP_DIR / "addressbook.pkl"
NOTES_FILE = APP_DIR / "notes.pkl"


# --- Міграція старих pickle-файлів ---
class FixImportUnpickler(pickle.Unpickler):
    """Дозволяє завантажити pickle, створений зі старими назвами модулів."""
    MAP = {
        "addressbook": "personal_assistant.addressbook",
        "notes": "personal_assistant.notes",
    }

    def find_class(self, module, name):
        module = self.MAP.get(module, module)
        return super().find_class(module, name)


def pickle_load_fixed(path: Path):
    """Безпечне завантаження pickle із підтримкою старих шляхів."""
    with path.open("rb") as f:
        return FixImportUnpickler(f).load()


# --- Універсальні функції збереження/завантаження ---
def save_data(obj, path: Path) -> None:
    """Загальний метод для збереження будь-якого об’єкта."""
    with path.open("wb") as f:
        pickle.dump(obj, f)


def load_data(path: Path, default_factory):
    """Загальний метод для безпечного завантаження."""
    if path.exists():
        try:
            return pickle_load_fixed(path)
        except Exception:
            pass
    return default_factory()


# --- Спеціалізовані обгортки ---
def save_addressbook(book: AddressBook) -> None:
    save_data(book, ABOOK_FILE)


def load_addressbook() -> AddressBook:
    return load_data(ABOOK_FILE, AddressBook)


def save_notes(notes: NotesBook) -> None:
    save_data(notes, NOTES_FILE)


def load_notes() -> NotesBook:
    return load_data(NOTES_FILE, NotesBook)
