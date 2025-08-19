from odoo import models, fields, api
from odoo.exceptions import ValidationError

class InsuranceCompany(models.Model):
    _name = 'insurance.company'
    _description = 'Insurance Company'
    _rec_name = 'partner_insurance_id' 
    
    partner_insurance_id = fields.Many2one(
        'res.partner',
        string="Company Name",
        domain="[('is_company', '=', True), ('is_insurance_company', '=', True)]",
        required=True
    )

    phone = fields.Char(related="partner_insurance_id.phone")
    email = fields.Char(related="partner_insurance_id.email")
    website = fields.Char(related="partner_insurance_id.website")

    coverage_percentage = fields.Float(required=True)

    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    payment_journal_id = fields.Many2one('account.journal', string="Payment Journal")


    @api.constrains('coverage_percentage')
    def _check_coverage_percentage(self):
        """
        Validate that the coverage percentage is within 0–100.
        """
        for record in self:
            if record.coverage_percentage < 0 or record.coverage_percentage > 100:
                raise ValidationError("Coverage percentage must be between 0 and 100.")