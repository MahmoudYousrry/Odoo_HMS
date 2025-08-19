from odoo import models, fields, api

class RoomService(models.Model):
    _name = 'room.service'
    _description = 'Hospital Room Service'

    # ==========================
    # FIELDS
    # ==========================
    name = fields.Char(
        string='Service Reference',
        required=True,
        readonly=True,
        default='New',
        help="Unique sequence-generated identifier for the room service."
    )

    service_name = fields.Char(
        string='Service Name',
        required=True,
        help="The name of the service provided in the room."
    )

    display_name = fields.Char(
        string="Display Name",
        compute='_compute_display_name',
        store=True,
        help="Name shown in selection fields instead of sequence."
    )

    price = fields.Float(
        string='Price per Hour',
        required=True,
        help="Hourly cost of this service."
    )

    description = fields.Text(
        string='Description',
        help="Detailed description of the service."
    )

    service_type = fields.Selection([
        ('basic', 'Basic'),
        ('optional', 'Optional')
    ], string='Service Type',
       required=True,
       default='optional',
       help="Indicates whether the service is a basic room service or an optional add-on.")


    # ==========================
    # COMPUTE METHODS
    # ==========================
    @api.depends('service_name')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = rec.service_name or rec.name


    # ==========================
    # OVERRIDES
    # ==========================
    @api.model
    def create(self, vals):
        """
        Override create method to generate a unique sequence for 'name'.
        """
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('room.service') or 'New'
        return super(RoomService, self).create(vals)
