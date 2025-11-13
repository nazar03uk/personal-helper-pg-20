from personal_assistant.addressbook import Name, Address, Phone, Email, Birthday, Record
from personal_assistant.notes import Note


def handle_command(cmd: str, book, notes) -> bool:
    """
    Повертає True, якщо дані змінювалися (для автозбереження), інакше False.
    """
    try:
        # ===== КОНТАКТИ =====

        if cmd == "add":
            name = input("Ім'я*: ").strip()
            if not name:
                print("❗ Ім'я обов'язкове.")
                return False

            if book.has_contact(name):
                print("❗ Контакт з таким ім’ям уже існує.")
                return False

            while True:
                phone = input(
                    "Введіть номер телефону в форматі +380XXXXXXXXX:\n"
                    "або 'exit' щоб скасувати...\n"
                ).strip()

                if phone.lower() == "exit":
                    print("❗ Додавання скасовано.")
                    return False

                try:
                    existing = book.find_by_phone(phone)
                    if existing:
                        print(f"❗ Номер {phone} уже прив'язаний до контакту '{existing.name.value}'.")
                        continue

                    phone_obj = Phone(phone)
                    break

                except Exception as e:
                    print(f"⚠️ Помилка: {e}. Введіть номер ще раз.")

            rec = Record(Name(name))
            rec.add_phone(phone_obj)    # один контакт = один номер
            book.add_record(rec)

            print("✅ Контакт створено.")
            return True

        if cmd == "add-address":
            name = input("Ім'я: ").strip()
            rec = book.get(name)
            if not rec:
                print("❗ Контакт не знайдено.")
                return False

            addr = input("Адреса: ").strip()
            rec.set_address(Address(addr))
            print("✅ Адресу збережено.")
            return True

        if cmd == "email":
            name = input("Ім'я: ").strip()
            rec = book.get(name)
            if not rec:
                print("❗ Контакт не знайдено.")
                return False

            em = input("Email: ").strip()
            rec.set_email(Email(em))
            print("✅ Email збережено.")
            return True

        if cmd == "add-birthday":
            name = input("Ім'я: ").strip()
            rec = book.get(name)
            if not rec:
                print("❗ Контакт не знайдено.")
                return False

            bd = input("Дата (ДД.ММ.РРРР): ").strip()
            rec.set_birthday(Birthday(bd))
            print("✅ День народження збережено.")
            return True

        # ===== Виправлена логіка редагування телефону =====
        if cmd == "edit-phone":
            name = input("Ім'я: ").strip()
            rec = book.get(name)
        
            if not rec:
                print("❗ Контакт не знайдено.")
                return False
        
            if not rec.phones:
                print("❗ У контакту немає телефону.")
                return False
        
            # одразу новий номер
            new = input("Новий телефон: ").strip()
        
            # перевірка формату (regex або метод validate всередині Phone)
            try:
                exists = book.find_by_phone(new)
                if exists and exists is not rec:
                    print(f"❗ Номер {new} уже використовується контактом '{exists.name.value}'.")
                    return False
        
                # заміна першого номера
                old_phone = rec.phones[0].value
                rec.edit_phone(old_phone, new)
        
                print("✅ Телефон змінено.")
                return True
        
            except ValueError as e:
                print(f"⚠️ Помилка: {e}")
                return False


        if cmd == "delete":
            name = input("Ім'я: ").strip()
            try:
                book.delete_record(name)
                print("🗑️ Контакт видалено.")
                return True
            except KeyError:
                print("❗ Контакт не знайдено.")
                return False

        if cmd == "show":
            print(book)
            return False

        if cmd == "show-contact":
            name = input("Ім'я: ").strip()
            print(book.get(name) or "Контакт не знайдено.")
            return False

        if cmd == "find":
            q = input("Пошук: ").strip()
            res = book.search(q)
            print(*res, sep="\n") if res else print("Нічого не знайдено.")
            return False

        if cmd == "birthdays":
            try:
                days = int(input("Кількість днів: "))
            except ValueError:
                print("❗ Введіть число.")
                return False

            res = book.birthdays_within(days)
            for rec, d in res:
                print(f"{rec.name.value}: через {d} дн.")
            if not res:
                print("Немає.")
            return False

        # ===== НОТАТКИ =====

        if cmd == "add-note":
            text = input("Текст: ").strip()
            tags = input("Теги через кому: ").strip()
            tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []

            idx = notes.add_note(Note(text, tag_list))
            print(f"✅ Нотатку #{idx} збережено.")
            return True

        if cmd == "edit-note":
            try:
                idx = int(input("ID: "))
            except ValueError:
                print("❗ ID має бути числом.")
                return False

            new = input("Новий текст: ")
            notes.edit_note(idx, new)
            print("✏️ Змінено.")
            return True

        if cmd == "delete-note":
            try:
                idx = int(input("ID: "))
            except ValueError:
                print("❗ ID має бути числом.")
                return False

            notes.delete_note(idx)
            print("🗑️ Нотатку видалено.")
            return True

        if cmd == "add-tag":
            try:
                idx = int(input("ID: "))
            except ValueError:
                print("❗ ID має бути числом.")
                return False

            tag = input("Тег: ").strip()
            note = notes.get(idx)

            if not note:
                print("❗ Нотатку не знайдено.")
                return False

            if tag in note.tags:
                print(f"❗ Тег '{tag}' уже існує у цій нотатці.")
                return False

            notes.add_tag(idx, tag)
            print("🏷️ Тег додано.")
            return True

        if cmd == "remove-tag":
            try:
                idx = int(input("ID: "))
            except ValueError:
                print("❗ ID має бути числом.")
                return False

            tag = input("Тег: ").strip()
            note = notes.get(idx)

            if not note:
                print("❗ Нотатку не знайдено.")
                return False

            if tag not in note.tags:
                print(f"❗ Тег '{tag}' не існує у цій нотатці.")
                return False

            notes.remove_tag(idx, tag)
            print("🏷️ Тег видалено.")
            return True

        if cmd == "find-note":
            q = input("Пошук: ").strip()
            res = notes.search(q)
            print(*[f"{i}. {n}" for i, n in res], sep="\n") if res else print("Немає.")
            return False

        if cmd == "show-notes":
            print(notes)
            return False

        if cmd == "show-notes-by-tag":
            tag = input("Тег: ").strip()
            res = notes.filter_by_tag(tag)
            print(*[f"{i}. {n}" for i, n in res], sep="\n") if res else print("Немає.")
            return False

    except Exception as e:
        print("⚠️ Помилка:", e)

    return False
