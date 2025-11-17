import os
import requests
from dotenv import load_dotenv, set_key

load_dotenv()

SUBDOMAIN = os.getenv("SUBDOMAIN")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
AUTH_CODE = os.getenv("AUTH_CODE")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")
ENV_PATH = ".env"


def save_tokens(data: dict):
    set_key(ENV_PATH, "ACCESS_TOKEN", data["access_token"])
    set_key(ENV_PATH, "REFRESH_TOKEN", data["refresh_token"])
    print("Токены успешно сохранены в .env")


def get_access_token_from_code():
    url = f"https://{SUBDOMAIN}.amocrm.ru/oauth2/access_token"
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": AUTH_CODE,
        "redirect_uri": REDIRECT_URI
    }

    response = requests.post(url, json=data)
    if response.status_code == 200:
        tokens = response.json()
        save_tokens(tokens)
        print("Access Token успешно получен.")
        return tokens["access_token"]
    else:
        print("Ошибка:", response.status_code, response.text)
        return None


def refresh_access_token():
    url = f"https://{SUBDOMAIN}.amocrm.ru/oauth2/access_token"
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
        "redirect_uri": REDIRECT_URI
    }

    response = requests.post(url, json=data)
    if response.status_code == 200:
        tokens = response.json()
        save_tokens(tokens)
        print("Access Token обновлён.")
        return tokens["access_token"]
    else:
        print("Ошибка при обновлении токена:", response.status_code, response.text)
        return None


def get_valid_access_token():
    if ACCESS_TOKEN and REFRESH_TOKEN:
        print("Попытка обновить токен...")
        return refresh_access_token()
    elif AUTH_CODE:
        print("Получение токена первый раз...")
        return get_access_token_from_code()
    else:
        print("Укажите AUTH_CODE в .env для первого запуска.")
        return None


if __name__ == "__main__":
    token = get_valid_access_token()