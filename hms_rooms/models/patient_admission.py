from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime


class PatientAdmission(models.Model):
    _name = 'patient.admission'
    _description = 'Patient Admission'

    # ==========================
    # FIELDS
    # ==========================
    name = fields.Char(
        string='Admission ID',
        required=True,
        readonly=True,
        default='New',
        help="Unique sequence-generated identifier for the patient admission."
    )

    patient_id = fields.Many2one(
        'patient',
        string='Patient',
        required=True,
        help="The patient being admitted."
    )

    room_id = fields.Many2one(
        'room',
        string='Room',
        required=True,
        domain="[('room_type', '=', room_type), ('state', 'in', ['available', 'partially_booked'])]",
        help="The room assigned to the patient."
    )

    admission_date = fields.Datetime(
        string='Admission Date',
        readonly=True,
        help="Date and time when the patient was admitted."
    )

    discharge_date = fields.Datetime(
        string='Discharge Date',
        readonly=True,
        help="Date and time when the patient was discharged."
    )

    room_type = fields.Selection([
        ('standard', 'Standard'),
        ('private', 'Private')
    ], string='Room Type',
       required=True,
       help="Type of room to be assigned."
    )

    basic_room_service_ids = fields.Many2many(
        'room.service',
        string='Basic Services',
        compute='_compute_basic_services',
        store=False,
        readonly=True,
        help="Basic services automatically included with the selected room."
    )

    optional_room_service_ids = fields.Many2many(
        'room.service',
        string='Optional Services',
        domain=[('service_type', '=', 'optional')],
        help="Optional services selected in addition to the room's basic services."
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('discharged', 'Discharged'),
        ('cancelled', 'Cancelled'),
    ], string='state',
       default='draft',
       help="Current admission state."
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id.id,
        readonly=True,
        help="Currency used for pricing."
    )

    total_price = fields.Float(
        string='Total Stay Price',
        compute='_compute_total_price',
        store=True,
        help="Total calculated price for the patient's stay."
    )
    show_discharge_button = fields.Boolean(
        compute='_compute_show_discharge_button',
        store=False
    )

    # ==========================
    # HELPERS
    # ==========================
    def _update_room_state(self):
        """Updates the room state based on the number of booked beds."""
        booked = self.room_id.booked_beds
        capacity = self.room_id.bed_count

        if booked <= 0:
            self.room_id.state = 'available'
        elif booked < capacity:
            self.room_id.state = 'partially_booked'
        else:
            self.room_id.state = 'fully_booked'

    def _get_stay_hours(self):
        """Total stay duration in hours, raises error if dates missing."""
        if not (self.admission_date and self.discharge_date):
            raise ValidationError("Admission and discharge dates are required to calculate stay hours.")
        return (self.discharge_date - self.admission_date).total_seconds() / 3600

    def _get_hourly_rate(self):
        """Total hourly rate (room + optional services), raises error if room missing."""
        if not self.room_id:
            raise ValidationError("Room is required to calculate hourly rate.")
        return self.room_id.total_base_hourly_price + sum(s.price for s in self.optional_room_service_ids)

    def _prepare_invoice_lines(self):
        """
        Prepares invoice lines for room charges and optional services.
        """
        stay_hours = self._get_stay_hours()
        invoice_lines = []

        invoice_lines.append({
            'name': f"Room Charge: {self.room_id.name}",
            'quantity': stay_hours,
            'price_unit': self.room_id.total_base_hourly_price,
        })

        for service in self.optional_room_service_ids:
            invoice_lines.append({
                'name': f"Service: {service.service_name or service.name}",
                'quantity': stay_hours,
                'price_unit': service.price,
            })

        return invoice_lines

    # ==========================
    # COMPUTE METHODS
    # ==========================
    @api.depends('room_id')
    def _compute_basic_services(self):
        """
        Retrieves the basic services associated with the selected room.
        """
        for rec in self:
            if rec.room_id:
                rec.basic_room_service_ids = rec.room_id.basic_service_ids.ids
            else:
                rec.basic_room_service_ids = False

    @api.depends('room_id', 'admission_date', 'discharge_date', 'optional_room_service_ids')
    def _compute_total_price(self):
        """Calculate total stay price based on hours stayed and hourly rate."""
        for rec in self:
            if rec.admission_date and rec.discharge_date and rec.room_id:
                if rec._get_stay_hours() <= 0:
                    raise ValidationError(
                        "Discharge date must be after admission date. Stay hours must be positive."
                    )
                rec.total_price = rec._get_stay_hours() * rec._get_hourly_rate()
            else:
                rec.total_price = 0.0

    @api.depends('admission_date', 'state')
    def _compute_show_discharge_button(self):
        """
        Determines whether the 'Discharge' button should be visible.
        The button is shown only if:
          - The admission_date is set and is today or earlier.
        """
        today = fields.Datetime.now()
        for rec in self:
            rec.show_discharge_button = bool(
                rec.admission_date and rec.admission_date.replace(minute=0, second=0, microsecond=0) > today.replace(
                                minute=0, second=0, microsecond=0))
    # ==========================
    # WORKFLOW ACTIONS
    # ==========================
    def _check_state_transition(self, expected_state):
        """
        Method to validate state before performing an action.
        """
        self.ensure_one()

        if self.state != expected_state:
            raise ValidationError(f"This action can only be performed when the admission is in '{expected_state}' state.")

    def action_confirm(self):
        """
        Confirms the patient admission.
        """
        self._check_state_transition('draft')

        if self.room_id.booked_beds >= self.room_id.bed_count:
            raise ValidationError("This room is fully booked.")

        self.room_id.booked_beds += 1
        self._update_room_state()

        self.state = 'in_progress'
        if not self.admission_date:
            self.admission_date = datetime.now()

    def action_discharge(self):
        """
        Discharges the patient.
        Generate and add invoice lines.
        """
        self._check_state_transition('in_progress')

        self.discharge_date = datetime.now()
        self.room_id.booked_beds -= 1
        self._update_room_state()

        self.state = 'discharged'

        invoice_lines = self._prepare_invoice_lines()
        self.env['invoice.service'].add_invoice_items(self.patient_id.id, invoice_lines)

    def action_set_cancelled(self):
        """
        Set the case state to 'cancelled'.
        """

        self.write({'state': 'cancelled'})

    # ==========================
    # OVERRIDES
    # ==========================
    @api.model
    def create(self, vals):
        """
        Overrides create method to generate a unique sequence for 'name'.
        """
        print(vals)
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('patient.admission') or 'New'
        return super().create(vals)
