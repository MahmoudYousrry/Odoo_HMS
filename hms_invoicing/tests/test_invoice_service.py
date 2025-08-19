from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

class TestInvoiceService(TransactionCase):

    def setUp(self):
        super().setUp()
        self.Patient = self.env['patient']
        self.InvoiceService = self.env['invoice.service']
        self.Partner = self.env['res.partner']

        self.partner = self.Partner.create({
            'name': 'Patient Test',
            'phone': '123456789',
        })

        self.patient = self.Patient.create({
            'name': 'Patient Test',
            'partner_id': self.partner.id,
        })

    def test_add_single_invoice_item(self):

        """
        Test adding a single invoice line using add_invoice_items.
        """

        lines = [{
            'name': 'ECG Test',
            'price_unit': 120.0,
            'quantity': 1,
        }]
        invoice = self.InvoiceService.add_invoice_items(self.patient.id, lines)

        self.assertEqual(invoice.state, 'draft')
        self.assertEqual(len(invoice.invoice_line_ids), 1)
        self.assertEqual(invoice.invoice_line_ids[0].name, 'ECG Test')
        self.assertEqual(invoice.invoice_line_ids[0].price_unit, 120.0)
        self.assertEqual(invoice.invoice_line_ids[0].quantity, 1.0)

    def test_add_multiple_invoice_items(self):

        """
        Test adding multiple invoice lines using add_invoice_items.
        """

        lines = [
            {'name': 'Blood Test', 'price_unit': 80.0, 'quantity': 1},
            {'name': 'MRI Scan', 'price_unit': 300.0, 'quantity': 1},
            {'name': 'Doctor Fees', 'price_unit': 150.0, 'quantity': 1},
        ]
        invoice = self.InvoiceService.add_invoice_items(self.patient.id, lines)

        self.assertEqual(invoice.state, 'draft')
        self.assertEqual(len(invoice.invoice_line_ids), 3)
        names = invoice.invoice_line_ids.mapped('name')
        self.assertIn('Blood Test', names)
        self.assertIn('MRI Scan', names)
        self.assertIn('Doctor Fees', names)
        self.assertAlmostEqual(invoice.amount_total, 530.0)