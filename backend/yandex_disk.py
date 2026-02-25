# backend/shared/yandex_disk.py
import os
import requests

TOKEN = os.getenv("YANDEX_TOKEN")
BASE_URL = "https://cloud-api.yandex.net/v1/disk"


def headers():
    if not TOKEN:
        raise Exception("YANDEX_TOKEN не установлен")
    return {"Authorization": f"OAuth {TOKEN}"}


def create_folder(path: str):
    r = requests.put(f"{BASE_URL}/resources", headers=headers(), params={"path": path})
    if r.status_code not in (201, 409):
        raise Exception(r.text)


def list_folder(path: str, limit: int = 1000, offset: int = 0, fields: str = None):
    params = {"path": path, "limit": limit, "offset": offset}
    if fields:
        params["fields"] = fields

    r = requests.get(f"{BASE_URL}/resources", headers=headers(), params=params)
    r.raise_for_status()

    data = r.json()

    # Нормализация: если есть _embedded.items — дублируем в data['items']
    if isinstance(data, dict):
        embedded = data.get("_embedded", {})
        if isinstance(embedded, dict) and "items" in embedded:
            data["items"] = embedded["items"]

    return data


def delete_file(path: str):
    r = requests.delete(
        f"{BASE_URL}/resources",
        headers=headers(),
        params={"path": path, "permanently": "true"}
    )
    if r.status_code not in (202, 204):
        raise Exception(r.text)
    return r.status_code


def upload_file(local_path: str, disk_path: str):
    # получаем ссылку загрузки
    r = requests.get(
        f"{BASE_URL}/resources/upload",
        headers=headers(),
        params={"path": disk_path, "overwrite": "true"}
    )

    if r.status_code == 409:
        # если файл уже есть — удалим и повторим
        delete_file(disk_path)
        r = requests.get(
            f"{BASE_URL}/resources/upload",
            headers=headers(),
            params={"path": disk_path, "overwrite": "true"}
        )

    r.raise_for_status()
    href = r.json()["href"]

    with open(local_path, "rb") as f:
        up = requests.put(href, data=f)
        up.raise_for_status()


def download_link(disk_path: str):
    r = requests.get(
        f"{BASE_URL}/resources/download",
        headers=headers(),
        params={"path": disk_path}
    )
    r.raise_for_status()
    return r.json()["href"]