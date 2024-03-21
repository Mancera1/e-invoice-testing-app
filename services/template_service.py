# e-invoice-testing-app/services/template_service.py

import os
from jinja2 import Environment, FileSystemLoader
from string import Template
import re


class TemplateService:
    def __init__(self, templates_directory='invoice_templates/jinja'):
        # Initialize Jinja2 environment to point to the directory where your Jinja templates are stored.
        self.jinja_env = Environment(loader=FileSystemLoader(templates_directory), autoescape=True)

    def render_template(self, template_name, context):
        """
        Renders a Jinja2 template with the given context.

        :param template_name: Name of the Jinja2 template file. Assumes the format "country.format.j2"
                               e.g., "El_Salvador.xml.j2" for an XML template for El Salvador.
        :param context: A dictionary with data to render the template.
        """
        # Ensure the template name includes the '.j2' extension
        if not template_name.endswith('.j2'):
            template_name += '.j2'

        template = self.jinja_env.get_template(template_name)
        return template.render(context)


    def get_template(self, country, format, use_jinja=False):
        """
        Fetches the template; if use_jinja is True, it expects a Jinja2 template.
        """
        template_path = os.path.join(format, f"{country}.{format}")
        if use_jinja:
            # For Jinja2 templates, we just need to return the template path, as Jinja will load it directly.
            return template_path
        else:
            # For basic string Template, load and return its content.
            full_path = os.path.join(self._templates_directory, template_path)
            if not os.path.exists(full_path):
                raise FileNotFoundError(f"Template for {country} in {format} format not found at {full_path}.")
            with open(full_path, 'r') as file:
                return file.read()

    def parse_template(self, invoice, template_content, use_jinja=False):
        """
        Parses the template with the given invoice data.
        If use_jinja is True, it uses Jinja2 for parsing.
        """
        if use_jinja:
            # Use Jinja2 for parsing
            template = self.jinja_env.get_template(template_content)
            return template.render(invoice=invoice.__dict__)
        else:
            # Fallback to the basic string Template for substitution
            template = Template(template_content)

            # Prepare data for substitution, handling items separately
            data = invoice.__dict__.copy()
            data['InvoiceDate'] = data['InvoiceDate'].strftime('%Y-%m-%d')

            items_content = ''
            if invoice.items:
                for item in invoice.items:
                    item_data = item.__dict__.copy()
                    item_template = '...'  # Define your item template here
                    item_content = Template(item_template).substitute(item_data)
                    items_content += item_content

            data['Items'] = items_content

            return template.safe_substitute(data)
