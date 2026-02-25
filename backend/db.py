# backend/shared/db.py

import ydb
import os

def get_ydb_driver():
    driver_config = ydb.DriverConfig(
        endpoint=os.getenv('YDB_ENDPOINT'),
        database=os.getenv('YDB_DATABASE'),
        credentials=ydb.credentials_from_env_variables()
    )
    driver = ydb.Driver(driver_config)
    driver.wait(timeout=5)
    return driver

def get_session():
    driver = get_ydb_driver()
    return driver.table_client.session().create()