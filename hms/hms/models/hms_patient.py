from odoo import models, fields,api
from odoo.exceptions import ValidationError
import re

class Patient(models.Model):
    _name = 'hms.patient'
    _rec_name = 'first_name'


    first_name = fields.Char(string="First Name", required=True)
    last_name = fields.Char(string="Last Name", required=True)
    email = fields.Char(string="Email",unique=True)
    birth_date = fields.Date(string="Birth Date", required=True)
    history = fields.Html(string="Medical History")
    pcr = fields.Boolean(string="PCR Test")
    cr_ratio = fields.Float(string="CR Ratio")
    blood_type = fields.Selection([
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-')
    ], string="Blood Type")
    image = fields.Image(string="Profile Image")
    address = fields.Text(string="Address")
    age = fields.Integer(string="Age", compute="_compute_age", store=True)

    department_id = fields.Many2one("hms.department")
    department_capacity = fields.Integer(related='department_id.capacity')
    doctor_ids = fields.Many2many('hms.doctor', string="Doctors")
    log_history_ids = fields.One2many("hms.log.history","patient_log_history_id",string="Log History")
    state = fields.Selection([
        ('undetermined', 'Undetermined'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('serious', 'Serious'),
    ], default='undetermined')

    _sql_constraints = [
        ('unique_email', 'UNIQUE(email)', 'Your email already exists.')
    ]

    @api.constrains('email')
    def _check_email(self):
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        for record in self:
            if record.email and not re.match(email_regex, record.email):
                raise ValidationError('Invalid email format: %s' % record.email)

    @api.constrains('state')
    def _log_state_change(self):
        for record in self:
            record.log_history_ids = [(0, 0, {'description': f"State changed to: {record.state}"})]

    @api.depends('birth_date')
    def _compute_age(self):
        for record in self:
            if record.birth_date:
                today = fields.Date.today()
                record.age = today.year - record.birth_date.year - (
                    (today.month, today.day) < (record.birth_date.month, record.birth_date.day)
                )
            else:
                record.age = 0


    @api.onchange('age')
    def _on_change_age(self):
        if self.age < 30 and self.age != 0 :
            self.pcr = True
            return{
                'warning' : {
                    'title' : 'Hello',
                    'message' : 'pcr is checked'
                },
            }
        else :
            self.pcr = False
