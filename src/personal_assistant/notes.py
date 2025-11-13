from collections import UserDict


class Note:
    """Одна нотатка: текст + унікальні теги (збереження порядку)."""
    
    def __init__(self, text: str, tags: list[str] | None = None):
        # Використання dict.fromkeys() прибирає дублікати, але зберігає порядок
        self.text = text.strip()
        self.tags = list(dict.fromkeys((tags or [])))

    # --- Робота з тегами ---
    def add_tag(self, tag: str) -> None:
        """Додає тег, якщо його ще немає."""
        tag = tag.strip()
        if tag and tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag: str) -> None:
        """Видаляє тег, якщо він існує."""
        self.tags = [t for t in self.tags if t != tag]

    # --- Текст ---
    def edit_text(self, new_text: str) -> None:
        """Редагує текст нотатки."""
        self.text = new_text.strip()

    # --- Подання ---
    def __str__(self) -> str:
        """Форматований вивід нотатки."""
        tag_str = f" | 🏷️ {', '.join(self.tags)}" if self.tags else ""
        return f"{self.text}{tag_str}"


class NotesBook(UserDict):
    """Колекція нотаток. Ключ — автоінкрементний int."""

    # --- CRUD ---
    def _require(self, index: int) -> Note:
        """Повертає нотатку або викликає помилку (для уникнення дублювання коду)."""
        index = int(index)
        note = self.data.get(index)
        if not note:
            raise KeyError("Нотатку не знайдено.")
        return note

    def add_note(self, note: Note) -> int:
        """Додає нову нотатку, повертає її ID."""
        new_id = max(self.data, default=0) + 1
        self.data[new_id] = note
        return new_id

    def delete_note(self, index: int) -> None:
        self._require(index)
        del self.data[int(index)]

    def edit_note(self, index: int, new_text: str) -> None:
        self._require(index).edit_text(new_text)

    def add_tag(self, index: int, tag: str) -> None:
        self._require(index).add_tag(tag)

    def remove_tag(self, index: int, tag: str) -> None:
        self._require(index).remove_tag(tag)

    # --- Пошук ---
    def search(self, query: str) -> list[tuple[int, Note]]:
        """Пошук за текстом або тегами."""
        q = query.lower()
        return [
            (i, n)
            for i, n in self.data.items()
            if q in n.text.lower() or any(q in t.lower() for t in n.tags)
        ]

    def filter_by_tag(self, tag: str) -> list[tuple[int, Note]]:
        """Фільтрація нотаток за тегом."""
        return [(i, n) for i, n in self.data.items() if tag in n.tags]

    # --- Подання ---
    def __str__(self) -> str:
        if not self.data:
            return "Немає нотаток."
        return "\n".join(f"{i}. {n}" for i, n in sorted(self.data.items()))
