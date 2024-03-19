import os
import json

config_dir = 'config/country_vendor_configs'
template_dir = 'invoice_templates/jinja'

# Ensure the template directory exists
os.makedirs(template_dir, exist_ok=True)

for config_file in os.listdir(config_dir):
    country_code = os.path.splitext(config_file)[0]
    template_file_path = os.path.join(template_dir, f"{country_code}.xml.j2")

    # Check if the template file already exists; if not, create a basic template
    if not os.path.exists(template_file_path):
        with open(template_file_path, 'w') as file:
            file.write(f"<!-- Basic Jinja2 template for {country_code.replace('_', ' ')} -->\n")
            file.write(f"<invoice>\n")
            file.write(f"    <!-- Add your XML structure here -->\n")
            file.write(f"</invoice>")

        print(f"Created Jinja2 template for {country_code}")

print("Jinja2 template generation completed.")
