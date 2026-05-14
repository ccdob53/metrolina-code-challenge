import requests

def test_api_is_reachable(base_url):
    response = requests.get(f"{base_url}/Test/TestEndpoint")
    assert response.status_code == 200