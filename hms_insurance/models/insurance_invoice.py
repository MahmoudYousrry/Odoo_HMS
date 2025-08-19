from odoo import models
from odoo.exceptions import ValidationError


class InsuranceInvoice(models.AbstractModel):
    _name = 'insurance.invoice'
    _description = 'Apply insurance in invoices'

    def _get_invoice_lines(self, invoice):
        """Get invoice lines."""
        lines = invoice.invoice_line_ids.filtered(lambda l: l.price_unit > 0)
        if not lines:
            raise ValidationError("No lines found in the invoice.")
        return lines

    def _apply_discount(self, invoice, coverage):
        if invoice.insurance_discount_applied:
            raise ValidationError("Insurance discount has already been applied to this invoice.")

        invoice_lines = self._get_invoice_lines(invoice)
        discount_amount = invoice.amount_total * coverage / 100.0
            
        invoice.write({
            'invoice_line_ids': [(0, 0, {
                'name': 'Insurance Discount',
                'quantity': 1,
                'price_unit': -discount_amount,
                'tax_ids': [(6, 0, [])],
                'account_id': invoice_lines[0].account_id.id,
            })],
            'insurance_discount_applied': True,
        })

    def _create_insurance_invoice(self, invoice, partner, coverage):
        """Create insurance invoice for the insurance company without relying on patient invoice lines."""
        
        insurance_amount = invoice.amount_total * coverage / 100.0

        return self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'invoice_line_ids': [(0, 0, {
                'name': f'Insurance Coverage ({coverage}%)',
                'quantity': 1,
                'price_unit': insurance_amount,
                'tax_ids': [(6, 0, [])],  
                'account_id': invoice.invoice_line_ids[0].account_id.id,
            })],
            'currency_id': invoice.currency_id.id,
            'original_patient_invoice_id': invoice.id,
        })

    def _create_claim(self, insurance_invoice, company):
        """Create insurance claim for the invoice."""
        return self.env['insurance.claim'].create({
            'invoice_id': insurance_invoice.id,
            'insurance_company_id': company.id,
            'state': 'draft'
        })

    def apply_insurance(self, invoice):
        """Apply insurance for the given invoice."""
        patient = self.env['patient'].search([
            ('user_id.partner_id', '=', invoice.partner_id.id)
        ], limit=1)
        
        if not patient.insurance_company_id:
            raise ValidationError(f"Patient {patient.name} has no insurance company assigned.")
        
        company = patient.insurance_company_id
        
        insurance_invoice = self._create_insurance_invoice(
            invoice, company.partner_insurance_id, company.coverage_percentage
        )
        
        self._apply_discount(invoice, company.coverage_percentage)

        
        self._create_claim(insurance_invoice, company)