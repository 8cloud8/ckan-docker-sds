"""
Shared configuration and fixtures for HealthDCAT-AP tests.
"""
import os
import time
import requests
import pytest

# Global test configuration
BASE_URL = os.getenv('CKAN_BASE_URL', 'http://localhost:5001')
API_URL = f"{BASE_URL}/api/3/action"


@pytest.fixture(scope="session")
def ckan_base_url():
    """Fixture providing CKAN base URL."""
    return BASE_URL


@pytest.fixture(scope="session")
def ckan_api_url():
    """Fixture providing CKAN API URL."""
    return API_URL


@pytest.fixture(scope="session", autouse=True)
def wait_for_ckan():
    """Wait for CKAN to be ready before running tests."""
    print("Waiting for CKAN to be ready...")
    start_time = time.time()
    timeout = 5
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{API_URL}/status_show", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print("CKAN is ready!")
                    return
        except requests.exceptions.RequestException:
            pass
        time.sleep(2)
    
    pytest.fail(f"CKAN not ready after {timeout} seconds")


@pytest.fixture(scope="session")
def test_organization():
    """Create test organization for health datasets."""
    org_data = {
        "name": "health-data-org",
        "title": "Health Data Organization",
        "description": "Test organization for HealthDCAT-AP datasets"
    }
    
    try:
        response = requests.post(
            f"{API_URL}/organization_create",
            json=org_data,
            headers={"Authorization": "test-api-key"}
        )
        if response.status_code == 200:
            print("Test organization created successfully")
            return org_data["name"]
    except requests.exceptions.RequestException as e:
        print(f"Note: Organization creation failed (expected in read-only tests): {e}")
    
    return org_data["name"]
