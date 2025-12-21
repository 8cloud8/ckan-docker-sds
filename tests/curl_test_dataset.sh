curl -s http://localhost:5001/api/action/status_show | head -5
curl -s http://localhost:5001/api/action/scheming_dataset_schema_show | grep -o '"dataset_type":"[^"]*"' | head -1

curl -s "http://127.0.0.1:5001/api/3/action/scheming_dataset_schema_list"
curl -s "http://127.0.0.1:5001/api/3/action/scheming_dataset_schema_show?type=dataset"
