import pytest
import requests


def test_item_list_structure(base_url, valid_headers):
    response = requests.get(f"{base_url}/Test/GetItemList", headers=valid_headers)

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    # Assert the expected fields are present in each item and have the correct types
    for item in data:
        assert "itemKey" in item
        assert "itemNumber" in item
        assert "itemDesc" in item
        assert "upc" in item
        assert "sku" in item
        assert "locations" in item

        assert isinstance(item["itemKey"], int)
        assert isinstance(item["itemNumber"], str)
        assert isinstance(item["itemDesc"], str)
        assert isinstance(item["locations"], list)

        assert item["upc"] is None or isinstance(item["upc"], str)
        assert item["sku"] is None or isinstance(item["sku"], str)

        for loc in item["locations"]:
            assert "locationId" in loc
            assert "onHandQty" in loc
            assert isinstance(loc["locationId"], str)
            assert isinstance(loc["onHandQty"], (int, float))


# This fixture creates one item and shares it across the tests below to enforce DRY principles


@pytest.fixture(scope="module")
def created_item(base_url, valid_headers):
    # Create a new item to be used in the tests below
    response = requests.post(
        f"{base_url}/Test/CreateItem",
        headers=valid_headers,
        params={"itemNumber": "TEST_001", "itemDesc": "Test item created by pytest"},
    )

    # Assert the creation was successful and we got back the expected item structure
    assert response.status_code == 200

    # Assert the created item appears in the list endpoint and has the expected structure
    list_resp = requests.get(f"{base_url}/Test/GetItemList", headers=valid_headers)
    assert list_resp.status_code == 200
    items = list_resp.json()
    item = next((i for i in items if i.get("itemNumber") == "TEST_001"), None)
    assert item is not None

    # Basic validations on the found item
    assert "itemKey" in item
    assert "itemNumber" in item
    assert "itemDesc" in item
    assert "upc" in item
    assert "sku" in item
    assert "locations" in item

    assert isinstance(item["itemKey"], int)
    assert isinstance(item["itemNumber"], str)
    assert isinstance(item["itemDesc"], str)
    assert isinstance(item["locations"], list)

    assert item["upc"] is None or isinstance(item["upc"], str)
    assert item["sku"] is None or isinstance(item["sku"], str)

    for loc in item["locations"]:
        assert "locationId" in loc
        assert "onHandQty" in loc
        assert isinstance(loc["locationId"], str)
        assert isinstance(loc["onHandQty"], (int, float))

    # Yield the found item and ensure cleanup runs afterwards
    try:
        yield item
    finally:
        # Best-effort cleanup; ignore errors so they don't mask test failures
        try:
            requests.post(
                f"{base_url}/Test/DeleteItem",
                headers=valid_headers,
                params={"itemKey": item["itemKey"]},
            )
        except Exception:
            pass


def test_create_item_success(base_url, valid_headers, created_item):
    response = requests.get(f"{base_url}/Test/GetItemList", headers=valid_headers)

    # Confirm the get list call was successful
    assert response.status_code == 200

    items = response.json()
    item_keys = [item["itemKey"] for item in items]

    # Confirm the created item is in the list by matching on itemKey
    assert created_item["itemKey"] in item_keys


def test_create_item_missing_params_fails(base_url, valid_headers):
    # Attempt to create an item without itemDesc
    response = requests.post(
        f"{base_url}/Test/CreateItem",
        headers=valid_headers,
        params={"itemNumber": "TEST_MISSING_DESC"},
    )

    # Assert the response indicates failure due to missing itemDesc
    assert response.status_code == 400

    # Attempt to create an item without itemNumber
    response = requests.post(
        f"{base_url}/Test/CreateItem",
        headers=valid_headers,
        params={"itemDesc": "Missing item number"},
    )

    # Assert the response indicates failure due to missing itemNumber
    assert response.status_code == 400


def test_edit_seeded_item(base_url, valid_headers):
    list_response = requests.get(f"{base_url}/Test/GetItemList", headers=valid_headers)
    items = list_response.json()
    original_item = next(
        (item for item in items if str(item.get("itemNumber")) == "78394"), None
    )
    assert original_item is not None
    updated = {**original_item, "itemDesc": "Updated by pytest"}

    edit_response = requests.post(
        f"{base_url}/Test/EditItem", headers=valid_headers, json=updated
    )
    assert edit_response.status_code == 200

    # Retrieve the list again to confirm the edit shows up there
    updated_list_response = requests.get(
        f"{base_url}/Test/GetItemList", headers=valid_headers
    )
    updated_items = updated_list_response.json()

    match = next(
        (i for i in updated_items if str(i.get("itemNumber")) == "78394"), None
    )
    assert match is not None
    assert match["itemDesc"] == "Updated by pytest"

    # Restore the original description so seeded data returns to normal
    restore_payload = {**original_item, "itemDesc": original_item["itemDesc"]}
    restore_response = requests.post(
        f"{base_url}/Test/EditItem", headers=valid_headers, json=restore_payload
    )
    assert restore_response.status_code == 200


def test_edit_created_item(base_url, valid_headers, created_item):
    # Edit the created item with a new description
    updated = {**created_item, "itemDesc": "Edited description by pytest"}

    # Call the edit endpoint with the updated item
    edit_response = requests.post(
        f"{base_url}/Test/EditItem", headers=valid_headers, json=updated
    )

    # Assert the edit was successful
    assert edit_response.status_code == 200

    # Confirm the edit shows up in the list
    list_response = requests.get(f"{base_url}/Test/GetItemList", headers=valid_headers)
    items = list_response.json()

    # Find the edited item in the list by matching on itemKey and confirm the description was updated
    match = next((i for i in items if i["itemKey"] == created_item["itemKey"]), None)
    assert match is not None
    assert match["itemDesc"] == "Edited description by pytest"


def test_edit_valid_upc(base_url, valid_headers, created_item):
    valid_upc = "036000291452"
    updated = {**created_item, "upc": valid_upc}

    response = requests.post(
        f"{base_url}/Test/EditItem", headers=valid_headers, json=updated
    )

    assert response.status_code == 200

    list_response = requests.get(f"{base_url}/Test/GetItemList", headers=valid_headers)
    assert list_response.status_code == 200
    items = list_response.json()
    match = next((i for i in items if i["itemKey"] == created_item["itemKey"]), None)
    assert match is not None
    assert match.get("upc") == f"0{valid_upc}"


def test_edit_invalid_upc(base_url, valid_headers, created_item):
    # Attempt to set an invalid UPC (too short)
    invalid_update = {**created_item, "upc": "123"}

    response = requests.post(
        f"{base_url}/Test/EditItem", headers=valid_headers, json=invalid_update
    )
    # Assert the response indicates failure due to invalid UPC format
    assert response.status_code == 400


def test_edit_rejects_itemkey_change(base_url, valid_headers, created_item):
    # Attempt to change the itemKey
    attempted_key = created_item["itemKey"] + 1
    updated = {**created_item, "itemKey": attempted_key}

    response = requests.post(
        f"{base_url}/Test/EditItem", headers=valid_headers, json=updated
    )

    # Assert the response indicates failure due to itemKey change
    assert response.status_code == 400


def test_delete_item_success(base_url, valid_headers):
    # Create a dedicated item for this test
    create_response = requests.post(
        f"{base_url}/Test/CreateItem",
        headers=valid_headers,
        params={
            "itemNumber": "TEST_DELETE",
            "itemDesc": "Item created for delete test",
        },
    )
    assert create_response.status_code == 200

    # Retrieve the list to find the itemKey of the created item
    list_resp = requests.get(f"{base_url}/Test/GetItemList", headers=valid_headers)
    assert list_resp.status_code == 200
    items = list_resp.json()
    target = next((i for i in items if i.get("itemNumber") == "TEST_DELETE"), None)
    assert target is not None

    item_key = target["itemKey"]

    # Call the delete endpoint with the itemKey of the created item
    delete_response = requests.post(
        f"{base_url}/Test/DeleteItem",
        headers=valid_headers,
        params={"itemKey": item_key},
    )

    # Assert the delete was successful
    assert delete_response.status_code == 200

    # Confirm the deleted item no longer appears in the list
    list_response = requests.get(f"{base_url}/Test/GetItemList", headers=valid_headers)
    items = list_response.json()

    item_keys = [item["itemKey"] for item in items]
    assert item_key not in item_keys


def test_delete_item_invalid_key(base_url, valid_headers):
    # Call the delete endpoint with an invalid itemKey and confirm it fails (status code not 200)
    response = requests.post(
        f"{base_url}/Test/DeleteItem", headers=valid_headers, params={"itemKey": -1}
    )

    # Assert the response indicates failure due to invalid itemKey
    assert response.status_code == 400
