# e-invoice-testing-app/app.py
from flask import Flask, request, render_template, jsonify, redirect, url_for
import os
import json
from datetime import datetime
from services.template_service import TemplateService
from services.configuration_service import ConfigurationService
# Include your database utility functions
from database import get_sql_connection

app = Flask(__name__, static_url_path='', static_folder='static', template_folder='templates')
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
    return render_template('add_country_form.html')


@app.route('/add-country', methods=['POST'])
def add_country():
    country = request.form['country']
    region = request.form['region']
    template_type = request.form['template_type'].lower()  # Expecting 'json', 'xml', or 'jinja'

    # Normalize country name for file and directory paths
    country_normalized = country.replace(" ", "_")

    # Create the template files based on the selected type
    create_template_from_base(country_normalized, template_type)

    # Add additional logic as needed, such as updating databases, etc.
    log_activity(f"Added new country: {country} with a {template_type} template")
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
    countries = []
    config_path = os.path.join('config', 'country_vendor_configs')
    for filename in os.listdir(config_path):
        if filename.endswith('.json'):
            country_name = filename[:-5]  # Remove the .json extension to get the country name
            with open(os.path.join(config_path, filename)) as f:
                country_config = json.load(f)
                file_type = country_config.get('format', 'Unknown')  # Extract the file type
            countries.append({'name': country_name, 'file_type': file_type})
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

@app.route('/delete-country/<country_id>', methods=['POST'])
def delete_country(country_id):
    # Implement the logic to delete a country by its ID
    # For demonstration purposes, this will just redirect
    return redirect(url_for('manage_countries'))


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


def create_xml_or_jinja_template(country, template_type):
    # Load the default configuration
    default_config_path = os.path.join('config', 'country_vendor_configs', 'default.json')
    with open(default_config_path, 'r') as file:
        default_config = json.load(file)

    # Determine the file extension based on the template type
    if template_type == 'xml':
        file_extension = '.xml'
    elif template_type == 'jinja':
        file_extension = '.j2'
    else:
        raise ValueError("Unsupported template type")

    # Generate the template content based on the default configuration
    template_content = generate_template_content(default_config, template_type)

    # Save the new template content to a file
    template_path = os.path.join('invoice_templates', template_type, f"{country}{file_extension}")
    with open(template_path, 'w') as file:
        file.write(template_content)



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


def create_template_from_base(country, template_type):
    # Define the path to your base templates
    base_template_path = {
        'json': 'invoice_templates/json/base_template.json',
        'xml': 'invoice_templates/xml/base_template.xml',
        'jinja': 'invoice_templates/jinja/base_template.j2'
    }

    # Check if the base template for the given type exists
    if template_type in base_template_path:
        base_path = base_template_path[template_type]
        if os.path.exists(base_path):
            with open(base_path, 'r') as base_file:
                base_content = base_file.read()

            # Create a country-specific template file from the base template
            country_template_path = os.path.join('invoice_templates', template_type, f"{country}.{template_type}")
            with open(country_template_path, 'w') as country_file:
                country_file.write(base_content)
            print(f"{template_type.capitalize()} template created for {country}.")
        else:
            print(f"Base template for {template_type} does not exist.")
    else:
        print(f"Unsupported template type: {template_type}")


def get_countries_info(directory="config/country_vendor_configs"):
    countries_info = []
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            with open(os.path.join(directory, filename), 'r') as file:
                country_info = json.load(file)
                country_info['filename'] = filename
                countries_info.append(country_info)
    return countries_info





if __name__ == "__main__":
    app.run(debug=True)
