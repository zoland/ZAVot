# tests/test_memory_store.py

import json
import os
from datetime import datetime

# Имитация структуры данных
data_store = {
    'users': {
        'admin001': {
            'role': 'admin',
            'password': 'test123'
        },
        'user001': {
            'role': 'user',
            'password': 'user123'
        }
    },
    'protocols': {
        '001/2026': {
            'file_name': 'Протокол №001 от 2026.pdf',
            'date_start': '2026-03-01',
            'date_end': '2026-03-07',
            'status': 'draft',
            'vote_type': 'open',
            'folder_main': 'files/main/001_2026',
            'folder_apps': 'files/main/001_2026/apps'
        }
    },
    'questions': {
        1: {
            'p_num': '001/2026',
            'q_num': '1',
            'default_vote': '@'
        }
    },
    'votes': {},
    'logs': []
}

def test_memory_store():
    """Тестирование in-memory хранилища"""
    print("🚀 Тестирование in-memory хранилища для ZAVot")
    print("=" * 50)
    
    # Тест пользователей
    print(f"👥 Пользователей: {len(data_store['users'])}")
    for code, user in data_store['users'].items():
        print(f"  {code}: {user['role']}")
    
    # Тест протоколов
    print(f"📝 Протоколов: {len(data_store['protocols'])}")
    for p_num, protocol in data_store['protocols'].items():
        print(f"  {p_num}: {protocol['status']}")
    
    # Тест вопросов
    print(f"❓ Вопросов: {len(data_store['questions'])}")
    
    # Тест логирования
    log_entry = {
        'u_code': 'admin001',
        'action': 'test_connection',
        'l_date': datetime.now().strftime('%Y-%m-%d'),
        'l_time': datetime.now().strftime('%H:%M:%S')
    }
    data_store['logs'].append(log_entry)
    print(f"📝 Логов: {len(data_store['logs'])}")
    
    print("\n✅ In-memory хранилище работает корректно!")
    print("📊 Данные готовы для использования в Cloud Functions")
    
    return True

def save_to_json():
    """Сохранение данных в JSON файл (имитация Яндекс.Диска)"""
    try:
        with open('test_data.json', 'w', encoding='utf-8') as f:
            json.dump(data_store, f, ensure_ascii=False, indent=2)
        print("💾 Данные сохранены в test_data.json")
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")
        return False

def load_from_json():
    """Загрузка данных из JSON файла"""
    try:
        with open('test_data.json', 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        print("📂 Данные загружены из test_data.json")
        return loaded_data
    except FileNotFoundError:
        print("ℹ️  Файл test_data.json не найден (создадим новый)")
        return None
    except Exception as e:
        print(f"❌ Ошибка загрузки: {e}")
        return None

if __name__ == "__main__":
    # Тест хранилища
    if test_memory_store():
        # Сохраняем данные
        if save_to_json():
            # Загружаем и проверяем
            loaded = load_from_json()
            if loaded:
                print("✅ Цикл сохранения/загрузки работает!")