"""
Main entry point for HealthDCAT-AP tests.

This module can be used to run basic connectivity tests or import all test modules.
"""
import sys
import os

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(__file__))

# Import test classes - handle both direct execution and package import
try:
    from .test_integration import TestHealthDCATIntegration  # noqa
    from .test_healthdcat_api import TestHealthDCATAP  # noqa
    from .test_sample_data import TestHealthDataSamples  # noqa
except ImportError:
    from test_integration import TestHealthDCATIntegration  # noqa
    from test_healthdcat_api import TestHealthDCATAP  # noqa
    from test_sample_data import TestHealthDataSamples  # noqa


def run_basic_connectivity_test():
    """Run a basic connectivity test to verify CKAN is accessible."""
    try:
        from .conftest import wait_for_ckan
    except ImportError:
        from conftest import wait_for_ckan
    
    print("Running basic HealthDCAT-AP connectivity test...")
    
    # Wait for CKAN to be ready
    try:
        wait_for_ckan()
        print("Basic HealthDCAT-AP tests passed!")
        return True
    except Exception as e:
        print(f"Basic connectivity test failed: {e}")
        return False


if __name__ == "__main__":
    run_basic_connectivity_test()
