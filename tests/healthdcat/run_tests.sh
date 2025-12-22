#!/bin/bash

# HealthDCAT-AP Test Runner Script
# Runs end-to-end tests for HealthDCAT-AP extension

set -e

echo "=== HealthDCAT-AP Test Suite ==="
echo "Starting HealthDCAT-AP end-to-end tests..."

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
TEST_DIR="${SCRIPT_DIR}"

# Create reports directory if it doesn't exist
mkdir -p "${TEST_DIR}/reports"

# Check if CKAN services are running
echo "Checking CKAN services..."
if ! docker-compose -f "${PROJECT_ROOT}/docker-compose.yml" ps | grep -q "Up"; then
    echo "Starting CKAN services..."
    cd "${PROJECT_ROOT}"
    docker-compose up -d
    echo "Waiting for services to be ready..."
    sleep 30
fi

# Install test dependencies if needed
if [ ! -f "${TEST_DIR}/venv/bin/activate" ]; then
    echo "Creating test virtual environment..."
    python3 -m venv "${TEST_DIR}/venv"
fi

source "${TEST_DIR}/venv/bin/activate"
pip install -r "${TEST_DIR}/requirements.txt"

# Wait for CKAN to be fully ready
echo "Waiting for CKAN to be ready..."
MAX_WAIT=120
WAIT_COUNT=0

while [ $WAIT_COUNT -lt $MAX_WAIT ]; do
    if curl -s -f http://localhost:5001/api/action/status_show > /dev/null 2>&1; then
        echo "CKAN is ready!"
        break
    fi
    echo "Waiting for CKAN... ($((WAIT_COUNT + 1))/$MAX_WAIT)"
    sleep 2
    WAIT_COUNT=$((WAIT_COUNT + 1))
done

if [ $WAIT_COUNT -eq $MAX_WAIT ]; then
    echo "ERROR: CKAN not ready after ${MAX_WAIT} attempts"
    exit 1
fi

# Load sample health datasets
echo "Loading sample health datasets..."
python3 -c "
import yaml
import requests
import json

# Load sample datasets
with open('${TEST_DIR}/data/sample_health_datasets.yaml', 'r') as f:
    data = yaml.safe_load(f)

api_url = 'http://localhost:5001/api/3/action'

print('Loading sample health datasets...')
for dataset in data.get('datasets', []):
    try:
        response = requests.post(
            f'{api_url}/package_create',
            json=dataset,
            headers={'Authorization': 'test-api-key'}
        )
        print(f'Dataset {dataset[\"name\"]}: {response.status_code}')
    except Exception as e:
        print(f'Dataset {dataset[\"name\"]} load failed (expected): {str(e)}')
"

# Run pytest with comprehensive reporting
echo "Running HealthDCAT-AP tests..."
cd "${TEST_DIR}"

# Run tests with different markers
echo "=== Running Core HealthDCAT-AP Tests ==="
python -m pytest test_healthdcat_e2e.py::TestHealthDCATAP -v \
    --html=reports/healthdcat-core-report.html \
    --json-report-file=reports/healthdcat-core-report.json

echo "=== Running Health Data Sample Tests ==="
python -m pytest test_healthdcat_e2e.py::TestHealthDataSamples -v \
    --html=reports/healthdcat-samples-report.html \
    --json-report-file=reports/healthdcat-samples-report.json

# Run all tests together
echo "=== Running Complete Test Suite ==="
python -m pytest test_healthdcat_e2e.py -v \
    --html=reports/healthdcat-complete-report.html \
    --json-report-file=reports/healthdcat-complete-report.json

# Generate summary
echo "=== Test Results Summary ==="
if [ -f "reports/healthdcat-complete-report.json" ]; then
    python3 -c "
import json
with open('reports/healthdcat-complete-report.json', 'r') as f:
    report = json.load(f)

summary = report.get('summary', {})
print(f'Total tests: {summary.get(\"total\", 0)}')
print(f'Passed: {summary.get(\"passed\", 0)}')
print(f'Failed: {summary.get(\"failed\", 0)}')
print(f'Errors: {summary.get(\"error\", 0)}')
print(f'Skipped: {summary.get(\"skipped\", 0)}')
print(f'Duration: {summary.get(\"duration\", 0):.2f}s')

if summary.get('failed', 0) > 0 or summary.get('error', 0) > 0:
    print('\\n❌ Some tests failed. Check reports for details.')
    exit(1)
else:
    print('\\n✅ All tests passed!')
"
fi

echo "=== Test Reports Generated ==="
echo "HTML Report: ${TEST_DIR}/reports/healthdcat-complete-report.html"
echo "JSON Report: ${TEST_DIR}/reports/healthdcat-complete-report.json"
echo ""
echo "HealthDCAT-AP tests completed!"

deactivate