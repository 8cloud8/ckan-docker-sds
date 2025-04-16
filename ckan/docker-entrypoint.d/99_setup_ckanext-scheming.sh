#!/bin/bash

if [[ $CKAN__PLUGINS == *"scheming_datasets"* ]]; then

   # pip install -e "git+https://github.com/ckan/ckanext-scheming.git#egg=ckanext-scheming"
   echo "Setting up scheming datasets"
   ckan config-tool $CKAN_INI "scheming.dataset_schemas = https://raw.githubusercontent.com/ckan/ckanext-scheming/refs/heads/master/ckanext/scheming/ckan_dataset.yaml"

else
   echo "Not configuring scheming_datasets"
fi
