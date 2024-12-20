"""
This module contains tests for the client update functionality in the FastAPI application.
"""

from unittest.mock import AsyncMock, patch
from datetime import date, datetime
from bson import ObjectId
from fastapi import HTTPException
import pytest
from app.clients.schema import ClientUpdate, Client
from app.clients.router import create_client, get_client_by_id, get_all_clients, update_client, delete_all_clients, delete_client_by_id
from app.database import clients_collection


@pytest.mark.asyncio
async def test_create_client():
    """
    Test the create_client function to ensure it creates a new client in the database correctly.
    """
    # Prepare test data
    mock_inserted_id = ObjectId()
    test_client_data = {
        "id": str(mock_inserted_id),  # Add a mock ObjectId here
        "first_name": "Alice",
        "last_name": "Smith",
        "email": "alice.smith@example.com",
        "date_of_birth": date(1992, 5, 10),
        "address": "789 Birch St, Springfield, IL",
        "phone": "555-6789"
    }

    # Mock the insert_one method to return a mock inserted_id
    clients_collection.insert_one = AsyncMock(
        return_value=AsyncMock(inserted_id=mock_inserted_id))

    # Call the function with test data
    test_client = Client(**test_client_data)
    created_client = await create_client(test_client)

    # Assertions
    assert created_client.id == str(mock_inserted_id)
    for key, value in test_client_data.items():
        if isinstance(value, date):
            assert created_client.dict()[key] == datetime.combine(
                value, datetime.min.time()).date()
        else:
            assert created_client.dict()[key] == value


@pytest.mark.asyncio
async def test_get_client_by_id():
    """
    Test the get_client_by_id function to ensure it retrieves a client correctly.
    """

    client_id = str(ObjectId())  # Generate a test client ID
    client_data = {
        "_id": ObjectId(client_id),
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "date_of_birth": "1990-01-15",
        "address": "123 Elm St, Springfield, IL",
        "phone": "555-1234"
    }

    # Mock the database method to return the sample client data
    clients_collection.find_one = AsyncMock(return_value=client_data)

    # Call the handler directly instead of using TestClient
    client = await get_client_by_id(client_id)  # Directly calling the handler

    # Perform assertions
    assert client["id"] == client_id
    assert client["first_name"] == "John"
    assert client["last_name"] == "Doe"
    assert client["email"] == "john.doe@example.com"
    assert client["date_of_birth"] == "1990-01-15"
    assert client["address"] == "123 Elm St, Springfield, IL"
    assert client["phone"] == "555-1234"


@pytest.mark.asyncio
async def test_get_client_by_id_not_found():
    """
    Test the get_client_by_id function to ensure it raises an HTTPException
    when the client is not found.
    """

    non_existent_client_id = str(ObjectId())

    # Mock the find_one method to return None for a non-existent client
    clients_collection.find_one = AsyncMock(return_value=None)

    # Call the handler directly
    try:
        await get_client_by_id(non_existent_client_id)
        pytest.fail("Expected HTTPException not raised")
    except HTTPException as e:
        assert e.status_code == 404
        assert e.detail == "Client not found"


@pytest.mark.asyncio
async def test_get_all_clients():
    """
    Test the get_all_clients function to ensure it retrieves all clients correctly.
    """
    # Sample client data
    client_data = [
        {
            "_id": ObjectId(),
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "date_of_birth": "1990-01-15",
            "address": "123 Elm St, Springfield, IL",
            "phone": "555-1234"
        },
        {
            "_id": ObjectId(),
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@example.com",
            "date_of_birth": "1985-06-22",
            "address": "456 Oak St, Chicago, IL",
            "phone": "555-5678"
        }
    ]

    # Mocking the async cursor with to_list method
    class MockCursor:
        async def to_list(self, length):
            return client_data

    mock_cursor = MockCursor()

    # Mock the `find` method to return the mock_cursor
    with patch('app.database.clients_collection.find', return_value=mock_cursor):
        # Call the function and await the result
        clients = await get_all_clients()

        # Perform assertions
        assert len(clients) == 2  # Check the length of the returned list
        assert clients[0]["first_name"] == "John"
        assert clients[1]["first_name"] == "Jane"


@pytest.mark.asyncio
async def test_get_all_clients_empty():
    """
    Test the get_all_clients function to ensure it returns an empty list 
    when no clients are found.
    """
    client_data = []
    class MockCursor:
        async def to_list(self, length):
            return client_data

    mock_cursor = MockCursor()

    # Mock the `find` method to return the mock_cursor
    with patch('app.database.clients_collection.find', return_value=mock_cursor):
        # Call the function and await the result
        clients = await get_all_clients()

        # Perform assertions
        assert clients == []


@pytest.mark.asyncio
async def test_update_client():
    """
    Test the update_client function to ensure it correctly updates a client's information.
    """
    # Prepare test data
    original_client_id = str(ObjectId())
    original_client_data = {
        "_id": ObjectId(original_client_id),
        "first_name": "John",
        "last_name": "Doe",
        "email": "johndoe@example.com",
        "date_of_birth": date(1990, 1, 1),
        "address": "123 Main St",
        "phone": "123-456-7890"
    }

    # Prepare update data
    client_update = ClientUpdate(
        first_name="Jane",
        last_name="Doee",
        email="jane.doee@example.com",
        date_of_birth=datetime.combine(date(1991, 2, 2), datetime.min.time()),
        address="456 Elm St",
        phone="098-765-4321"
    )

    clients_collection.find_one = AsyncMock(return_value=original_client_data)
    clients_collection.update_one = AsyncMock()

    # Call the update method
    updated_client = await update_client(original_client_id, client_update)

    # Update the mock to return the updated data
    updated_client_data = original_client_data.copy()
    updated_client_data.update(client_update.dict())
    updated_client_data["_id"] = ObjectId(
        original_client_id)  # Restore the original _id

    clients_collection.find_one = AsyncMock(return_value=updated_client_data)

    # Call the update method again to get the updated client
    updated_client = await update_client(original_client_id, client_update)

    # Assertions
    assert updated_client["first_name"] == "Jane"
    assert updated_client["last_name"] == "Doee"
    assert updated_client["email"] == "jane.doee@example.com"
    assert updated_client["date_of_birth"] == datetime(1991, 2, 2).date()
    assert updated_client["address"] == "456 Elm St"
    assert updated_client["phone"] == "098-765-4321"


@pytest.mark.asyncio
async def test_update_client_not_found():
    """
    Test the update_client function to ensure it raises an HTTPException 
    when the client is not found.
    """
    # Prepare test data
    non_existent_client_id = str(ObjectId())

    # Mock the find_one method to return None
    clients_collection.find_one = AsyncMock(return_value=None)

    # Prepare update data
    client_update = ClientUpdate(
        first_name="John Updated",
        last_name="Doe"
    )

    # Expect HTTPException to be raised
    with pytest.raises(HTTPException) as exc_info:
        await update_client(non_existent_client_id, client_update)

    # Additional assertion on the exception
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Client not found"


@pytest.mark.asyncio
async def test_delete_client_by_id():
    """
    Test the delete_client_by_id function to ensure it deletes a client by ID correctly.
    """
    # Prepare test data
    test_client_id = str(ObjectId())
    client_data = {
        "_id": ObjectId(test_client_id),
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "date_of_birth": "1990-01-15",
        "address": "123 Elm St, Springfield, IL",
        "phone": "555-1234"
    }

    # Mock find_one to simulate client exists
    clients_collection.find_one = AsyncMock(return_value=client_data)
    # Mock delete_one to simulate successful deletion
    clients_collection.delete_one = AsyncMock(
        return_value=AsyncMock(deleted_count=1))

    # Call the delete function
    response = await delete_client_by_id(test_client_id)

    # Assertions
    assert response["message"] == f"Client with ID {test_client_id} deleted successfully."


@pytest.mark.asyncio
async def test_delete_client_by_id_not_found():
    """
    Test the delete_client_by_id function to ensure it raises HTTPException 
    when the client is not found.
    """
    # Prepare test data
    non_existent_client_id = str(ObjectId())

    # Mock find_one to simulate client does not exist
    clients_collection.find_one = AsyncMock(return_value=None)

    # Call the delete function and expect an HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await delete_client_by_id(non_existent_client_id)

    # Assertions
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Client not found"


# Test case for invalid ObjectId format
@pytest.mark.asyncio
async def test_delete_client_by_id_invalid_id():
    """
    Test the delete_client_by_id function to ensure it raises HTTPException 
    when an invalid ObjectId format is provided.
    """
    # Invalid ObjectId
    invalid_client_id = "invalid_object_id"

    # Call the delete function and expect an HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await delete_client_by_id(invalid_client_id)

    # Assertions
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Invalid ObjectId format"


@pytest.mark.asyncio
async def test_delete_client_no_deletion():
    """
    Test the delete_client_by_id function to ensure it raises an HTTPException
    when the delete operation does not delete any client (i.e., deleted_count == 0).
    """
    # Prepare test data
    test_client_id = str(ObjectId())  # Generate a test ObjectId
    client_data = {
        "_id": ObjectId(test_client_id),
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "date_of_birth": "1990-01-15",
        "address": "123 Elm St, Springfield, IL",
        "phone": "555-1234"
    }

    # Mock find_one to simulate the client exists
    clients_collection.find_one = AsyncMock(return_value=client_data)

    # Mock delete_one to simulate that no client is deleted (deleted_count=0)
    clients_collection.delete_one = AsyncMock(
        return_value=AsyncMock(deleted_count=0))

    # Call the delete function and expect an HTTPException to be raised
    with pytest.raises(HTTPException) as exc_info:
        await delete_client_by_id(test_client_id)

    # Assertions
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Client not found"


@pytest.mark.asyncio
async def test_delete_all_clients():
    """
    Test the delete_all_clients function to ensure it deletes all clients in the database.
    """
    # Mock delete_many to simulate successful deletion
    clients_collection.delete_many = AsyncMock()

    # Call the delete function
    response = await delete_all_clients()

    # Assertions
    assert response["message"] == "All clients deleted successfully."
