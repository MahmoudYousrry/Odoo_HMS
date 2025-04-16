from odoo import models, fields, api
from odoo.exceptions import ValidationError

class CrmPatientInherit(models.Model):
    _inherit = 'res.partner'

    related_patient_id = fields.Many2one('hms.patient', string="Related Patient")


    @api.constrains('email')
    def _check_email_uniqueness_with_patients(self):
        for record in self:
            if record.email:
                existing_patient = self.env['hms.patient'].search([('email', '=', record.email)], limit=1)
                if existing_patient:
                    raise ValidationError("This email is already associated with a patient and cannot be used for a customer.")

    def unlink(self):
        for rec in self:
            if rec.related_patient_id:
                raise ValidationError("You can't delete a customer that is linked to a patient.")
        return super(CrmPatientInherit, self).unlink()
