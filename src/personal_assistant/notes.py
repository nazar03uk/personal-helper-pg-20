from collections import UserDict


class Note:
    """
    Одна нотатка: текст + унікальні теги (збереження порядку).
    """
    def __init__(self, text: str, tags: list[str] | None = None):
        self.text = text
        self.tags = list(dict.fromkeys(tags or []))

    def add_tag(self, tag: str) -> None:
        tag = tag.strip()
        if tag and tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag: str) -> None:
        self.tags = [t for t in self.tags if t != tag]

    def edit_text(self, new_text: str) -> None:
        self.text = new_text

    def __str__(self) -> str:
        t = f" | Теги: {', '.join(self.tags)}" if self.tags else ""
        return f"{self.text}{t}"


class NotesBook(UserDict):
    """
    Колекція нотаток. Ключ — автоінкрементний int.
    """
    def add_note(self, note: Note) -> int:
        new_id = (max(self.data) + 1) if self.data else 1
        self.data[new_id] = note
        return new_id

    def delete_note(self, index: int) -> None:
        index = int(index)
        if index in self.data:
            del self.data[index]
        else:
            raise KeyError("Нотатку не знайдено.")

    def edit_note(self, index: int, new_text: str) -> None:
        index = int(index)
        if index in self.data:
            self.data[index].edit_text(new_text)
        else:
            raise KeyError("Нотатку не знайдено.")

    def add_tag(self, index: int, tag: str) -> None:
        index = int(index)
        if index in self.data:
            self.data[index].add_tag(tag)
        else:
            raise KeyError("Нотатку не знайдено.")

    def remove_tag(self, index: int, tag: str) -> None:
        index = int(index)
        if index in self.data:
            self.data[index].remove_tag(tag)
        else:
            raise KeyError("Нотатку не знайдено.")

    def search(self, query: str) -> list[tuple[int, Note]]:
        q = query.lower()
        return [(i, n) for i, n in self.data.items() if q in n.text.lower() or any(q in t.lower() for t in n.tags)]

    def filter_by_tag(self, tag: str) -> list[tuple[int, Note]]:
        return [(i, n) for i, n in self.data.items() if tag in n.tags]

    def __str__(self) -> str:
        if not self.data:
            return "Немає нотаток."
        return "\n".join(f"{i}. {n}" for i, n in sorted(self.data.items()))
