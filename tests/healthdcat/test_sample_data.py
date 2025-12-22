"""
Tests for sample health datasets functionality.
"""
import pytest
import requests
import os

# Import configuration - handle both direct execution and package import
try:
    from .conftest import API_URL
except ImportError:
    from conftest import API_URL


class TestHealthDataSamples:
    """Tests for sample health datasets."""

    def test_load_sample_health_datasets(self, ckan_api_url):
        """Load sample health datasets from test data."""
        try:
            import yaml
        except ImportError:
            pytest.skip("PyYAML not available - install with: pip install PyYAML")

        # Get path relative to this test file
        test_dir = os.path.dirname(__file__)
        sample_file = os.path.join(test_dir, "data", "sample_health_datasets.yaml")

        if os.path.exists(sample_file):
            with open(sample_file, 'r') as f:
                samples = yaml.safe_load(f)

            for dataset in samples.get('datasets', []):
                try:
                    response = requests.post(
                        f"{ckan_api_url}/package_create",
                        json=dataset,
                        headers={"Authorization": "test-api-key"}
                    )
                    print(f"Sample dataset '{dataset['name']}' load status: {response.status_code}")
                except requests.exceptions.RequestException as e:
                    print(f"Sample dataset load failed (expected): {e}")
        else:
            pytest.skip("Sample datasets file not found")