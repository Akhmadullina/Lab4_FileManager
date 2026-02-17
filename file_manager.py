import os
import shutil
import stat
import fnmatch

# Вспомогательные функции
def get_user_choice(prompt="Выберите действие: "):
    # Безопасный ввод выбора пользователя
    return input(prompt).strip()

def get_path(prompt="Введите путь или имя: "):
    # Ввод пути с обработкой пустой строки
    path = input(prompt).strip()
    if not path:
        print("Ошибка: путь не может быть пустым.")
        return None
    return path

def confirm_action(message):
    # Запрос подтверждения
    ans = input(f"{message} (y/n): ").strip().lower()
    return ans == 'y' or ans == 'да' or ans == 'yes'

def format_permissions(mode):
    # Форматирование прав доступа
    is_dir = 'd' if stat.S_ISDIR(mode) else '-'
    perms = [
        (stat.S_IRUSR, 'r'), (stat.S_IWUSR, 'w'), (stat.S_IXUSR, 'x'),
        (stat.S_IRGRP, 'r'), (stat.S_IWGRP, 'w'), (stat.S_IXGRP, 'x'),
        (stat.S_IROTH, 'r'), (stat.S_IWOTH, 'w'), (stat.S_IXOTH, 'x')
    ]
    perm_str = ''.join([p[1] if mode & p[0] else '-' for p in perms])
    return is_dir + perm_str

# Основные функции

def list_directory(path="."):
    # Содержимое текущего каталога
    try:
        items = os.listdir(path)
        print(f"\n Содержимое: {os.path.abspath(path)} ")
        folders = []
        files = []
        for item in items:
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                folders.append(f"[ПАПКА] {item}")
            else:
                size = os.path.getsize(item_path)
                files.append(f"[ФАЙЛ] {item} ({size} байт)")
        # Сначала папки, потом файлы
        for f in sorted(folders):
            print(f)
        for f in sorted(files):
            print(f)
        print(f" Всего объектов: {len(items)} ")
    except PermissionError:
        print("Ошибка: недостаточно прав для просмотра каталога.")
    except FileNotFoundError:
        print("Ошибка: каталог не найден.")

def change_dir():
    # Смена текущего рабочего директория
    new_path = get_path("Введите путь для перехода: ")
    if new_path and os.path.exists(new_path) and os.path.isdir(new_path):
        os.chdir(new_path)
        print(f"Текущая директория изменена на: {os.getcwd()}")
    elif new_path:
        print("Указанный путь не существует или не является папкой.")

def create_folder():
    # Создание новой папки в текущей директории
    name = get_path("Введите имя новой папки: ")
    if name:
        try:
            os.mkdir(name)
            print(f"Папка '{name}' создана.")
        except FileExistsError:
            print("Папка с таким именем уже существует.")
        except Exception as e:
            print(f"Ошибка создания: {e}")

def create_file():
    # Создание пустого текстового файла
    name = get_path("Введите имя нового файла (например, test.txt): ")
    if name:
        try:
            with open(name, 'w', encoding='utf-8') as f:
                pass
            print(f"Файл '{name}' создан.")
        except Exception as e:
            print(f"Ошибка создания файла: {e}")

def view_file():
    # Вывод содержимого текстового файла на экран
    name = get_path("Введите имя файла для просмотра: ")
    if name and os.path.isfile(name):
        try:
            with open(name, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"\n Содержимое {name} ")
                print(content if content else "[Файл пуст]")
                print("- Конец файла -")
        except PermissionError:
            print("Нет прав на чтение файла.")
        except UnicodeDecodeError:
            print("Не удается прочитать файл (возможно, бинарный).")
        except Exception as e:
            print(f"Ошибка: {e}")
    elif name:
        print("Файл не найден или это папка.")

def edit_file():
    # Дописывание текста в конец файла
    name = get_path("Введите имя файла для редактирования: ")
    if name and os.path.isfile(name):
        if confirm_action(f"Дописать текст в конец файла '{name}'?"):
            try:
                text = input("Введите текст для добавления: ")
                with open(name, 'a', encoding='utf-8') as f:
                    f.write(text + '\n')
                print("Текст добавлен.")
            except Exception as e:
                print(f"Ошибка: {e}")
    elif name:
        print("Файл не найден.")

def copy_item():
    # Копирование файла или папки
    src = get_path("Введите имя источника (что копируем): ")
    if not src: return
    dst = get_path("Введите имя назначения (куда копируем): ")
    if not dst: return

    if not os.path.exists(src):
        print("Источник не найден.")
        return

    if os.path.exists(dst):
        if not confirm_action(f"'{dst}' уже существует. Перезаписать?"):
            print("Копирование отменено.")
            return

    try:
        if os.path.isdir(src):
            # Копируем папку (shutil.copytree требует, чтобы dst не существовала). Если мы уже проверили и подтвердили перезапись, нужно сначала удалить dst
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print(f"Папка '{src}' скопирована в '{dst}'.")
        else:
            shutil.copy2(src, dst) # copy2 пытается сохранить метаданные
            print(f"Файл '{src}' скопирован в '{dst}'.")
    except Exception as e:
        print(f"Ошибка при копировании: {e}")

def move_rename():
    # Перемещениие или переименовывание файла/папки
    src = get_path("Введите текущее имя/путь: ")
    if not src: return
    dst = get_path("Введите новое имя/путь: ")
    if not dst: return

    if not os.path.exists(src):
        print("Исходный объект не найден.")
        return

    if os.path.exists(dst):
        if not confirm_action(f"'{dst}' уже существует. Перезаписать?"):
            print("Операция отменена.")
            return

    try:
        shutil.move(src, dst)
        print(f"Объект перемещен/переименован в '{dst}'.")
    except Exception as e:
        print(f"Ошибка: {e}")

def delete_item():
    # Удаляет файл или папку
    name = get_path("Введите имя файла/папки для удаления: ")
    if name and os.path.exists(name):
        if confirm_action(f"Вы уверены, что хотите удалить '{name}'?"):
            try:
                if os.path.isdir(name):
                    shutil.rmtree(name)
                else:
                    os.remove(name)
                print(f"'{name}' удален.")
            except Exception as e:
                print(f"Ошибка удаления: {e}")
    elif name:
        print("Объект не найден.")

def change_attributes():
    # Изменение атрибута файла (Windows: Read Only, Hidden)
    name = get_path("Введите имя файла/папки: ")
    if not name or not os.path.exists(name):
        print("Объект не найден.")
        return

    print("Текущие атрибуты (упрощенно):")
    readonly = not os.access(name, os.W_OK)
    hidden = False
    # Проверка скрытости
    if os.name != 'nt':
        if os.path.basename(name).startswith('.'):
            hidden = True

    print(f"  Read Only: {readonly}")
    print(f"  Hidden: {hidden}")

    print("1. Установить Read Only")
    print("2. Снять Read Only")
    choice = input("Выберите действие: ")

    try:
        current_mode = os.stat(name).st_mode
        if choice == '1':
            # Убираем бит записи для владельца
            new_mode = current_mode & ~stat.S_IWRITE
            os.chmod(name, new_mode)
            print("Атрибут Read Only установлен.")
        elif choice == '2':
            # Добавляем бит записи
            new_mode = current_mode | stat.S_IWRITE
            os.chmod(name, new_mode)
            print("Атрибут Read Only снят.")
        else:
            print("Неверный выбор.")
    except Exception as e:
        print(f"Ошибка изменения атрибутов: {e}")

def change_permissions():
    # Изменяет права доступа
    if os.name == 'nt':
        print("Функция chmod не поддерживается в Windows.")
        return

    name = get_path("Введите имя файла/папки: ")
    if not name or not os.path.exists(name):
        print("Объект не найден.")
        return

    # Текущие права
    st = os.stat(name)
    print(f"Текущие права (octal): {oct(st.st_mode)[-3:]}")

    perm_str = input("Введите новые права (например, 755, 644): ").strip()
    if not perm_str.isdigit() or len(perm_str) != 3:
        print("Неверный формат. Используйте три цифры (например, 755).")
        return

    try:
        new_perm = int(perm_str, 8)
        os.chmod(name, new_perm)
        print(f"Права для '{name}' изменены на {perm_str}.")
    except Exception as e:
        print(f"Ошибка: {e}")

def search_files():
    # Поиск файла по маске в текущей папке и подпапках
    mask = get_path("Введите маску для поиска (например, *.txt, *file*): ")
    if not mask:
        return

    print(f"Поиск '{mask}' в {os.getcwd()} ...")
    found = 0
    for root, dirs, files in os.walk('.'):
        # Поиск в папках
        for d in dirs:
            if fnmatch.fnmatch(d, mask):
                print(f"[ПАПКА] {os.path.join(root, d)}")
                found += 1
        # Поиск в файлах
        for f in files:
            if fnmatch.fnmatch(f, mask):
                print(f"[ФАЙЛ] {os.path.join(root, f)}")
                found += 1

    print(f" Найдено объектов: {found} ")

# Основной цикл программы
def main():
    # Главное меню программы
    print("-"*50)
    print(" ФАЙЛОВЫЙ МЕНЕДЖЕР")
    print("-"*50)
    print(f"Текущая папка: {os.getcwd()}")

    # Словарь действий
    actions = {
        '1': list_directory,
        '2': change_dir,
        '3': create_folder,
        '4': create_file,
        '5': view_file,
        '6': edit_file,
        '7': copy_item,
        '8': move_rename,
        '9': delete_item,
        '10': change_attributes,
        '11': change_permissions,
        '12': search_files,
    }

    while True:
        print("\n- Меню -")
        print("0. Выход")
        print("1. Показать содержимое")
        print("2. Сменить папку")
        print("3. Создать папку")
        print("4. Создать файл")
        print("5. Просмотреть файл")
        print("6. Редактировать файл (дописать)")
        print("7. Копировать")
        print("8. Переместить/Переименовать")
        print("9. Удалить")
        print("10. Атрибуты (Read Only)")
        print("11. Права доступа (chmod)")
        print("12. Поиск (по маске)")
        print("-"*50)

        choice = get_user_choice()

        if choice == '0':
            if confirm_action("Выйти из программы?"):
                print("До свидания.")
                break
        elif choice in actions:
            try:
                actions[choice]()  # Вызов функции
            except Exception as e:
                print(f"Непредвиденная ошибка: {e}")
        else:
            print("Неизвестная команда. Пожалуйста, выберите номер из меню.")

if __name__ == "__main__":
    main()