from datetime import datetime
from uuid import UUID
import uuid

from fastapi import FastAPI
from typing_extensions import List, TypedDict

from model import Account, Transaction

app = FastAPI()

user_id = uuid.uuid4()
account_id_0 = uuid.uuid4()
account_id_1 = uuid.uuid4()
category_investment_id = uuid.uuid4()
category_crypto_id = uuid.uuid4()
category_other_id = uuid.uuid4()

temp_bd = [
    {
        "id": user_id,
        "username": "average_crypto_fan",
        "email": "ilovecrypto@mail.ru",
        "created_at": "2023-10-01T12:00:00",
        "accounts": [
            {
                "id": account_id_0,
                "user_id": user_id,
                "name": "Bank Account",
                "balance": 1000,
                "currency": "USD",
                "created_at": "2023-10-01T12:00:00",
                "updated_at": "2023-10-01T12:00:00",
                "budgets": [],
                "targets": [],
                "transactions": [
                    {
                        "id": uuid.uuid4(),
                        "account_id": account_id_0,
                        "amount": 100000,
                        "timestamp": "2023-10-01T12:00:00",
                        "category": {
                            "id": category_other_id,
                            "name": "Other"
                        },
                        "description": "Initial deposit"
                    },
                    {
                        "id": uuid.uuid4(),
                        "account_id": account_id_0,
                        "amount": -50000,
                        "timestamp": "2023-10-02T13:00:00",
                        "category": {
                            "id": category_investment_id,
                            "name": "Investments"
                        },
                        "description": "купил"
                    },
                    {
                        "id": uuid.uuid4(),
                        "account_id": account_id_0,
                        "amount": -50000,
                        "timestamp": "2023-10-03T14:00:00",
                        "category": {
                            "id": category_investment_id,
                            "name": "Investments"
                        },
                        "description": "докупил"
                    },
                    {
                        "id": uuid.uuid4(),
                        "account_id": account_id_0,
                        "amount": 1000,
                        "timestamp": "2023-10-04T15:00:00",
                        "category": {
                            "id": category_investment_id,
                            "name": "Investments"
                        },
                        "description": "зафиксировал"
                    }
                ]
            },
            {
                "id": account_id_0,
                "user_id": user_id,
                "name": "Crypto Wallet",
                "balance": 0,
                "currency": "BTC",
                "created_at": "2023-10-01T12:00:00",
                "updated_at": "2023-10-01T12:00:00",
                "budgets": [],
                "targets": [],
                "transactions": [
                    {
                        "id": uuid.uuid4(),
                        "account_id": account_id_1,
                        "amount": 1,
                        "timestamp": "2023-10-01T13:00:00",
                        "category": {
                            "id": category_crypto_id,
                            "name": "Crypto"
                        },
                        "description": "купил крипту"
                    },
                    {
                        "id": uuid.uuid4(),
                        "account_id": account_id_1,
                        "amount": 2,
                        "timestamp": "2023-10-02T14:00:00",
                        "category": {
                            "id": category_crypto_id,
                            "name": "Crypto"
                        },
                        "description": "докупил крипту"
                    },
                    {
                        "id": uuid.uuid4(),
                        "account_id": account_id_1,
                        "amount": 3,
                        "timestamp": "2023-10-03T15:00:00",
                        "category": {
                            "id": category_crypto_id,
                            "name": "Crypto"
                        },
                        "description": "зафиксировал"
                    }
                ]
            }
        ]
    }
]


@app.get("/users")
def get_all_users() -> TypedDict('Response', {"status": int, "users": List[dict]}):
    return {"status": 200, "users": temp_bd}
@app.get("/users/{user_id}/accounts")
def get_all_accounts(user_id: UUID) -> TypedDict('Response', {"status": int, "accounts": List[Account]}):
    for user in temp_bd:
        if user["id"] == user_id:
            return {"status": 200, "accounts": user["accounts"]}
    return {"status": 404, "accounts": []}


@app.get("/users/{user_id}/accounts/{account_id}")
def get_account_by_id(user_id: UUID, account_id: UUID) -> TypedDict('Response', {"status": int, "account": Account}):
    for user in temp_bd:
        if user["id"] == user_id:
            for account in user["accounts"]:
                if account["id"] == account_id:
                    return {"status": 200, "account": account}
    return {"status": 404, "account": None}


@app.get("/users/{user_id}/accounts/{account_id}/transactions")
def get_transactions_by_account(user_id: UUID, account_id: UUID) -> TypedDict('Response', {"status": int, "transactions": List[Transaction]}):
    for user in temp_bd:
        if user["id"] == user_id:
            for account in user["accounts"]:
                if account["id"] == account_id:
                    return {"status": 200, "transactions": account["transactions"]}
    return {"status": 404, "transactions": []}


@app.put("/users/{user_id}/accounts/{account_id}/transactions")
def add_transaction(user_id: UUID, account_id: UUID, transaction: TypedDict('Transaction', {"amount": int, "category": int, "description": str})) \
        -> TypedDict('Response', {"status": int, "transaction": Transaction}):
    for user in temp_bd:
        if user["id"] == user_id:
            for account in user["accounts"]:
                if account["id"] == account_id:
                    new_transaction = {
                        "id": uuid.uuid4(),
                        "account_id": account_id,
                        "amount": transaction["amount"],
                        "timestamp": datetime.now().isoformat(),
                        "category": {"id": transaction["category"], "name": "Unknown"},
                        "description": transaction["description"]
                    }
                    account["transactions"].append(new_transaction)
                    return {"status": 201, "transaction": new_transaction}