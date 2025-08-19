from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    original_patient_invoice_id = fields.Many2one('account.move',string="Original Patient Invoice")

    insurance_discount_applied = fields.Boolean(string="Insurance Discount Applied")

    def button_apply_insurance(self):
        for invoice in self:
            if invoice.move_type == 'out_invoice':
                self.env['insurance.invoice'].apply_insurance(invoice)
