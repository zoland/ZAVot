# tests/test_YD.py
import os
import sys
import json

# УСТАНОВИТЕ ВАШ ТОКЕН ЯНДЕКС.ДИСКА ЗДЕСЬ!
# Получите токен по инструкции: https://yandex.ru/dev/disk/poligon/
os.environ['YANDEX_TOKEN'] = 'y0__xCNmNUXGNuWAyDt76XDFjCuxsT2B0FY85jXmRt4St9OVDN5A3AVgEyu'

# Добавляем путь к backend/shared для импорта yandex_disk.py
current_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
shared_path = os.path.join(current_dir, '..', 'backend', 'shared')
sys.path.append(os.path.normpath(shared_path))

print(f"🔍 Пути для поиска модулей: {sys.path}")

try:
    from yandex_disk import list_folder, create_folder
    print("✅ Модуль Яндекс.Диска импортирован успешно")
except Exception as e:
    print(f"❌ Ошибка импорта yandex_disk.py: {e}")
    sys.exit(1)

def test_yandex_disk_browsing():
    """Тестирование просмотра каталога Яндекс.Диска"""
    print("🚀 Тестирование просмотра каталога Яндекс.Диска")
    print("=" * 50)
    
    # Базовая папка проекта (из отчета)
    base_folder = "disk:/04ЧР_ОП"
    
    try:
        # Проверим токен перед началом
        token = os.getenv('YANDEX_TOKEN')
        if not token:
            print("⚠️  YANDEX_TOKEN не установлен!")
            return False
            
        print(f"🔑 Используется токен: {token[:10]}...")
        
        # Создаем базовую папку если её нет
        print(f"📁 Проверка/создание базовой папки: {base_folder}")
        create_folder(base_folder)
        print("✅ Базовая папка готова")
        
        # Просматриваем содержимое
        print(f"\n📂 Содержимое папки {base_folder}:")
        folder_content = list_folder(base_folder)
        
        # Анализируем результаты
        if isinstance(folder_content, dict) and 'items' in folder_content:
            items = folder_content['items']
            print(f"Найдено {len(items)} элементов:")
            
            for item in items:
                item_type = "📁" if item.get('type') == 'dir' else "📄"
                name = item.get('name', 'Без имени')
                size = item.get('size', 0)
                
                if item.get('type') == 'dir':
                    print(f"  {item_type} {name}/")
                else:
                    size_mb = size / (1024 * 1024) if size > 0 else 0
                    print(f"  {item_type} {name} ({size_mb:.2f} MB)")
            
            # Показываем общую информацию
            if 'total' in folder_content:
                print(f"\n📊 Всего элементов: {folder_content['total']}")
            
        else:
            print("ℹ️  Папка пуста или ошибка получения содержимого")
            print(f"Ответ: {folder_content}")
            
        # Тест подпапок для ZAVot
        test_folders = [
            f"{base_folder}/files",
            f"{base_folder}/files/main",
            f"{base_folder}/files/main/apps"
        ]
        
        print(f"\n📋 Создание структуры папок ZAVot:")
        for folder in test_folders:
            try:
                create_folder(folder)
                print(f"  ✅ {folder}")
            except Exception as e:
                if "already exists" in str(e).lower() or "уже существует" in str(e):
                    print(f"  ℹ️  {folder} - уже существует")
                else:
                    print(f"  ℹ️  {folder} - {str(e)[:50]}...")
        
        # Просматриваем структуру files
        files_folder = f"{base_folder}/files"
        print(f"\n📂 Содержимое {files_folder}:")
        try:
            files_content = list_folder(files_folder)
            if isinstance(files_content, dict) and 'items' in files_content:
                for item in files_content['items']:
                    item_type = "📁" if item.get('type') == 'dir' else "📄"
                    name = item.get('name', 'Без имени')
                    print(f"  {item_type} {name}")
            else:
                print("  ℹ️  Папка files пуста или ошибка")
        except Exception as e:
            print(f"  ❌ Ошибка просмотра files: {e}")
            
        print("\n✅ Просмотр каталога Яндекс.Диска работает!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка работы с Яндекс.Диском: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_disk_space_info():
    """Получение информации о занятом пространстве"""
    print("\n💾 Информация о дисковом пространстве:")
    print("=" * 40)
    
    try:
        # Получаем информацию о диске
        disk_info = list_folder("disk:/")
        
        if isinstance(disk_info, dict):
            if 'total' in disk_info and 'used' in disk_info:
                total_gb = disk_info.get('total', 0) / (1024**3)
                used_gb = disk_info.get('used', 0) / (1024**3)
                free_gb = total_gb - used_gb
                usage_percent = (used_gb / total_gb * 100) if total_gb > 0 else 0
                
                print(f"Общий объем: {total_gb:.2f} GB")
                print(f"Использовано: {used_gb:.2f} GB")
                print(f"Свободно: {free_gb:.2f} GB")
                print(f"Занято: {usage_percent:.1f}%")
            else:
                print("ℹ️  Детальная информация о диске недоступна")
                available_keys = list(disk_info.keys()) if isinstance(disk_info, dict) else "Не словарь"
                print(f"Доступные ключи: {available_keys}")
        else:
            print(f"ℹ️  Неожиданный формат ответа: {type(disk_info)}")
            
    except Exception as e:
        print(f"ℹ️  Ошибка получения информации о диске: {e}")

if __name__ == "__main__":
    yandex_token = os.getenv('YANDEX_TOKEN')
    print(f"🔑 YANDEX_TOKEN установлен: {'Да' if yandex_token else 'Нет'}")
    
    if not yandex_token:
        print("⚠️  ВНИМАНИЕ: Установите YANDEX_TOKEN в коде!")
        print("Пример: os.environ['YANDEX_TOKEN'] = 'ваш_токен'")
    
    # Тест просмотра каталога
    success = test_yandex_disk_browsing()
    if success:
        # Тест информации о диске
        test_disk_space_info()
        print("\n🎉 Все тесты Яндекс.Диска пройдены успешно!")
    else:
        print("\n❌ Тесты Яндекс.Диска не пройдены")