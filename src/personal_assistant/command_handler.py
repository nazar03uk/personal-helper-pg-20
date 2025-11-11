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
        
            # Перевірка дубля імені
            if book.has_contact(name):
                print("❗ Контакт з таким ім’ям уже існує.")
                return False
        
            # Ввід телефону з повторенням
            while True:
                phone = input("Телефон* (або 'exit' щоб скасувати): ").strip()
                if phone.lower() == "exit":
                    print("❗ Додавання скасовано.")
                    return False
        
                try:
                    # Перевірка дубля номера у всій книзі
                    existing = book.find_by_phone(phone)
                    if existing:
                        print(f"❗ Номер {phone} уже прив'язаний до контакту '{existing.name.value}'.")
                        continue
                    
                    phone_obj = Phone(phone)  # <-- тут відбувається валідація
                    break
                
                except Exception as e:
                    print(f"⚠️ Помилка: {e}. Введіть номер ще раз.")
        
            rec = Record(Name(name))
            rec.add_phone(phone_obj)
            book.add_record(rec)
            print("✅ Контакт створено.")
            return True


        if cmd == "add-address":
            name = input("Ім'я: ").strip()
            addr = input("Адреса: ").strip()
            rec = book.get(name)
            if not rec:
                print("❗ Контакт не знайдено.")
                return False
            rec.set_address(Address(addr))
            print("✅ Адресу збережено.")
            return True

        if cmd == "email":
            name = input("Ім'я: ").strip()
            em = input("Email: ").strip()
            rec = book.get(name)
            if not rec:
                print("❗ Контакт не знайдено.")
                return False
            rec.set_email(Email(em))
            print("✅ Email збережено.")
            return True

        if cmd == "add-birthday":
            name = input("Ім'я: ").strip()
            bd = input("Дата (ДД.ММ.РРРР): ").strip()
            rec = book.get(name)
            if not rec:
                print("❗ Контакт не знайдено.")
                return False
            rec.set_birthday(Birthday(bd))
            print("✅ День народження збережено.")
            return True

        if cmd == "edit-phone":
            name = input("Ім'я: ").strip()
            old = input("Старий телефон: ").strip()
            new = input("Новий телефон: ").strip()
            rec = book.get(name)
            if not rec:
                print("❗ Контакт не знайдено.")
                return False

            # Забороняємо дублювати телефон у будь-якого контакту при заміні
            exists = book.find_by_phone(new)
            if exists and exists is not rec:
                print(f"❗ Номер {new} уже використовується контактом '{exists.name.value}'.")
                return False

            rec.edit_phone(old, new)
            print("✅ Телефон змінено.")
            return True

        if cmd == "remove-phone":
            name = input("Ім'я: ").strip()
            ph = input("Телефон: ").strip()
            rec = book.get(name)
            if not rec:
                print("❗ Контакт не знайдено.")
                return False
            rec.remove_phone(ph)
            print("🗑️ Телефон видалено.")
            return True

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
            idx = notes.add_note(Note(text, tag_list))  # type: ignore[name-defined]
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
            tag = input("Тег: ")
            notes.add_tag(idx, tag)
            print("🏷️ Тег додано.")
            return True

        if cmd == "remove-tag":
            try:
                idx = int(input("ID: "))
            except ValueError:
                print("❗ ID має бути числом.")
                return False
            tag = input("Тег: ")
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
