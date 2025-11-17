import os
import requests
from fastapi import HTTPException

from dotenv import load_dotenv

load_dotenv()

SUBDOMAIN = os.getenv("SUBDOMAIN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

def create_lead(name: str, price: int = 0, contact_id: int = None, company_id: int = None):
    url = f"https://{SUBDOMAIN}.amocrm.ru/api/v4/leads"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    if contact_id and company_id:
        data = [
            {
                "name": name,
                "price": price,
                "_embedded": {
                    "contacts": [{"id": contact_id}],
                    "companies": [{"id": company_id}]
                }
            }
        ]

    elif contact_id:
        data = [
            {
                "name": name,
                "price": price,
                "_embedded": {
                    "contacts": [{"id": contact_id}]
                }
            }
        ]

    elif company_id:
        data = [
            {
                "name": name,
                "price": price,
                "_embedded": {
                    "companies": [{"id": company_id}]
                }
            }
        ]

    else:
        data = [
            {
                "name": name,
                "price": price,
            }
        ]

    response = requests.post(url, json=data, headers=headers)

    if response.status_code in (200, 201):
        return response.json()
    else:
        raise Exception(f"Ошибка при создании лида: {response.status_code} {response.text}")


def create_contact(name: str, phone: str = None, email: str = None, position: str = None):
    url = f"https://{SUBDOMAIN}.amocrm.ru/api/v4/contacts"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    custom_fields = []

    if phone:
        custom_fields.append({
            "field_code": "PHONE",
            "values": [{"value": phone}]
        })

    if email:
        custom_fields.append({
            "field_code": "EMAIL",
            "values": [{"value": email}]
        })

    if position:
        custom_fields.append({
            "field_code": "POSITION",
            "values": [{"value": position}]
        })

    data = [
        {
            "name": name,
            "custom_fields_values": custom_fields
        }
    ]

    response = requests.post(url, json=data, headers=headers)

    if response.status_code in (200, 201):
        contact_id = response.json()["_embedded"]["contacts"][0]["id"]
        return contact_id
    else:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Ошибка при создании контакта: {response.status_code} {response.text}"
        )


def create_company(name: str, phone: str = None, email: str = None, web: str = None, address: str = None):
    url = f"https://{SUBDOMAIN}.amocrm.ru/api/v4/companies"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    custom_fields = []

    if phone:
        custom_fields.append({
            "field_code": "PHONE",
            "values": [{"value": phone}]
        })

    if email:
        custom_fields.append({
            "field_code": "EMAIL",
            "values": [{"value": email}]
        })

    if web:
        custom_fields.append({
            "field_code": "WEB",
            "values": [{"value": web}]
        })

    if address:
        custom_fields.append({
            "field_code": "ADDRESS",
            "values": [{"value": address}]
        })

    data = [
        {
            "name": name,
            "custom_fields_values": custom_fields
        }
    ]

    response = requests.post(url, json=data, headers=headers)

    if response.status_code in (200, 201):
        company_id = response.json()["_embedded"]["companies"][0]["id"]
        return company_id
    else:
        raise HTTPException(response.status_code, response.text)


def attach_company_to_contact(contact_id: int, company_id: int):
    url = f"https://{SUBDOMAIN}.amocrm.ru/api/v4/contacts/{contact_id}"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "_embedded": {
            "companies": [{"id": company_id}]
        }
    }

    response = requests.patch(url, json=data, headers=headers)

    if response.status_code in (200, 201):
        return True
    else:
        raise HTTPException(response.status_code, response.text)


def attach_company_to_lead(lead_id: int, company_id: int):
    url = f"https://{SUBDOMAIN}.amocrm.ru/api/v4/leads/{lead_id}"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "_embedded": {
            "companies": [{"id": company_id}]
        }
    }

    response = requests.patch(url, json=data, headers=headers)

    if response.status_code in (200, 201):
        return True
    else:
        raise HTTPException(response.status_code, response.text)


def add_comment_to_lead(lead_id: int, text: str):
    url = f"https://{SUBDOMAIN}.amocrm.ru/api/v4/leads/{lead_id}/notes"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    data = [
        {
            "note_type": "common",
            "params": {
                "text": text
            }
        }
    ]

    response = requests.post(url, json=data, headers=headers)

    if response.status_code in (200, 201):
        return response.json()
    else:
        raise HTTPException(response.status_code, f"Ошибка при добавлении комментария: {response.text}")


def move_lead(lead_id: int, pipeline_name: str, status_name: str):
    url = f"https://{SUBDOMAIN}.amocrm.ru/api/v4/leads/pipelines"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Ошибка получения воронок: {response.text}")

    pipelines = response.json()["_embedded"]["pipelines"]

    pipeline = next(
        (p for p in pipelines if p["name"].lower() == pipeline_name.lower()),
        None
    )

    if not pipeline:
        raise Exception(f"Воронка '{pipeline_name}' не найдена")

    pipeline_id = pipeline["id"]

    statuses = pipeline["_embedded"]["statuses"]
    status = next(
        (s for s in statuses if s["name"].lower() == status_name.lower()),
        None
    )

    if not status:
        raise Exception(
            f"Статус '{status_name}' не найден в воронке '{pipeline_name}'"
        )

    status_id = status["id"]

    patch_url = f"https://{SUBDOMAIN}.amocrm.ru/api/v4/leads"
    body = [
        {
            "id": lead_id,
            "pipeline_id": pipeline_id,
            "status_id": status_id
        }
    ]

    result = requests.patch(patch_url, headers=headers, json=body)

    if result.status_code not in (200, 201):
        raise Exception(f"Ошибка переноса сделки: {result.status_code} {result.text}")

    return result.json()


def move_lead_to_next_status(lead_id: int):
    lead_url = f"https://{SUBDOMAIN}.amocrm.ru/api/v4/leads/{lead_id}"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    lead_resp = requests.get(lead_url, headers=headers)

    if lead_resp.status_code != 200:
        raise Exception(f"Ошибка получения сделки: {lead_resp.text}")

    lead = lead_resp.json()
    pipeline_id = lead["pipeline_id"]
    current_status_id = lead["status_id"]

    pipelines_url = f"https://{SUBDOMAIN}.amocrm.ru/api/v4/leads/pipelines"
    pipelines_resp = requests.get(pipelines_url, headers=headers)

    if pipelines_resp.status_code != 200:
        raise Exception(f"Ошибка получения воронок: {pipelines_resp.text}")

    pipelines = pipelines_resp.json()["_embedded"]["pipelines"]

    pipeline = next((p for p in pipelines if p["id"] == pipeline_id), None)
    if not pipeline:
        raise Exception("Не найдена текущая воронка сделки")

    statuses = pipeline["_embedded"]["statuses"]

    status_ids = [s["id"] for s in statuses]

    if current_status_id not in status_ids:
        raise Exception("Текущий статус не найден в воронке")

    current_index = status_ids.index(current_status_id)

    if current_index == len(statuses) - 1:
        raise Exception("Сделка уже в последнем статусе, дальше некуда")

    next_status_id = statuses[current_index + 1]["id"]

    patch_url = f"https://{SUBDOMAIN}.amocrm.ru/api/v4/leads"
    body = [
        {
            "id": lead_id,
            "pipeline_id": pipeline_id,
            "status_id": next_status_id
        }
    ]

    result = requests.patch(patch_url, json=body, headers=headers)

    if result.status_code not in (200, 201):
        raise Exception(
            f"Ошибка перевода в следующий статус: {result.status_code} {result.text}"
        )

    return result.json()