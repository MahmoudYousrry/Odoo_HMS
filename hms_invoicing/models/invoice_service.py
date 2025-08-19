from odoo import models, api
from odoo.exceptions import ValidationError

class InvoiceService(models.AbstractModel):
    _name = 'invoice.service'
    _description = 'Patient Invoice Service Handler'

    @api.model
    def get_or_create_draft_invoice(self, patient_id):
        """
        Retrieve an existing draft invoice for the patient’s partner
        (via user_id.partner_id), or create a new one if none exists.
        """
        if not patient_id:
            raise ValidationError("Patient ID is required to create an invoice.")

        patient = self.env['patient'].browse(patient_id)
        partner_id = patient.user_id.partner_id.id

        invoice = self.env['account.move'].search([
            ('partner_id', '=', partner_id),
            ('state', '=', 'draft'),
            ('move_type', '=', 'out_invoice'),
        ], limit=1)

        if not invoice:
            invoice = self.env['account.move'].create({
                'move_type': 'out_invoice',
                'partner_id': partner_id,
                'patient_id': patient.id,
            })

        return invoice

    @api.model
    def append_invoice_lines(self, invoice, lines):
        """
        Append invoice lines to a draft invoice.
        """
        if not invoice or invoice.state != 'draft':
            raise ValidationError("Invoice must be in draft state to append lines.")

        new_lines = []
        for line in lines:
            price = line.get('price_unit', 0)
            if price < 0:
                raise ValidationError("Invalid price in invoice line.")
            quantity = line.get('quantity', 1.0)
            new_lines.append((0, 0, {
                'name': line.get('name') or 'Service',
                'quantity': quantity,
                'price_unit': price,
            }))

        invoice.write({'invoice_line_ids': new_lines})

    @api.model
    def add_invoice_items(self, patient_id, lines):
        """
        Create or update an invoice with lines for the patient.
        """
        invoice = self.get_or_create_draft_invoice(patient_id)
        self.append_invoice_lines(invoice, lines)
        return invoice
