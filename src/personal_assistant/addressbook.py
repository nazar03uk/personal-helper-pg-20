from collections import UserDict
from datetime import datetime, date
import re

# ----- Базові поля -----

class Field:
    """Базове поле, яке зберігає текстове значення."""
    def __init__(self, value: str):
        self.value = value.strip()

    def __str__(self) -> str:
        return self.value


class Name(Field):
    """Ім’я контакту (унікальне в межах книги)."""
    pass


class Address(Field):
    """Поштова адреса."""
    pass


class Phone(Field):
    """Телефон у міжнародному форматі: +380XXXXXXXXX"""
    PHONE_RE = re.compile(r"^\+[0-9]{10,15}$")

    def __init__(self, value: str):
        value = value.strip()
        if not self.PHONE_RE.match(value):
            raise ValueError("Некоректний номер телефону. Приклад: +380676789012")
        super().__init__(value)


class Email(Field):
    """Email з валідацією за RFC 5322."""
    EMAIL_RE = re.compile(
        r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
        r"[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$"
    )

    def __init__(self, value: str):
        value = value.strip()
        if not self.EMAIL_RE.match(value):
            raise ValueError("Некоректний email. Приклад: example@gmail.com")
        super().__init__(value)


class Birthday(Field):
    """Дата народження у форматі ДД.ММ.РРРР."""
    FORMAT = "%d.%m.%Y"

    def __init__(self, value: str):
        value = value.strip()
        try:
            datetime.strptime(value, self.FORMAT)
        except ValueError:
            raise ValueError("Дата повинна бути у форматі ДД.ММ.РРРР.")
        super().__init__(value)

    @property
    def as_date(self) -> date:
        """Повертає дату як об’єкт date."""
        return datetime.strptime(self.value, self.FORMAT).date()


# ----- Запис і книга -----

class Record:
    """Контакт: ім’я, телефони, email, адреса, день народження."""
    def __init__(self, name: Name):
        self.name = name
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
        """Редагує існуючий номер телефону."""
        for i, p in enumerate(self.phones):
            if p.value == old_value:
                self.phones[i] = Phone(new_value)
                return
        raise ValueError("Телефон не знайдено у контакті.")

    # --- інші поля ---
    def set_email(self, email: Email) -> None:
        self.email = email

    def set_address(self, address: Address) -> None:
        self.address = address

    def set_birthday(self, birthday: Birthday) -> None:
        self.birthday = birthday

    # --- подання ---
    def __str__(self) -> str:
        """Форматований вивід контакту з усіма даними."""
        safe = lambda v: v.value if v else "—"
        phones = ", ".join(p.value for p in self.phones) or "—"
        return (
            f"{self.name.value}: "
            f"📞 {phones} | ✉️ {safe(self.email)} | 🏠 {safe(self.address)} | 🎂 {safe(self.birthday)}"
        )


class AddressBook(UserDict):
    """Колекція контактів із пошуком і перевірками унікальності."""
    
    # --- перевірки ---
    def has_contact(self, name: str) -> bool:
        return name in self.data

    def find_by_phone(self, phone_value: str) -> Record | None:
        """Шукає контакт за номером телефону."""
        return next(
            (rec for rec in self.data.values() if any(p.value == phone_value for p in rec.phones)),
            None
        )

    # --- CRUD ---
    def add_record(self, record: Record) -> None:
        """Додає контакт із перевіркою унікальності імені та телефонів."""
        if record.name.value in self.data:
            raise KeyError("Контакт з таким ім’ям уже існує.")
        for p in record.phones:
            found = self.find_by_phone(p.value)
            if found:
                raise ValueError(f"Номер {p.value} вже використовується контактом '{found.name.value}'.")
        self.data[record.name.value] = record

    def delete_record(self, name: str) -> None:
        """Видаляє контакт за іменем."""
        if name not in self.data:
            raise KeyError("Контакт не знайдено.")
        del self.data[name]

    # --- пошук ---
    def search(self, query: str) -> list[Record]:
        """Пошук у будь-якому полі (ім’я, адреса, email, телефони)."""
        q = query.strip().lower()
        def match(rec: Record):
            fields = [
                rec.name.value,
                rec.address.value if rec.address else "",
                rec.email.value if rec.email else "",
                *[p.value for p in rec.phones]
            ]
            return any(q in f.lower() for f in fields)
        return [r for r in self.data.values() if match(r)]

    # --- ДН у межах N днів ---
    def birthdays_within(self, days: int) -> list[tuple[Record, int]]:
        """Повертає список контактів, у яких день народження через ≤ N днів."""
        today = date.today()
        result = []
        for rec in self.data.values():
            if not rec.birthday:
                continue
            bd = rec.birthday.as_date.replace(year=today.year)
            if bd < today:
                bd = bd.replace(year=today.year + 1)
            diff = (bd - today).days
            if 0 <= diff <= days:
                result.append((rec, diff))
        return sorted(result, key=lambda x: x[1])

    # --- подання ---
    def __str__(self) -> str:
        if not self.data:
            return "Адресна книга порожня."
        return "\n".join(str(self.data[k]) for k in sorted(self.data, key=str.lower))
