from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
from faker import Faker
import random
import pandas as pd
from datetime import datetime
import os
from fastapi.responses import FileResponse
import os
app = FastAPI()

fake = Faker()

# ----------------------------
# Schema Model
# ----------------------------

class Customer(BaseModel):
    customer_id: int
    name: str
    email: EmailStr
    account_balance: float
    kyc_status: str


# ----------------------------
# Request Model
# ----------------------------

from typing import Dict

class GenerateRequest(BaseModel):
    records: int
    mode: str = "valid"
    schema: Dict[str, str]

# ----------------------------
# Generator Function
# ----------------------------

def generate_field(field_type, mode):

    if field_type == "int":
        return random.randint(10000, 99999) if mode == "valid" else 999

    if field_type == "float":
        return round(random.uniform(1000, 100000), 2) if mode == "valid" else -100

    if field_type == "name":
        return fake.name() if mode != "negative" else ""

    if field_type == "email":
        return fake.email() if mode != "negative" else "invalid-email"

    if field_type.startswith("choice:"):
        options = field_type.split(":")[1].split(",")
        return random.choice(options)

    return "N/A"
valid_records = []
invalid_records = []

for i in range(request.records):

    # Mode logic
    if request.mode == "mixed":
        if i < int(request.records * 0.7):
            mode = "valid"
        elif i < int(request.records * 0.85):
            mode = "boundary"
        else:
            mode = "negative"
    else:
        mode = request.mode

    record = {}

    for field, field_type in request.schema.items():
        record[field] = generate_field(field_type, mode)

    valid_records.append(record)

    # Generate based on mode
    if mode == "valid":
        raw = {
            "customer_id": random.randint(10000, 99999),
            "name": fake.name(),
            "email": fake.email(),
            "account_balance": round(random.uniform(1000, 100000), 2),
            "kyc_status": random.choice(["Verified", "Pending", "Rejected"])
        }

    elif mode == "boundary":
        raw = {
            "customer_id": 10000,
            "name": fake.name(),
            "email": fake.email(),
            "account_balance": 0.00,
            "kyc_status": "Pending"
        }

    else:  # negative
        raw = {
            "customer_id": 999,
            "name": "",
            "email": "invalid-email",
            "account_balance": -500,
            "kyc_status": "Unknown"
        }

    try:
        validated = Customer(**raw)
        valid_records.append(validated.model_dump())
    except Exception:
        invalid_records.append(raw)


# ----------------------------
# API Endpoint
# ----------------------------

@app.post("/generate")
def generate_data(request: GenerateRequest):

    valid_records = []

    for _ in range(request.records):
        raw = generate_customer()
        validated = Customer(**raw)
        valid_records.append(validated.model_dump())

    df = pd.DataFrame(valid_records)

    os.makedirs("output", exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"output/api_generated_{timestamp}.csv"

    df.to_csv(filename, index=False)

    return {
    "message": "File generated",
    "mode": request.mode,
    "valid_records": len(valid_records),
    "invalid_records": len(invalid_records),
    "file_name": filename
}