#!/bin/bash

if [[ $CKAN__PLUGINS == *"scheming_datasets"* ]]; then
   echo "Setting up HealthDCAT-AP schema"
   # Configure HealthDCAT-AP schema from ckanext-dcat
   ckan config-tool $CKAN_INI "scheming.dataset_schemas = ckanext.dcat.schemas:health_dcat_ap.yaml"
   # Include both ckanext-scheming and ckanext-dcat presets
   ckan config-tool $CKAN_INI "scheming.presets = ckanext.scheming:presets.json ckanext.dcat.schemas:presets.yaml"
   # Configure HealthDCAT-AP RDF profile
   ckan config-tool $CKAN_INI "ckanext.dcat.rdf.profiles = euro_dcat_ap euro_health_dcat_ap"
 else
   echo "Not configuring scheming_datasets"
fi
