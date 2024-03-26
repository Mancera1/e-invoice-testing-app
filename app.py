# e-invoice-testing-app/app.py
from flask import Flask, request, render_template, jsonify, redirect, url_for
import os
import json
from datetime import datetime
from services.template_service import TemplateService
from services.configuration_service import ConfigurationService
# Include your database utility functions
from database import get_sql_connection
from flask_wtf.csrf import CSRFProtect
import xml.etree.ElementTree as ET
from xml.dom import minidom

app = Flask(__name__, static_url_path='', static_folder='static', template_folder='templates')
app.config['SECRET_KEY'] = ''
csrf = CSRFProtect(app)

app.config['TEMPLATE_EXTENSIONS'] = ['.j2', '.html']

# Setup for configuration service
config_service = ConfigurationService(config_dir=os.path.join(os.getcwd(), 'config', 'country_vendor_configs'))

# Setup for template service
template_service = TemplateService(templates_directory=os.path.join(os.getcwd(), 'invoice_templates/jinja'))


@app.route('/')
def index():
    return render_template('index.html')



@app.route('/dashboard')
def dashboard():
    total_countries = len(os.listdir('config/country_vendor_configs'))
    total_templates = len(os.listdir('invoice_templates/jinja'))
    recent_activity = fetch_recent_activity_from_database()
    return render_template('dashboard.html',
                           total_countries=total_countries,
                           total_templates=total_templates,
                           recent_activity=recent_activity)


@app.route('/add-country')
def add_country_form():
    with open('config/invoice_fields.json') as f:
        fields = json.load(f)
    return render_template('add_country_form.html', fields=fields)



@app.route('/add-country', methods=['POST'])
def add_country():
    # Existing setup code
    country = request.form['country']
    region = request.form['region']
    template_type = request.form['template_type'].lower()

    # Handle the new field selections
    selected_fields = request.form.getlist('details')  # Assuming 'details' contains the selected fields

    # Create the template based on the base template and selected additional fields
    create_template_from_base_with_fields(country, template_type, region, selected_fields)

    return redirect(url_for('dashboard'))





@app.route('/generate-invoice-form')
def generate_invoice_form():
    return render_template('generate_invoice_form.html')


@app.route('/generate-invoice', methods=['POST'])
def generate_invoice():
    # Extract invoice details from the form
    # Generate the invoice using the details
    # Save invoice to database or send to a third-party service
    log_activity("Invoice generated")
    return jsonify({'message': 'Invoice generated successfully'})


@app.route('/manage-countries')
def manage_countries():
    countries_info_path = os.path.join('config', 'country_vendor_configs', 'countries_info.json')
    if os.path.exists(countries_info_path):
        with open(countries_info_path, 'r') as file:
            countries = json.load(file)
    else:
        countries = []

    return render_template('manage_countries.html', countries=countries)



@app.route('/fetch-invoices')
def fetch_invoices():
    # Implement your logic to fetch invoices here
    return jsonify({'error': 'Endpoint not implemented'}), 501


@app.route('/edit-country/<country_id>', methods=['GET', 'POST'])
def edit_country(country_id):
    # Assuming you have a way to fetch a country by its ID
    # For demonstration purposes, we'll just return a placeholder response
    if request.method == 'POST':
        # Here, you'd update the country's information based on form data
        # This is a placeholder for demonstration
        return redirect(url_for('manage_countries'))
    else:
        # Render an edit form for the country
        # This is a placeholder for demonstration
        country = {"id": country_id, "name": "Placeholder Country", "region": "Placeholder Region"}
        return render_template('edit_country_form.html', country=country)


@app.route('/delete-country/<country_name>', methods=['POST'])
def delete_country(country_name):
    # Normalize country name for file and directory paths
    country_normalized = country_name.replace(" ", "_")

    # Delete the country information from countries_info.json
    delete_country_info(country_normalized)

    # Delete the template file associated with the country
    delete_template_file(country_normalized)

    return redirect(url_for('manage_countries'))


def delete_template_file(country):
    # Assuming you might have different template types for different countries,
    # so we check for each possible type
    template_types = ['json', 'xml', 'jinja']
    # app_root = os.path.join(os.getcwd(), 'apps', 'e-invoice-generator-app', 'invoice_templates')
    app_root = os.path.join(os.getcwd(), 'invoice_templates')
    for template_type in template_types:
        template_path = os.path.join(app_root, template_type, f"{country}.{template_type}")
        if os.path.exists(template_path):
            os.remove(template_path)


def delete_country_info(country):
    config_path = os.path.join(os.getcwd(), 'config', 'country_vendor_configs', 'countries_info.json')
    if os.path.exists(config_path):
        with open(config_path, 'r') as file:
            countries_info = json.load(file)

        # Filter out the country to be deleted
        countries_info = [info for info in countries_info if info['name'] != country]

        with open(config_path, 'w') as file:
            json.dump(countries_info, file, indent=4)

def log_activity(activity):
    connection = get_sql_connection()
    if connection:
        cursor = connection.cursor()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            cursor.execute("INSERT INTO ActivityLog (Activity, Timestamp) VALUES (?, ?)", (activity, timestamp))
            connection.commit()
        finally:
            cursor.close()
            connection.close()


def fetch_recent_activity_from_database():
    query = "SELECT Activity, Timestamp FROM ActivityLog ORDER BY Timestamp DESC LIMIT 10"
    connection = get_sql_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute(query)
            activities = cursor.fetchall()
            return [{'activity': row[0], 'timestamp': row[1].strftime('%Y-%m-%d %H:%M:%S')} for row in activities]
        finally:
            cursor.close()
            connection.close()
    return []


def create_xml_or_jinja_template(country, template_type, selected_fields=None):
    # Load the default configuration
    default_config_path = os.path.join('config', 'country_vendor_configs', 'default.json')
    with open(default_config_path, 'r') as file:
        default_config = json.load(file)

    # Determine the file extension based on the template type
    file_extension = '.xml' if template_type == 'xml' else '.j2'

    base_template_path = os.path.join('invoice_templates', template_type, f"base_template{file_extension}")
    new_template_path = os.path.join('invoice_templates', template_type, f"{country}{file_extension}")

    if template_type == 'xml':
        tree = ET.parse(base_template_path)
        root = tree.getroot()

        # Dynamically update or remove elements based on selected_fields
        for elem in root.findall("./*"):
            if elem.tag not in selected_fields:
                root.remove(elem)
            else:
                # Update placeholders for selected elements if needed
                elem.text = f"{{{{ {elem.tag} }}}}"

        # Add new elements that are in selected_fields but not in the base template
        for field in selected_fields:
            if root.find(f"./{field}") is None:
                ET.SubElement(root, field).text = f"{{{{ {field} }}}}"

        # Generate the new XML content
        template_content = ET.tostring(root, encoding='unicode')
    else:
        # Handle Jinja template generation
        template_content = generate_template_content(default_config, template_type)

    # Save the updated or new template content to a file
    with open(new_template_path, 'w') as file:
        file.write(template_content)

import xml.etree.ElementTree as ET

def create_dynamic_xml_template(selected_fields):
    # Create the root element
    invoice = ET.Element('Invoice')

    # Dynamically add child elements based on selected fields
    for field in selected_fields:
        # For simplicity, adding all fields directly under the root
        # In a real application, you might need to structure this according to your XML schema
        ET.SubElement(invoice, field).text = f"{{{{ {field} }}}}"

    # Convert the ElementTree to a string
    xml_str = ET.tostring(invoice, 'utf-8')

    return xml_str


def generate_template_content(config, template_type):
    # Placeholder for generating Jinja template content based on configuration
    return "{% extends 'base_template.j2' %}\n{% block content %}\n  <!-- Dynamic Content Here -->\n{% endblock %}"



def generate_template_content(config, template_type):
    # This function generates the template content string based on the provided configuration
    # and the desired template type (XML or Jinja).
    # You would need to implement this function to match your specific template structure.
    if template_type == 'xml':
        return "<Invoice>\n  <!-- XML Template Structure -->\n</Invoice>"
    elif template_type == 'jinja':
        return "{% extends 'base_template.j2' %}\n{% block content %}\n  <!-- Jinja Template Structure -->\n{% endblock %}"
    else:
        raise ValueError("Unsupported template type")


def create_json_template(country):
    # Load the default configuration
    default_config_path = os.path.join('config', 'country_vendor_configs', 'default.json')
    with open(default_config_path, 'r') as file:
        default_config = json.load(file)

    # Update the default configuration with country-specific information
    default_config['staticFields']['CountryCode'] = country
    # You can add more country-specific changes to the default_config here

    # Save the updated configuration as a new JSON file
    config_path = os.path.join('config', 'country_vendor_configs', f"{country}.json")
    with open(config_path, 'w') as file:
        json.dump(default_config, file, indent=4)


def create_template(country, template_type):
    base_template_path = os.path.join('invoice_templates', 'base_templates')

    # Check for base template according to the type
    if template_type == 'json':
        base_template_file = os.path.join(base_template_path, 'base_template.json')
    elif template_type == 'xml':
        base_template_file = os.path.join(base_template_path, 'base_template.xml')
    elif template_type == 'jinja':
        base_template_file = os.path.join(base_template_path, 'base_template.j2')
    else:
        raise ValueError("Unknown template type")

    country_template_path = os.path.join('invoice_templates', template_type, f"{country}.{template_type}")

    # Read the base template content
    with open(base_template_file, 'r') as base_template:
        content = base_template.read()

    # Create or update the country-specific template with the base content
    with open(country_template_path, 'w') as country_template:
        country_template.write(content)

    print(f"{template_type.capitalize()} template created for {country}.")


def create_template_from_base(country, template_type, region, selected_details):
    # Define the path to the base template and the destination for the new template
    base_template_path = os.path.join(os.getcwd(), 'invoice_templates', template_type, f'base_template.{template_type}')
    new_template_path = os.path.join(os.getcwd(), 'invoice_templates', template_type, f"{country}.{template_type}")

    # Ensure the base template file exists before attempting to read it
    if not os.path.exists(base_template_path):
        raise FileNotFoundError(f"Base template for {template_type} not found.")

    # Read the base template content
    with open(base_template_path, 'r') as base_template:
        content = base_template.read()

    # Save the base template content as the new template for the country
    with open(new_template_path, 'w') as new_template:
        new_template.write(content)

    # Update the countries_info.json to include the new country's information
    update_country_info(country, template_type, region, os.path.join(os.getcwd(), 'config', 'country_vendor_configs'))
    print(f"Template for {country} created based on the base template for {template_type}.")


def get_countries_info(directory="config/country_vendor_configs"):
    countries_info = []
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            with open(os.path.join(directory, filename), 'r') as file:
                country_info = json.load(file)
                country_info['filename'] = filename
                countries_info.append(country_info)
    return countries_info


@app.route('/edit-template/<template_type>/<country_name>', methods=['GET', 'POST'])
def edit_template(template_type, country_name):
    if request.method == 'POST':
        new_content = request.form['template_content']
        save_template_content(template_type, country_name, new_content)
        return redirect(url_for('manage_countries'))
    else:
        content = get_template_content(template_type, country_name)
        return render_template('edit_template_form.html', content=content, country_name=country_name, template_type=template_type)


def get_template_content(template_type, country_name):
    file_path = os.path.join(app.root_path, 'invoice_templates', template_type, f"{country_name}.{template_type}")
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return "File not found."

def save_template_content(template_type, country_name, content):
    file_path = os.path.join(app.root_path, 'invoice_templates', template_type, f"{country_name}.{template_type}")
    with open(file_path, 'w') as file:
        file.write(content)


def add_or_update_xml_field_correctly(template_content, new_fields):
    """
    Adds or updates XML elements based on new_fields dictionary.
    Ensures elements are placed logically according to the invoice structure.

    Args:
        template_content (str): Original XML content of the invoice template.
        new_fields (dict): Dictionary of new fields to add or update.
                           Keys are field names, values are the content.

    Returns:
        str: Updated XML content.
    """
    root = ET.fromstring(template_content)

    # Example: Assuming all new fields should be within <InvoiceDetails>
    invoice_details = root.find('InvoiceDetails')
    if invoice_details is None:
        invoice_details = ET.SubElement(root, 'InvoiceDetails')

    for field, value in new_fields.items():
        existing = invoice_details.find(field)
        if existing is not None:
            existing.text = value
        else:
            ET.SubElement(invoice_details, field).text = value

    # Convert back to a string while preserving structure
    rough_string = ET.tostring(root, 'utf-8')
    prettified_xml = prettify_xml(rough_string)  # Use the new prettify_xml function here
    return prettified_xml


def create_template_from_base_with_fields(country, template_type, region, selected_details):
    base_template_path = os.path.join(os.getcwd(), 'invoice_templates', template_type, 'base_template.xml')
    new_template_path = os.path.join(os.getcwd(), 'invoice_templates', template_type, f"{country}.xml")

    if not os.path.exists(base_template_path):
        raise FileNotFoundError(f"Base template for {template_type} not found.")

    tree = ET.parse(base_template_path)
    root = tree.getroot()

    # Iterate over selected_details to integrate them into the template
    for detail in selected_details:
        # Check if this detail is already in the base template
        existing_element = root.find(f".//{detail}")
        if existing_element is not None:
            # If the element exists, you may choose to update it
            existing_element.text = f"{{{{ {detail} }}}}"
        else:
            # If the element doesn't exist, add it where it logically belongs
            # This is a simplified example; your logic may vary
            new_element = ET.SubElement(root, detail)
            new_element.text = f"{{{{ {detail} }}}}"

    # Save the modified tree to a new XML file for the country
    tree.write(new_template_path)

    update_country_info(country, template_type, region, os.path.join(os.getcwd(), 'config', 'country_vendor_configs'))
    print(f"Template for {country} updated with selected fields based on the base template for {template_type}.")




def update_country_info(country, template_type, region, config_path):
    countries_info_path = os.path.join(config_path, 'countries_info.json')

    if os.path.exists(countries_info_path):
        with open(countries_info_path, 'r') as file:
            countries_info = json.load(file)
    else:
        countries_info = []

    country_info = {
        "name": country,
        "template_type": template_type,
        "region": region
    }

    # Avoid duplicating country info
    if not any(info['name'] == country for info in countries_info):
        countries_info.append(country_info)

        with open(countries_info_path, 'w') as file:
            json.dump(countries_info, file, indent=4)


def prettify_xml(xml_string):
    """
    Removes excessive whitespace from an XML string.

    Args:
        xml_string (str): The XML string to be prettified.

    Returns:
        str: The prettified XML string with minimized whitespace.
    """
    from xml.dom.minidom import parseString

    # Parse the XML string
    dom = parseString(xml_string)

    # Prettify the XML string
    pretty_xml_as_string = dom.toprettyxml()

    # Post-process to remove blank lines
    lines = pretty_xml_as_string.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]

    # Join the non-empty lines to form the final string
    final_xml_string = '\n'.join(non_empty_lines)

    return final_xml_string



if __name__ == "__main__":
    app.run(debug=True)

