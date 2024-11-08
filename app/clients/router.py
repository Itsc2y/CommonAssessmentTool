from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from typing import List

from app.clients.service.logic import interpret_and_calculate
from app.clients.schema import PredictionInput, Client, ClientUpdate

router = APIRouter(prefix="/clients", tags=["clients"])

mock_clients_db = {
    1: Client(
        id=1,
        first_name="Amy",
        last_name="Doe",
        email="amy.doe@example.com",
        date_of_birth="1995-04-23",
        address="123 Main St, Springfield",
        phone="123-456-7890"
    ),
    2: Client(
        id=2,
        first_name="Bob",
        last_name="Smith",
        email="bob.smith@example.com",
        date_of_birth="1999-08-17",
        address="456 Elm St, Springfield",
        phone="098-765-4321"
    ),
}


def generate_new_id():
    return max(mock_clients_db.keys(), default=0) + 1

@router.post("/create", response_model=Client, summary="Create a new client")
async def create_client(client_data: Client):
    new_id = generate_new_id()
    client_data.id = new_id  # Set new client ID
    mock_clients_db[new_id] = client_data
    return client_data


@router.get("/clients/{id}", response_model=Client, summary="Retrieve client by ID")
async def get_client_by_id(id: int):
    client = mock_clients_db.get(id)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.get("/clients", response_model=List[Client], summary="Retrieve all clients")
async def get_all_clients():
    return list(mock_clients_db.values())


@router.delete("/clients/{id}", response_model=None, summary="Delete client by ID")
async def delete_client_by_id(id: int):
    client = mock_clients_db.pop(id, None)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return {"message": f"Client with ID {id} deleted successfully."}


@router.delete("/clients", response_model=None, summary="Delete all clients")
async def delete_all_clients():
    mock_clients_db.clear()
    return {"message": "All clients deleted successfully."}


@router.put("/clients/{id}", response_model=Client, summary="Update client by ID")
async def update_client(id: int, client_data: ClientUpdate):
    client = mock_clients_db.get(id)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")

    updated_fields = client_data.model_dump(exclude_unset=True)
    updated_client = client.model_copy(update=updated_fields)
    mock_clients_db[id] = updated_client
    
    return updated_client