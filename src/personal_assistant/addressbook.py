from collections import UserDict
from datetime import datetime, date
import re


# ----- Базові поля -----

class Field:
    def __init__(self, value: str):
        self.value = value

    def __str__(self) -> str:
        return str(self.value)


class Name(Field):
    """Ім’я контакту (унікальне в межах книги)."""
    pass


class Address(Field):
    """Поштова адреса."""
    pass


class Phone(Field):
    """Телефон: лише цифри, довжина 7–15."""
    def __init__(self, value: str):
        if not value.isdigit():
            raise ValueError("Телефон повинен містити лише цифри.")
        if not (7 <= len(value) <= 15):
            raise ValueError("Довжина телефону має бути від 7 до 15 цифр.")
        super().__init__(value)


class Email(Field):
    """Email regex-валідація."""
    EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

    def __init__(self, value: str):
        if not self.EMAIL_RE.match(value):
            raise ValueError("Некоректний email.")
        super().__init__(value)


class Birthday(Field):
    """Дата народження у форматі ДД.ММ.РРРР."""
    FORMAT = "%d.%m.%Y"

    def __init__(self, value: str):
        try:
            datetime.strptime(value, self.FORMAT)
        except ValueError:
            raise ValueError("Дата повинна бути у форматі ДД.ММ.РРРР.")
        super().__init__(value)

    @property
    def as_date(self) -> date:
        return datetime.strptime(self.value, self.FORMAT).date()


# ----- Запис і книга -----

class Record:
    """
    Контакт: ім’я, адреса (опц.), список телефонів, email (опц.), ДН (опц.).
    """
    def __init__(self, name: Name):
        self.name: Name = name
        self.address: Address | None = None
        self.phones: list[Phone] = []
        self.email: Email | None = None
        self.birthday: Birthday | None = None

    # --- телефони ---
    def add_phone(self, phone: Phone) -> None:
        if any(p.value == phone.value for p in self.phones):
            raise ValueError("Такий номер уже додано до цього контакту.")
        self.phones.append(phone)

    def remove_phone(self, phone_value: str) -> None:
        self.phones = [p for p in self.phones if p.value != phone_value]

    def edit_phone(self, old_value: str, new_value: str) -> None:
        for i, p in enumerate(self.phones):
            if p.value == old_value:
                self.phones[i] = Phone(new_value)
                return
        raise ValueError("Вказаний телефон не знайдено у контакті.")

    # --- інші поля ---
    def set_email(self, email: Email) -> None:
        self.email = email

    def set_address(self, address: Address) -> None:
        self.address = address

    def set_birthday(self, birthday: Birthday) -> None:
        self.birthday = birthday

    # --- подання ---
    def __str__(self) -> str:
        phone_str = ", ".join(p.value for p in self.phones) if self.phones else "—"
        email_str = self.email.value if self.email else "—"
        addr_str = self.address.value if self.address else "—"
        bd_str = self.birthday.value if self.birthday else "—"
        # Іконки як у ваших прикладах
        return f"{self.name.value}: 📞 {phone_str} | ✉️ {email_str} | 🏠 {addr_str} | 🎂 {bd_str}"


class AddressBook(UserDict):
    """
    Колекція контактів. Ключ — унікальне ім’я.
    Додатково: пошук, найближчі ДН, перевірка унікальності телефону.
    """

    # --- сервісні перевірки ---
    def has_contact(self, name: str) -> bool:
        return name in self.data

    def find_by_phone(self, phone_value: str) -> Record | None:
        for rec in self.data.values():
            if any(p.value == phone_value for p in rec.phones):
                return rec
        return None

    # --- CRUD ---
    def add_record(self, record: Record) -> None:
        # Забороняємо дублікати імен
        if record.name.value in self.data:
            raise KeyError("Контакт з таким ім’ям уже існує.")
        # Забороняємо дублікати телефонів по всій книзі
        for p in record.phones:
            found = self.find_by_phone(p.value)
            if found is not None:
                raise ValueError(
                    f"Номер {p.value} вже використовується контактом '{found.name.value}'."
                )
        self.data[record.name.value] = record

    def delete_record(self, name: str) -> None:
        if name in self.data:
            del self.data[name]
        else:
            raise KeyError("Контакт не знайдено.")

    # --- пошук ---
    def search(self, query: str) -> list[Record]:
        q = query.strip().lower()
        results: list[Record] = []
        for rec in self.data.values():
            if q in rec.name.value.lower():
                results.append(rec)
                continue
            if rec.address and q in rec.address.value.lower():
                results.append(rec)
                continue
            if rec.email and q in rec.email.value.lower():
                results.append(rec)
                continue
            if any(q in p.value for p in rec.phones):
                results.append(rec)
        return results

    # --- ДН у межах N днів ---
    def birthdays_within(self, days: int) -> list[tuple[Record, int]]:
        today = date.today()
        res: list[tuple[Record, int]] = []
        for rec in self.data.values():
            if not rec.birthday:
                continue
            bd = rec.birthday.as_date
            next_bd = bd.replace(year=today.year)
            if next_bd < today:
                next_bd = next_bd.replace(year=today.year + 1)
            left = (next_bd - today).days
            if 0 <= left <= days:
                res.append((rec, left))
        res.sort(key=lambda x: x[1])
        return res

    # --- подання ---
    def __str__(self) -> str:
        if not self.data:
            return "Адресна книга порожня."
        # Для стабільного виводу відсортуємо за ім’ям
        lines = [str(self.data[k]) for k in sorted(self.data.keys(), key=str.lower)]
        return "\n".join(lines)
