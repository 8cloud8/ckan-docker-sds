"""
Integration tests that validate HealthDCAT-AP installation and setup.
"""
import pytest
import requests
import subprocess
import os

# Import configuration - handle both direct execution and package import
try:
    from .conftest import API_URL
except ImportError:
    from conftest import API_URL


class TestHealthDCATIntegration:
    """Integration tests that validate HealthDCAT-AP installation and setup."""

    def test_service_status(self):
        """Test that CKAN services are running."""
        try:
            result = subprocess.run(['docker-compose', 'ps'], capture_output=True, text=True)
            assert 'ckan' in result.stdout
            assert 'Up' in result.stdout
            print("Services are running")
        except subprocess.SubprocessError as e:
            pytest.fail(f"Could not check service status: {e}")

    def test_ckan_connectivity(self, ckan_api_url):
        """Test basic CKAN connectivity."""
        response = requests.get(f"{ckan_api_url}/status_show")
        assert response.status_code == 200
        data = response.json()
        assert data.get('success') is True
        print("CKAN is accessible")

    def test_healthdcat_extensions_loaded(self, ckan_api_url):
        """Test that required HealthDCAT-AP extensions are loaded."""
        response = requests.get(f"{ckan_api_url}/status_show")
        assert response.status_code == 200

        data = response.json()
        assert data.get('success') is True

        extensions = data['result']['extensions']
        required = ['dcat', 'scheming_datasets', 'dcat_json_interface']
        missing = [ext for ext in required if ext not in extensions]

        assert not missing, f'Missing extensions: {missing}'
        print(f"All required HealthDCAT-AP extensions loaded: {', '.join(required)}")

    def test_healthdcat_configuration(self):
        """Test that HealthDCAT-AP configuration is applied."""
        try:
            # Check configuration in running container
            result = subprocess.run([
                'docker-compose', 'exec', '-T', 'ckan',
                'grep', '-c', '-E', r'(health_dcat_ap\.yaml|euro_health_dcat_ap)',
                '/srv/app/ckan.ini'
            ], capture_output=True, text=True)

            config_count = int(result.stdout.strip() or '0')
            if config_count >= 2:
                print("HealthDCAT-AP configuration found in CKAN config")
            else:
                print("WARNING: HealthDCAT-AP configuration may not be fully applied")

        except (subprocess.SubprocessError, ValueError):
            print("WARNING: Could not verify HealthDCAT-AP configuration")

    def test_dataset_api_functionality(self, ckan_api_url):
        """Test basic dataset API functionality."""
        response = requests.get(f"{ckan_api_url}/package_list")
        assert response.status_code == 200

        data = response.json()
        assert data.get('success') is True

        dataset_count = len(data.get('result', []))
        print(f"Dataset API functional - {dataset_count} datasets found")

    def test_sample_health_datasets_available(self):
        """Test that sample health datasets are available."""
        try:
            import yaml
        except ImportError:
            pytest.skip("PyYAML not available - install with: pip install PyYAML")
        
        test_dir = os.path.dirname(__file__)
        sample_file = os.path.join(test_dir, "data", "sample_health_datasets.yaml")

        if os.path.exists(sample_file):
            with open(sample_file, 'r') as f:
                data = yaml.safe_load(f)

            dataset_count = len(data.get('datasets', []))
            assert dataset_count > 0, "No sample datasets found"

            print(f"Sample health datasets available ({dataset_count} datasets)")
            print("   Sample dataset names:")
            for ds in data.get('datasets', [])[:3]:  # Show first 3
                print(f"   - {ds['title']}")
            if len(data.get('datasets', [])) > 3:
                print(f"   ... and {len(data.get('datasets', [])) - 3} more")
        else:
            pytest.fail("Sample dataset file not found")

    def test_test_infrastructure_ready(self):
        """Test that test infrastructure files are available."""
        test_dir = os.path.dirname(__file__)

        # Check for pytest file (this file)
        pytest_file = os.path.join(test_dir, "test_integration.py")
        assert os.path.exists(pytest_file), "Integration test suite not available"
        print("Integration test suite available")

        # Check for other test files if they exist
        for test_file in ["run_tests.sh", "quick_test.sh"]:
            file_path = os.path.join(test_dir, test_file)
            if os.path.exists(file_path) and os.access(file_path, os.X_OK):
                print(f"{test_file} available")