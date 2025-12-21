CKAN_INI=$(docker-compose exec ckan env | grep CKAN_INI | awk -F= '{print $2}')
docker-compose exec ckan grep -E "(scheming|dcat\.rdf\.profiles)" $CKAN_INI

docker-compose exec ckan ckan config-tool $CKAN_INI | grep -E "(scheming|dcat|presets)"
docker-compose exec ckan grep -n "dcat_date" /srv/app/src/ckanext-dcat/ckanext/dcat/schemas/health_dcat_ap.yaml
docker-compose exec ckan grep -n "presets" /srv/app/src/ckanext-dcat/ckanext/dcat/schemas/presets.yaml

