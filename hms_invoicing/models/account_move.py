from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    patient_id = fields.Many2one('patient', string="Patient", ondelete='restrict')

    @api.model_create_multi
    def create(self, vals_list):
        """
        Ensure invoices linked to a patient are also linked to the
        patient's related partner (via patient.user_id.partner_id).
        """
        for vals in vals_list:
            patient_id = vals.get('patient_id')
            if patient_id and not vals.get('partner_id'):
                patient = self.env['patient'].browse(patient_id)
                if patient.exists() and patient.user_id.partner_id:
                    vals['partner_id'] = patient.user_id.partner_id.id
        return super().create(vals_list)

    @api.depends('patient_id.name', 'name', 'amount_total', 'state', 'currency_id')
    def _compute_display_name(self):
        for rec in self:
            parts = [
                rec.patient_id.name or rec.name or 'Patient name',
                f"Total: {rec.amount_total:.2f} {rec.currency_id.name}" if rec.currency_id else '',
                f"state: {dict(rec._fields['state'].selection).get(rec.state, rec.state)}",
            ]
            rec.display_name = " | ".join(filter(None, parts))