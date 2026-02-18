import os, requests

TOKEN = os.getenv("YANDEX_TOKEN")
BASE_URL = "https://cloud-api.yandex.net/v1/disk"

def headers():
    return {"Authorization": f"OAuth {TOKEN}"}

def create_folder(path: str):
    r = requests.put(f"{BASE_URL}/resources", headers=headers(), params={"path": path})
    if r.status_code not in (201, 409):
        raise Exception(r.text)

def list_folder(path: str):
    r = requests.get(f"{BASE_URL}/resources", headers=headers(), params={"path": path, "limit": 100})
    r.raise_for_status()
    return r.json()

def delete_file(path: str):
    r = requests.delete(f"{BASE_URL}/resources",
                        headers=headers(),
                        params={"path": path, "permanently": "true"})
    return r.status_code

def upload_file(local_path: str, disk_path: str):
    # получаем ссылку загрузки
    r = requests.get(f"{BASE_URL}/resources/upload",
                     headers=headers(),
                     params={"path": disk_path, "overwrite": "true"})

    if r.status_code == 409:
        # если файл уже есть — удалим и повторим
        delete_file(disk_path)
        r = requests.get(f"{BASE_URL}/resources/upload",
                         headers=headers(),
                         params={"path": disk_path, "overwrite": "true"})

    r.raise_for_status()
    href = r.json()["href"]

    with open(local_path, "rb") as f:
        up = requests.put(href, files={"file": f})
        up.raise_for_status()
        
def download_link(disk_path: str):
    r = requests.get(f"{BASE_URL}/resources/download",
                     headers=headers(),
                     params={"path": disk_path})
    r.raise_for_status()
    return r.json()["href"]




