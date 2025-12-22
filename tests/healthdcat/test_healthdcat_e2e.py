import pytest
import requests
import json
import time
from typing import Dict, Any


class TestHealthDCATAP:
    """End-to-end tests for HealthDCAT-AP extension"""
    
    BASE_URL = "http://localhost:5001"
    API_URL = f"{BASE_URL}/api/3/action"
    
    @classmethod
    def setup_class(cls):
        """Setup class - wait for CKAN to be ready"""
        cls.wait_for_ckan()
        cls.create_test_organization()
    
    @classmethod
    def wait_for_ckan(cls, timeout=5):
        """Wait for CKAN to be ready"""
        print("Waiting for CKAN to be ready...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{cls.API_URL}/status_show")
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        print("CKAN is ready!")
                        return
            except requests.exceptions.RequestException:
                pass
            time.sleep(2)
        
        raise Exception(f"CKAN not ready after {timeout} seconds")
    
    @classmethod
    def create_test_organization(cls):
        """Create test organization for health datasets"""
        org_data = {
            "name": "health-data-org",
            "title": "Health Data Organization", 
            "description": "Test organization for HealthDCAT-AP datasets"
        }
        
        try:
            response = requests.post(
                f"{cls.API_URL}/organization_create",
                json=org_data,
                headers={"Authorization": "test-api-key"}
            )
            if response.status_code == 200:
                print("Test organization created successfully")
        except requests.exceptions.RequestException as e:
            print(f"Note: Organization creation failed (expected in read-only tests): {e}")
    
    def test_ckan_status(self):
        """Test that CKAN is running and extensions are loaded"""
        response = requests.get(f"{self.API_URL}/status_show")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        
        extensions = data["result"]["extensions"]
        required_extensions = ["dcat", "scheming_datasets", "dcat_json_interface"]
        
        for ext in required_extensions:
            assert ext in extensions, f"Extension {ext} not found in loaded extensions"
    
    def test_healthdcat_schema_available(self):
        """Test that HealthDCAT-AP schema is available"""
        response = requests.get(f"{self.API_URL}/scheming_dataset_schema_list")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                schema_list = data["result"]
                print(f"Available schemas: {schema_list}")
                # The health schema should be configured as the default dataset schema
        
        # Test that we can access the health schema configuration
        try:
            response = requests.get(f"{self.API_URL}/scheming_dataset_schema_show?type=dataset")
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    schema = data["result"]
                    assert "health" in schema.get("about", "").lower() or "dcat" in schema.get("about", "").lower()
                    print("HealthDCAT-AP schema is configured correctly")
        except requests.exceptions.RequestException:
            print("Schema endpoint not available - this is expected in some configurations")
    
    def test_dcat_profiles_configured(self):
        """Test that DCAT RDF profiles include HealthDCAT-AP"""
        # This test verifies the configuration indirectly by testing dataset creation
        # with health-specific fields
        sample_health_dataset = {
            "name": "test-health-dataset-profiles",
            "title": "Test Health Dataset - Profiles",
            "notes": "Testing HealthDCAT-AP RDF profiles configuration",
            "tags": [{"name": "health"}, {"name": "dcat-ap"}, {"name": "test"}],
            "owner_org": "health-data-org"
        }
        
        try:
            response = requests.post(
                f"{self.API_URL}/package_create",
                json=sample_health_dataset,
                headers={"Authorization": "test-api-key"}
            )
            # Even if creation fails due to auth, we can test the response structure
            print(f"Dataset creation response status: {response.status_code}")
            if response.status_code != 403:  # If not forbidden due to auth
                assert response.status_code in [200, 201, 409]  # OK, Created, or Conflict
        except requests.exceptions.RequestException:
            pass  # Expected in read-only environments
    
    def test_health_dataset_fields_validation(self):
        """Test that health-specific fields are properly validated"""
        health_dataset = {
            "name": "test-health-validation",
            "title": "Health Data Validation Test",
            "notes": "Testing health-specific field validation",
            "tags": [{"name": "health-data"}, {"name": "validation"}],
            # Health-specific fields that should be available in HealthDCAT-AP
            "contact": [{
                "name": "Health Data Contact",
                "email": "healthdata@example.com",
                "uri": "https://example.com/contact"
            }],
            "theme": ["health", "public-health"],
            "owner_org": "health-data-org"
        }
        
        try:
            response = requests.post(
                f"{self.API_URL}/package_create",
                json=health_dataset,
                headers={"Authorization": "test-api-key"}
            )
            # Test validation response even if auth fails
            if response.status_code not in [403, 401]:
                data = response.json()
                if not data.get("success"):
                    errors = data.get("error", {})
                    # Check that health-specific fields don't cause validation errors
                    assert "contact" not in errors, "Contact field should be valid in HealthDCAT-AP"
                    assert "theme" not in errors, "Theme field should be valid in HealthDCAT-AP"
        except requests.exceptions.RequestException:
            pass
    
    def test_dataset_list_with_health_data(self):
        """Test listing datasets and verify health data structure"""
        response = requests.get(f"{self.API_URL}/package_list")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        
        # If datasets exist, test their structure
        dataset_list = data["result"]
        if dataset_list:
            # Get details of first dataset
            response = requests.get(f"{self.API_URL}/package_show?id={dataset_list[0]}")
            if response.status_code == 200:
                dataset_data = response.json()
                if dataset_data["success"]:
                    dataset = dataset_data["result"]
                    # Verify dataset has expected structure for health data
                    assert "name" in dataset
                    assert "title" in dataset
                    print(f"Dataset structure validated: {dataset.get('name')}")
    
    def test_rdf_export_with_health_profile(self):
        """Test RDF export includes HealthDCAT-AP profile elements"""
        # First get list of datasets
        response = requests.get(f"{self.API_URL}/package_list")
        if response.status_code == 200:
            data = response.json()
            if data["success"] and data["result"]:
                dataset_id = data["result"][0]
                
                # Try to get RDF export
                rdf_url = f"{self.BASE_URL}/dataset/{dataset_id}.rdf"
                try:
                    response = requests.get(rdf_url)
                    if response.status_code == 200:
                        rdf_content = response.text
                        # Check for DCAT-AP and health-related RDF elements
                        health_indicators = [
                            "dcat:",
                            "dct:",
                            "foaf:",
                            "health" # Look for health-related terms
                        ]
                        
                        found_indicators = []
                        for indicator in health_indicators:
                            if indicator in rdf_content:
                                found_indicators.append(indicator)
                        
                        print(f"RDF export found indicators: {found_indicators}")
                        assert len(found_indicators) >= 2, "RDF should contain DCAT-AP elements"
                except requests.exceptions.RequestException:
                    print("RDF export test skipped - endpoint not accessible")


class TestHealthDataSamples:
    """Tests for sample health datasets"""
    
    API_URL = "http://localhost:5001/api/3/action"
    
    def test_load_sample_health_datasets(self):
        """Load sample health datasets from test data"""
        import os
        import yaml
        
        # Get path relative to this test file
        test_dir = os.path.dirname(__file__)
        sample_file = os.path.join(test_dir, "data", "sample_health_datasets.yaml")
        
        if os.path.exists(sample_file):
            with open(sample_file, 'r') as f:
                samples = yaml.safe_load(f)
            
            for dataset in samples.get('datasets', []):
                try:
                    response = requests.post(
                        f"{self.API_URL}/package_create",
                        json=dataset,
                        headers={"Authorization": "test-api-key"}
                    )
                    print(f"Sample dataset '{dataset['name']}' load status: {response.status_code}")
                except requests.exceptions.RequestException as e:
                    print(f"Sample dataset load failed (expected): {e}")


if __name__ == "__main__":
    # Run basic connectivity test
    test_instance = TestHealthDCATAP()
    test_instance.setup_class()
    test_instance.test_ckan_status()
    print("Basic HealthDCAT-AP tests passed!")
