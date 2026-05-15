import requests

def test_valid_api_key(base_url, valid_headers):
    response = requests.get(f"{base_url}/Test/GetItemList", headers=valid_headers)

    # With valid API key, we expect a successful response (200 OK)
    
    assert response.status_code == 200

def test_invalid_api_key(base_url, invalid_headers):
    response = requests.get(f"{base_url}/Test/GetItemList", headers=invalid_headers)

    # With invalid API key, we expect an unauthorized (401) or forbidden (403) response
    
    assert response.status_code in [401, 403]
    assert response.status_code != 200

def test_missing_api_key(base_url, no_headers):
    response = requests.get(f"{base_url}/Test/GetItemList", headers=no_headers)

    # With no API key, we expect an unauthorized (401) or forbidden (403) response
    
    assert response.status_code in [401, 403]
    assert response.status_code != 200