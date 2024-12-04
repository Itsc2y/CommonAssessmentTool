"""
This module handles client-related API routes for the application.
"""

from datetime import datetime, date
from typing import List

from bson import ObjectId
from fastapi import APIRouter, HTTPException

from app.clients.schema import Client, ClientUpdate
from app.database import clients_collection

router = APIRouter(prefix="", tags=["clients"])


@router.post("/clients/create", response_model=Client, summary="Create a new client")
async def create_client(client_data: Client):
    """
    Create a new client in the database.

    Args:
        client_data (Client): The client data to create.

    Returns:
        Client: The created client object.
    """
    client_dict = client_data.dict(exclude={"id"})
    for key, value in client_dict.items():
        if isinstance(value, date):
            client_dict[key] = datetime.combine(value, datetime.min.time())
    result = await clients_collection.insert_one(client_dict)
    client_dict["_id"] = result.inserted_id
    return Client(id=str(client_dict["_id"]), **client_dict)


@router.get("/clients/{client_id}", response_model=Client, summary="Retrieve client by ID")
async def get_client_by_id(client_id: str):
    """
    Retrieve a client by their ID.

    Args:
        client_id (str): The ID of the client to retrieve.

    Returns:
        Client: The retrieved client object.
    """
    client = await clients_collection.find_one({"_id": ObjectId(client_id)})
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    # Convert ObjectId to string and return a formatted client object
    client["id"] = str(client["_id"])
    del client["_id"]
    return client


@router.get("/clients", response_model=List[Client], summary="Retrieve all clients")
async def get_all_clients():
    """
    Retrieve all clients in the database.

    Returns:
        List[Client]: A list of all clients.
    """
    # clients_cursor = list(await clients_collection.find())
    clients_cursor = await clients_collection.find().to_list(length=None)
    # Convert _id to id and return the list
    for client in clients_cursor:
        client["id"] = str(client["_id"])
        del client["_id"]

    return clients_cursor


@router.delete("/clients/{client_id}", response_model=None, summary="Delete client by ID")
async def delete_client_by_id(client_id: str):
    """
    Delete a client by their ID.

    Args:
        client_id (str): The ID of the client to delete.

    Returns:
        dict: A message indicating successful deletion.
    """
    if not ObjectId.is_valid(client_id):
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")

    client = await clients_collection.find_one({"_id": ObjectId(client_id)})
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")

    delete_result = await clients_collection.delete_one({"_id": ObjectId(client_id)})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Client not found")

    return {"message": f"Client with ID {client_id} deleted successfully."}


@router.delete("/clients", response_model=None, summary="Delete all clients")
async def delete_all_clients():
    """
    Delete all clients in the database.

    Returns:
        dict: A message indicating successful deletion of all clients.
    """
    await clients_collection.delete_many({})
    return {"message": "All clients deleted successfully."}


@router.put("/clients/{client_id}", response_model=Client, summary="Update client by ID")
async def update_client(client_id: str, client_data: ClientUpdate):
    """
    Update a client's information by their ID.

    Args:
        client_id (str): The ID of the client to update.
        client_data (ClientUpdate): The updated client data.

    Returns:
        Client: The updated client object.
    """
    client = await clients_collection.find_one({"_id": ObjectId(client_id)})
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")

    # Convert datetime.date to datetime.datetime for fields that are datetime.date
    updated_fields = client_data.dict(exclude_unset=True)
    for field, value in updated_fields.items():
        if isinstance(value, date):
            updated_fields[field] = datetime.combine(
                value, datetime.min.time())

    await clients_collection.update_one({"_id": ObjectId(client_id)}, {"$set": updated_fields})

    updated_client = await clients_collection.find_one({"_id": ObjectId(client_id)})
    updated_client["id"] = str(updated_client["_id"])
    del updated_client["_id"]

    return updated_client
