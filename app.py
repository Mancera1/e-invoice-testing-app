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


@app.route('/add-country-form')
def add_country_form():
    return render_template('add_country_form.html')


@app.route('/add-country')
def add_country():
    return render_template('add_country_form.html')


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
    countries = os.listdir('config/country_vendor_configs')
    return render_template('manage_countries.html', countries=countries)


@app.route('/fetch-invoices')
def fetch_invoices():
    # Implement your logic to fetch invoices here
    return jsonify({'error': 'Endpoint not implemented'}), 501


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


if __name__ == "__main__":
    app.run(debug=True)
