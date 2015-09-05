"""
===
PDF
===
"""

import os

from django.core.files.temp import NamedTemporaryFile
from django.utils import timezone
from django.template import loader
import pdfkit

from system.models import Config


def create_invoice_pdf(invoice):
    """
    Generates PDF from the invoice object

    :param Invoice invoice: Invoice object
    :return: file name
    """
    t_file = NamedTemporaryFile(suffix='.pdf', delete=False)
    template = loader.get_template('invoice.html')
    conf = Config.objects.coreconf()
    net_days = conf.get('net_terms', 10)
    template_path = os.path.realpath(os.path.dirname(__file__) + '/templates')

    context = {
        'invoice': invoice,
        'due_date': invoice.date_updated_at + timezone.timedelta(days=net_days),
        'coreconf': conf,
        'template_path': template_path
    }
    rendered = template.render(context)

    pdfkit.from_string(rendered, t_file.name)

    return t_file.name
