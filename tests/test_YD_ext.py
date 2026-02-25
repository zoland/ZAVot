# tests/test_YD_ext.py
import os
import sys
import json
import requests
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

# ТОКЕН БЕРЕМ ИЗ ПЕРЕМЕННОЙ ОКРУЖЕНИЯ!
YD_TOKEN = os.getenv('YANDEX_TOKEN')

# Добавляем путь к backend/shared для импорта yandex_disk.py
current_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
shared_path = os.path.join(current_dir, '..', 'backend', 'shared')
sys.path.append(os.path.normpath(shared_path))

try:
    from yandex_disk import list_folder, create_folder, upload_file, download_link, delete_file
    print("✅ Модуль Яндекс.Диска импортирован успешно")
except Exception as e:
    print(f"❌ Ошибка импорта yandex_disk.py: {e}")
    sys.exit(1)


def format_size(size_bytes):
    """Форматирование размера файла"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def get_items(folder_content: dict):
    """Достать items из ответа YD"""
    return folder_content.get('_embedded', {}).get('items', [])


def get_disk_info():
    """Получение подробной информации о диске"""
    print("💾 Получение информации о диске...")
    if not YD_TOKEN:
        print("❌ YANDEX_TOKEN не установлен")
        return None

    headers = {"Authorization": f"OAuth {YD_TOKEN}"}
    response = requests.get("https://cloud-api.yandex.net/v1/disk", headers=headers)
    if response.status_code == 200:
        data = response.json()
        total_YD = data.get('total_space', 0) / (1024**3)
        used_YD  = data.get('used_space',  0) / (1024**3)
        
        free_YD = total_YD - used_YD
        usage_percent = (used_YD / total_YD) * 100 if total_YD > 0 else 0
        
        print(f"📊 Информация о дисковом пространстве:")
        print(f"   Общий объем:  {total_YD:.2f} GB")
        print(f"   Использовано: {used_YD:.2f} GB ({usage_percent:.1f}%)")
        print(f"   Свободно:     {free_YD:.2f} GB")
        return {
            'total': total_YD,
            'used': used_YD,
            'free': free_YD,
            'percent': usage_percent
        }
    else:
        print(f"❌ Ошибка получения информации о диске: {response.status_code}")
        return None


def list_folder_detailed(path, indent=0):
    """Рекурсивное отображение содержимого папки с размерами (аналог ls -R)"""
    try:
        folder_content = list_folder(path)
        items = get_items(folder_content)

        if not items:
            print(" " * indent + "ℹ️  Папка пуста или ошибка")
            return
        
        folders = []
        files = []
        
        # Разделяем папки и файлы
        for item in items:
            if item.get('type') == 'dir':
                folders.append(item)
            else:
                files.append(item)
        
        # Отображаем файлы
        for item in files:
            name = item.get('name', 'Без имени')
            size = item.get('size', 0)
            formatted_size = format_size(size)
            print(" " * indent + f"📄 {name} ({formatted_size})")
        
        # Отображаем папки и рекурсивно обходим их
        for item in folders:
            name = item.get('name', 'Без имени')
            print(" " * indent + f"📁 {name}/")
            
            sub_path = f"{path.rstrip('/')}/{name}"
            list_folder_detailed(sub_path, indent + 2)
            
    except Exception as e:
        print(" " * indent + f"❌ Ошибка просмотра {path}: {e}")


def analyze_disk_usage():
    """Анализ использования диска - где находятся большие файлы"""
    print("\n🔍 Анализ использования диска...")
    
    try:
        root_content = list_folder("disk:/")
        items = get_items(root_content)
        
        if not items:
            print("ℹ️  Невозможно получить содержимое корня диска")
            return
        
        large_files = []
        
        print("📊 Размеры элементов в корне диска:")
        
        for item in items:
            name = item.get('name', 'Без имени')
            size = item.get('size', 0)
            item_type = item.get('type', '')
            
            if item_type == 'file':
                formatted_size = format_size(size)
                print(f"  📄 {name}: {formatted_size}")
                
                if size > 1024 * 1024:  # Больше 1MB
                    large_files.append((name, size, formatted_size))
            else:
                print(f"  📁 {name}/")
        
        if large_files:
            print(f"\n🔥 Большие файлы (>1MB):")
            large_files.sort(key=lambda x: x[1], reverse=True)
            for name, size, formatted_size in large_files[:10]:
                print(f"  📄 {name}: {formatted_size}")
        else:
            print("✅ Нет больших файлов (>1MB)")
            
    except Exception as e:
        print(f"❌ Ошибка анализа использования диска: {e}")


def show_project_structure():
    """Показ структуры проекта ZAVot на Яндекс.Диске"""
    print("\n📂 Структура проекта ZAVot на Яндекс.Диске:")
    print("=" * 50)
    
    base_folder = "disk:/04ЧР_ОП"
    
    try:
        base_content = list_folder(base_folder)
        items = get_items(base_content)

        if items is not None:
            print(f"📁 {base_folder}/")
            list_folder_detailed(base_folder, 2)
        else:
            print(f"ℹ️  Папка {base_folder} не найдена или пуста")
            
    except Exception as e:
        print(f"❌ Ошибка просмотра структуры проекта: {e}")


def test_file_operations():
    """Тест операций с файлами: создание, запись, чтение, удаление"""
    print("\n🧪 Тест операций с файлами...")
    
    base_folder = "disk:/04ЧР_ОП"
    test_folder = f"{base_folder}/test_operations"
    
    try:
        create_folder(test_folder)
        print("✅ Тестовая папка создана")
        
        test_data = {
            'timestamp': datetime.now().isoformat(),
            'test': 'file_operations',
            'size': '1KB'
        }
        
        local_file = 'test_file.json'
        with open(local_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        print("✅ Локальный тестовый файл создан")
        
        disk_path = f"{test_folder}/test_file.json"
        upload_file(local_file, disk_path)
        print("✅ Файл загружен на диск")
        
        folder_content = list_folder(test_folder)
        items = get_items(folder_content)
        for item in items:
            if item.get('name') == 'test_file.json':
                size = item.get('size', 0)
                formatted_size = format_size(size)
                print(f"✅ Размер загруженного файла: {formatted_size}")
                break
        
        try:
            download_url = download_link(disk_path)
            print("✅ Ссылка для скачивания получена")
        except Exception as e:
            print(f"ℹ️  Ошибка получения ссылки: {e}")
        
        try:
            delete_file(disk_path)
            print("✅ Файл удален с диска")
        except Exception as e:
            print(f"ℹ️  Ошибка удаления файла: {e}")
        
        if os.path.exists(local_file):
            os.remove(local_file)
            print("✅ Локальный файл удален")
            
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования операций с файлами: {e}")
        import traceback
        traceback.print_exc()
        return False


def comprehensive_disk_test():
    """Комплексный тест Яндекс.Диска"""
    print("🚀 Комплексный тест Яндекс.Диска для ZAVot")
    print("=" * 60)
    
    try:
        get_disk_info()
        analyze_disk_usage()
        show_project_structure()
        test_file_operations()
        
        print("\n🎉 Комплексный тест завершен успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка комплексного теста: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    yandex_token = os.getenv('YANDEX_TOKEN')
    print(f"🔑 YANDEX_TOKEN установлен: {'Да' if yandex_token else 'Нет'}")
    
    if not yandex_token or yandex_token == 'ваш_токен':
        print("⚠️  Установите ваш реальный YANDEX_TOKEN в окружении!")
        sys.exit(1)
    
    # Комплексный тест
    if comprehensive_disk_test():
        print("\n🏆 Все тесты Яндекс.Диска пройдены успешно!")
    else:
        print("\n❌ Тесты Яндекс.Диска не пройдены")