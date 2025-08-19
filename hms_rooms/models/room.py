from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Room(models.Model):
    _name = 'room'
    _description = 'Hospital Room'

    # ==========================
    # FIELDS
    # ==========================
    name = fields.Char(
        string='Room Name',
        required=True,
        readonly=True,
        default='New',
        help="Unique sequence-generated identifier for the room."
    )

    display_name = fields.Char(
        string="Display Name",
        compute='_compute_display_name',
        store=True,
        help="Automatically generated name combining room code, type, and clinic."
    )

    clinic_id = fields.Many2one(
        'clinic',
        string='Clinic',
        required=True,
        help="The clinic where this room is located."
    )

    room_type = fields.Selection([
        ('standard', 'Standard'),
        ('private', 'Private')
    ], string='Room Type', required=True, help="Type of the room.")

    bed_count = fields.Integer(
        string='Number of Beds',
        required=True,
        default=1,
        help="Total number of beds available in this room."
    )

    basic_service_ids = fields.Many2many(
        'room.service',
        string='Basic Services',
        domain=[('service_type', '=', 'basic')],
        help="List of basic services included with the room."
    )

    base_hourly_price = fields.Float(
        string='Base Hourly Price',
        help="Base cost per hour for using this room (excluding services)."
    )

    total_base_hourly_price = fields.Float(
        string='Total Base Hourly Price',
        compute='_compute_total_base_hourly_price',
        store=True,
        help="Base price per hour including the price of all basic services."
    )

    state = fields.Selection([
        ('available', 'Available'),
        ('partially_booked', 'Partially Booked'),
        ('fully_booked', 'Fully Booked'),
        ('under_maintenance', 'Under Maintenance'),
        ('out_of_service', 'Out of Service')
    ], string='state', default='available', readonly=True,
       help="Current availability state of the room.")

    booked_beds = fields.Integer(
        string='Booked Beds',
        default=0,
        help="Number of beds currently booked."
    )

    available_beds = fields.Integer(
        string='Available Beds',
        compute='_compute_available_beds',
        store=True,
        help="Number of beds still available for booking."
    )

    # ==========================
    # ONCHANGE METHODS
    # ==========================
    @api.onchange('bed_count', 'room_type')
    def _onchange_private_room_bed_count(self):
        if self.room_type == 'private' and self.bed_count > 1:
            return {
                'warning': {
                    'title': "Warning",
                    'message': "This is a private room. It is recommended to have only one bed. Are you sure you want to add more than one?"
                }
            }

    # ==========================
    # COMPUTE METHODS
    # ==========================
    @api.depends('base_hourly_price', 'basic_service_ids')
    def _compute_total_base_hourly_price(self):
        """
        Calculates the total hourly price by adding the base price
        and the prices of all linked basic services.
        """
        for rec in self:
            total_price = rec.base_hourly_price or 0.0
            for service in rec.basic_service_ids:
                total_price += service.price
            rec.total_base_hourly_price = total_price

    @api.depends('bed_count', 'booked_beds')
    def _compute_available_beds(self):
        """
        Calculates the number of available beds by subtracting booked beds
        from the total bed count.
        """
        for rec in self:
            rec.available_beds = rec.bed_count - rec.booked_beds

    @api.depends('name', 'room_type', 'clinic_id')
    def _compute_display_name(self):
        """
        Generates a display name in the format:
        <Room Code> — <Room Type> — <Clinic Name>
        """
        for rec in self:
            room_type_label = dict(rec._fields['room_type'].selection).get(rec.room_type, '')
            clinic_name = rec.clinic_id.name or ''
            rec.display_name = f"{rec.name} — {room_type_label} — {clinic_name}"

    # ==========================
    # WORKFLOW ACTIONS
    # ==========================
    def _check_state_transition(self, expected_state):
        """
        Helper method to validate state before performing an action.
        """
        self.ensure_one()

        if self.state != expected_state:
            raise ValidationError(f"This action can only be performed when the room is in '{expected_state}' state.")

    def action_set_under_maintenance(self):
        """
        Set room state to Under Maintenance.
        """
        self._check_state_transition('available')
        self.state = 'under_maintenance'

    def action_set_out_of_service(self):
        """
        Set room state to Out of Service.
        """
        self._check_state_transition('available')
        self.state = 'out_of_service'

    def action_set_available_from_maintenance(self):
        """
        Make the room available after maintenance.
        """
        self._check_state_transition('under_maintenance')
        self.state = 'available'

    def action_set_available_from_out_of_service(self):
        """
        Make the room available after being out of service.
        """
        self._check_state_transition('out_of_service')
        self.state = 'available'

    # ==========================
    # OVERRIDES
    # ==========================
    @api.model
    def create(self, vals):
        """
        Overrides create method to generate a unique sequence number for 'name'
        if it's not provided.
        """
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('room.sequence') or 'New'
        return super().create(vals)
