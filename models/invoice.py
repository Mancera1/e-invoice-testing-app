# e-invoice-testing-app/services/template_service.py

from datetime import datetime
from typing import List, Optional


class InvoiceItem:
    def __init__(self, description: str, quantity: int, unit_price: float, total: float):
        self.description = description
        self.quantity = quantity
        self.unit_price = unit_price
        self.total = total


class Invoice:
    def __init__(self, invoice_number: str, invoice_date: datetime, items: Optional[List[InvoiceItem]], total_amount: float, tax_amount: float, grand_total: float):
        self.invoice_number = invoice_number
        self.invoice_date = invoice_date
        self.items = items
        self.total_amount = total_amount
        self.tax_amount = tax_amount
        self.grand_total = grand_total
