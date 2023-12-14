import requests
import json
import pandas as pd
import zipfile
import os
import time

# Функция для скачивания данных с API Drom.ru
def get_data_from_api():
    url = "https://api.drom.ru/v1.2/bulls/search"
    params = {
        "marks": "TOYOTA",
        "models": "CROWN",
        "generation[]": ["15", "16"],
        "cities": ["vladivostok", "ussuriysk"],
        "status": "active",
        "documents": "true",
        "repair": "false"
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data

# Функция для создания и записи данных в файл Data.csv
def create_csv_file(data):
    df = pd.DataFrame(columns=[
        "Номер объявления",
        "URL объявления",
        "Марка авто",
        "Модель авто",
        "Цена продажи",
        "Цена Дрома",
        "Поколение авто",
        "Комплектация авто",
        "Пробег",
        "Пробег по РФ",
        "Цвет",
        "Тип кузова",
        "Мощность двигателя",
        "Тип топлива",
        "Объем двигателя"
    ])
    try:
        for item in data["result"]["ads"]:
            ad_data = [
                item.get("bull_id", "null"),
                item.get("url", "null"),
                item["car"].get("make", "null"),
                item["car"].get("model", "null"),
                item.get("price", "null"),
                item.get("price_formatted", "null"),
                item["car"].get("gen", "null"),
                item["car"].get("complectation", "null"),
                item["car"].get("run", "null"),
                "без пробега по РФ" if item["car"].get("run_mapped") == 2 else "null",
                item["car"].get("color", "null"),
                item["car"].get("body", "null"),
                item["car"].get("engine_power", "null"),
                item["car"].get("fuel_type", "null"),
                item["car"].get("engine_capacity", "null")
            ]
            df.loc[len(df)] = ad_data
    except KeyError:
     print("Ошибка в структуре данных,проверьте, что ключи соответствуют ожидаемым")
    df.to_csv("Data.csv", index=False)

# Функция для скачивания фотографий объявлений
def download_photos(data):
    for item in data["result"]["ads"]:
        ad_dir = str(item.get("bull_id", "null"))
        os.makedirs(ad_dir, exist_ok=True)
        for i, photo in enumerate(item["photos"]):
            photo_url = photo.get("preview")
            response = requests.get(photo_url)
            with open(f"{ad_dir}/photo_{i}.jpg", "wb") as file:
                file.write(response.content)
            time.sleep(1)

# Выполняем все действия
data = get_data_from_api()
create_csv_file(data)
download_photos(data)

# Создание архива
with zipfile.ZipFile("Result_Crown.zip", "w") as archive:
    archive.write("Data.csv")
    for foldername, subfolders, filenames in os.walk("."):
        for filename in filenames:
            if filename.endswith(".jpg"):
                archive.write(os.path.join(foldername, filename))