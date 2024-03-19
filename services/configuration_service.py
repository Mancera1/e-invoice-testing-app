# e-invoice-testing-app/services/configuration_service.py
import json
import os


class ConfigurationService:
    def __init__(self, config_dir='config/country_vendor_configs'):
        self.config_dir = config_dir
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)

    def load_configuration(self, country_code):
        config_path = os.path.join(self.config_dir, f"{country_code}.json")
        if not os.path.exists(config_path):
            self.create_default_configuration(country_code, config_path)

        with open(config_path, 'r') as file:
            return json.load(file)

    def create_default_configuration(self, country_code, config_path):
        default_config = {
            "format": "XML",
            "staticFields": {
                "Currency": "USD",
                "CountryCode": country_code
            },
            "fieldsOrder": [
                "InvoiceNumber",
                "InvoiceDate",
                "Items",
                "TotalAmount",
                "TaxAmount",
                "GrandTotal"
            ]
        }
        with open(config_path, 'w') as file:
            json.dump(default_config, file, indent=4)
