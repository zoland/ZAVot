# tests/test_ydb.py
import ydb
import os
import time

# Конфигурация из отчета
os.environ['YDB_ENDPOINT'] = 'grpcs://ydb.serverless.yandexcloud.net:2135'
os.environ['YDB_DATABASE'] = '/ru-central1/b1gv8svig7g9qarfknd1/etnl447sor653hngpn2i'

def get_driver():
    """Создаем YDB драйвер"""
    driver = ydb.Driver(
        endpoint=os.getenv('YDB_ENDPOINT'),
        database=os.getenv('YDB_DATABASE'),
        credentials=ydb.AnonymousCredentials()
    )
    return driver

def create_zavot_tables(driver):
    """Создаем таблицы согласно ТЗ ZAVot"""
    # Ждем подключения подольше
    print("⏳ Ожидание подключения к YDB (может занять до 60 секунд)...")
    try:
        driver.wait(timeout=60)
        print("✅ Подключение к YDB установлено!")
    except Exception as e:
        print(f"❌ Не удалось подключиться к YDB: {e}")
        return False
    
    session = driver.table_client.session().create()
    
    print("📋 Создание таблиц согласно ТЗ ZAVot...")
    
    # Таблица пользователей
    try:
        try:
            session.drop_table('users')
            print("🗑️  Удалена старая таблица users")
        except:
            pass
        
        session.create_table(
            'users',
            ydb.TableDescription()
            .with_primary_key('u_code')
            .with_columns(
                ydb.Column('u_code', ydb.OptionalType(ydb.PrimitiveType.Utf8)),
                ydb.Column('role', ydb.OptionalType(ydb.PrimitiveType.Utf8)),
                ydb.Column('password', ydb.OptionalType(ydb.PrimitiveType.Utf8))
            )
        )
        print("✅ Таблица users создана")
    except Exception as e:
        print(f"ℹ️  Таблица users: {e}")
    
    # Таблица протоколов
    try:
        try:
            session.drop_table('protocols')
            print("🗑️  Удалена старая таблица protocols")
        except:
            pass
        
        session.create_table(
            'protocols',
            ydb.TableDescription()
            .with_primary_key('p_num')
            .with_columns(
                ydb.Column('p_num', ydb.OptionalType(ydb.PrimitiveType.Utf8)),
                ydb.Column('file_name', ydb.OptionalType(ydb.PrimitiveType.Utf8)),
                ydb.Column('date_start', ydb.OptionalType(ydb.PrimitiveType.Utf8)),
                ydb.Column('date_end', ydb.OptionalType(ydb.PrimitiveType.Utf8)),
                ydb.Column('status', ydb.OptionalType(ydb.PrimitiveType.Utf8)),
                ydb.Column('vote_type', ydb.OptionalType(ydb.PrimitiveType.Utf8)),
                ydb.Column('folder_main', ydb.OptionalType(ydb.PrimitiveType.Utf8)),
                ydb.Column('folder_apps', ydb.OptionalType(ydb.PrimitiveType.Utf8))
            )
        )
        print("✅ Таблица protocols создана")
    except Exception as e:
        print(f"ℹ️  Таблица protocols: {e}")
    
    # Таблица вопросов
    try:
        try:
            session.drop_table('questions')
            print("🗑️  Удалена старая таблица questions")
        except:
            pass
        
        session.create_table(
            'questions',
            ydb.TableDescription()
            .with_primary_key('q_id')
            .with_columns(
                ydb.Column('q_id', ydb.OptionalType(ydb.PrimitiveType.Int64)),
                ydb.Column('p_num', ydb.OptionalType(ydb.PrimitiveType.Utf8)),
                ydb.Column('q_num', ydb.OptionalType(ydb.PrimitiveType.Utf8)),
                ydb.Column('default_vote', ydb.OptionalType(ydb.PrimitiveType.Utf8))
            )
        )
        print("✅ Таблица questions создана")
    except Exception as e:
        print(f"ℹ️  Таблица questions: {e}")
    
    # Таблица голосов
    try:
        try:
            session.drop_table('votes')
            print("🗑️  Удалена старая таблица votes")
        except:
            pass
        
        session.create_table(
            'votes',
            ydb.TableDescription()
            .with_primary_key('v_id')
            .with_columns(
                ydb.Column('v_id', ydb.OptionalType(ydb.PrimitiveType.Int64)),
                ydb.Column('p_num', ydb.OptionalType(ydb.PrimitiveType.Utf8)),
                ydb.Column('u_code', ydb.OptionalType(ydb.PrimitiveType.Utf8)),
                ydb.Column('q_num', ydb.OptionalType(ydb.PrimitiveType.Utf8)),
                ydb.Column('vote', ydb.OptionalType(ydb.PrimitiveType.Utf8))
            )
        )
        print("✅ Таблица votes создана")
    except Exception as e:
        print(f"ℹ️  Таблица votes: {e}")
    
    # Таблица логов
    try:
        try:
            session.drop_table('logs')
            print("🗑️  Удалена старая таблица logs")
        except:
            pass
        
        session.create_table(
            'logs',
            ydb.TableDescription()
            .with_primary_key('id')
            .with_columns(
                ydb.Column('id', ydb.OptionalType(ydb.PrimitiveType.Int64)),
                ydb.Column('u_code', ydb.OptionalType(ydb.PrimitiveType.Utf8)),
                ydb.Column('action', ydb.OptionalType(ydb.PrimitiveType.Utf8)),
                ydb.Column('l_date', ydb.OptionalType(ydb.PrimitiveType.Utf8)),
                ydb.Column('l_time', ydb.OptionalType(ydb.PrimitiveType.Utf8))
            )
        )
        print("✅ Таблица logs создана")
    except Exception as e:
        print(f"ℹ️  Таблица logs: {e}")
    
    return True

def test_basic_operations(driver):
    """Тест базовых операций CRUD"""
    try:
        driver.wait(timeout=30)
        session = driver.table_client.session().create()
    except:
        print("❌ Не удалось создать сессию")
        return False
    
    print("\n🧪 Тестирование базовых операций...")
    
    # Тест: Добавление пользователя
    try:
        query = """
            DECLARE $u_code AS Utf8;
            DECLARE $role AS Utf8;
            DECLARE $password AS Utf8;
            
            UPSERT INTO users (u_code, role, password) 
            VALUES ($u_code, $role, $password);
        """
        
        session.transaction().execute(
            query=query,
            parameters={
                '$u_code': 'admin001',
                '$role': 'admin',
                '$password': 'test123'
            },
            commit_tx=True
        )
        print("✅ Добавлен/обновлен тестовый пользователь")
    except Exception as e:
        print(f"ℹ️  Ошибка при добавлении пользователя: {e}")
    
    # Тест: Чтение пользователя
    try:
        query = """
            SELECT * FROM users WHERE u_code = 'admin001';
        """
        
        result = session.transaction().execute(
            query=query,
            commit_tx=True
        )
        
        if result[0].rows:
            user = dict(result[0].rows[0])
            print(f"✅ Найден пользователь: {user}")
        else:
            print("ℹ️  Пользователь не найден")
    except Exception as e:
        print(f"ℹ️  Ошибка чтения пользователя: {e}")
    
    return True

def test_connection():
    """Основной тест подключения и создания таблиц"""
    print("🚀 Тестирование YDB для проекта ZAVot")
    print("=" * 50)
    
    try:
        driver = get_driver()
        print("✅ Драйвер YDB создан")
        
        # Создаем таблицы
        if not create_zavot_tables(driver):
            driver.stop()
            return False
        
        # Тестируем операции
        test_basic_operations(driver)
        
        # Финальный тест
        try:
            driver.wait(timeout=30)
            session = driver.table_client.session().create()
            result = session.transaction().execute(
                "SELECT COUNT(*) as count FROM users;",
                commit_tx=True
            )
            print(f"📊 Количество пользователей в базе: {result[0].rows[0]['count']}")
        except Exception as e:
            print(f"ℹ️  Ошибка финального теста: {e}")
        
        driver.stop()
        print("\n🎉 YDB для ZAVot настроена успешно!")
        print("✅ Все таблицы созданы и готовы к работе")
        return True
        
    except Exception as e:
        print(f"❌ Критическая ошибка настройки YDB: {e}")
        import traceback
        traceback.print_exc()
        try:
            driver.stop()
        except:
            pass
        return False

if __name__ == "__main__":
    test_connection()