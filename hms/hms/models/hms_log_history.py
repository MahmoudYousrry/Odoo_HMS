from odoo import models, fields, api

class HmsLogHistory(models.Model):
    _name = 'hms.log.history'
    _rec_name='description'

    patient_log_history_id = fields.Many2one("hms.patient")
    description = fields.Text(string='Description')

