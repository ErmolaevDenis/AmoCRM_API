import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import amocrm_client as client

app = FastAPI(title="amoCRM_api")

class Lead(BaseModel):
    name: str
    price: int = 0


@app.post("/create_lead")
def create_lead_endpoint(lead_name: str, lead_price: int,
                         contact_name: str = None, contact_phone: str = None, contact_email: str = None, contact_position: str = None,
                         company_name: str = None, company_phone: str = None, company_email: str = None,
                         company_web: str = None, company_address: str = None):
    try:
        lead = Lead(name=lead_name, price=lead_price)
        if contact_name and company_name:
            contact_id = client.create_contact(contact_name, contact_phone, contact_email, contact_position)
            company_id = client.create_company(company_name, company_phone, company_email, company_web, company_address)
            client.attach_company_to_contact(contact_id, company_id)
            result = client.create_lead(name=lead.name, price=lead.price, contact_id=contact_id, company_id=company_id)
        elif contact_name:
            contact_id = client.create_contact(contact_name, contact_phone, contact_email, contact_position)
            result = client.create_lead(name=lead.name, price=lead.price, contact_id=contact_id)
        elif company_name:
            company_id = client.create_company(company_name, company_phone, company_email, company_web, company_address)
            result = client.create_lead(name=lead.name, price=lead.price, company_id=company_id)
        else:
            result = client.create_lead(name=lead.name, price=lead.price)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/add_comment_to_lead")
def add_comment_to_lead_endpoint(lead_id: int, text: str):
    try:
        result = client.add_comment_to_lead(lead_id, text)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/move_lead")
def move_lead_endpoint(lead_id: int, pipeline_name: str, status_name: str):
    try:
        result = client.move_lead(lead_id, pipeline_name, status_name)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/move_lead_next_status")
def move_lead_next_status_endpoint(lead_id: int):
    try:
        result = client.move_lead_to_next_status(lead_id)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == '__main__':
    create_lead_endpoint(lead_name="Max_Neuro", lead_price=1000000,
                         contact_name="Maxim", contact_phone="0123456789", contact_email="max@test.com", contact_position="CEO",
                         company_name="NEURO", company_phone="987654321", company_email="neuro@test.com",
                         company_web="http://neuro_test.com", company_address="NN")