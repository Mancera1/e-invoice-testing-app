# populate_configurations.py

import json
import os
from services.configuration_service import ConfigurationService

# Assuming country_region_mapping.json lists all countries
country_region_path = os.path.join('config', 'country_region_mapping.json')

def populate_base_configurations():
    config_service = ConfigurationService()

    with open(country_region_path, 'r') as file:
        country_region_mappings = json.load(file)

    for region, countries in country_region_mappings.items():
        for country in countries:
            # Replace spaces with underscores or any other needed transformations
            country_code = country.replace(" ", "_")
            config_service.load_configuration(country_code)


if __name__ == '__main__':
    populate_base_configurations()
