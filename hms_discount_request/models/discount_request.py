from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class DiscountRequest(models.Model):
    _name = 'hms.discount.request'
    _description = 'Patient Discount Request'

    # ==========================
    # FIELDS
    # ==========================
    name = fields.Char(
        string="Reference",
        required=True,
        readonly=True,
        default='New',
        help="Unique reference for this discount request."
    )

    invoice_id = fields.Many2one(
        'account.move',
        string="Invoice",
        required=True,
        domain=[('move_type', '=', 'out_invoice'), ('state', '=', 'draft')],
        help="The draft customer invoice for which this discount is requested."
    )

    patient_id = fields.Many2one(
        'patient',
        string="Patient",
        related='invoice_id.patient_id',
        store=True,
        readonly=True,
        help="Patient linked to the selected invoice."
    )

    discount_amount = fields.Monetary(
        string="Discount Amount",
        required=True,
        help="The amount to be discounted from the invoice."
    )

    discount_reason = fields.Text(
        string="Reason",
        required=True,
        help="Reason for requesting this discount."
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('applied', 'Applied'),
    ], string="state", default='draft')

    currency_id = fields.Many2one(
        related='invoice_id.currency_id',
        store=True,
        string="Currency",
        help="Currency of the linked invoice."
    )

    # ==========================
    # CONSTRAINTS
    # ==========================
    @api.constrains('discount_amount', 'invoice_id')
    def _check_discount_amount(self):
        """
        Ensures the discount amount does not exceed the invoice total.
        """
        for rec in self:
            if rec.invoice_id and rec.discount_amount > rec.invoice_id.amount_total:
                raise ValidationError("Discount amount cannot be greater than the invoice total amount.")

    # ==========================
    # WORKFLOW ACTIONS
    # ==========================
    def _check_state_transition(self, expected_state, required_group_xml_id):
        """
        Helper method to ensure correct state transitions and group permissions.
        """
        self.ensure_one()

        if self.state != expected_state:
            raise UserError("You are not allowed to perform this action in the current state.")

        if not self.env.user.has_group(required_group_xml_id):
            raise UserError("You do not have the required permissions to perform this action.")

    def action_submit(self):
        """
        Submits the discount request for approval.
        """
        for rec in self:
            rec._check_state_transition(
                expected_state='draft',
                required_group_xml_id='hms_discount_request.group_discount_request_creator',
            )
            rec.state = 'submitted'

    def action_approve(self):
        """
        Approves the discount request.
        """
        for rec in self:
            rec._check_state_transition(
                expected_state='submitted',
                required_group_xml_id='hms_discount_request.group_discount_request_financial_manager',
            )
            rec.state = 'approved'

    def action_reject(self):
        """
        Rejects the discount request.
        """
        for rec in self:
            rec._check_state_transition(
                expected_state='submitted',
                required_group_xml_id='hms_discount_request.group_discount_request_financial_manager',
            )
            rec.state = 'rejected'

    def action_apply_discount(self):
        """
        Applies the approved discount to the related invoice.
        """
        for rec in self:
            rec._check_state_transition(
                expected_state='approved',
                required_group_xml_id='hms_discount_request.group_discount_request_accountant',
            )

            if rec.invoice_id.state not in ['posted', 'draft']:
                raise ValidationError("Cannot apply discount on a paid or cancelled invoice.")

            rec.invoice_id.write({
                'invoice_line_ids': [(0, 0, {
                    'name': f"Discount {rec.name}",
                    'quantity': 1,
                    'price_unit': -rec.discount_amount,
                    'account_id': rec.invoice_id.invoice_line_ids[0].account_id.id,
                })]
            })
            rec.state = 'applied'


    # ==========================
    # OVERRIDES
    # ==========================
    @api.model
    def create(self, vals):
        """
        Generates a sequence number for 'name' if not set.
        """
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('hms.discount.request') or 'New'
        return super().create(vals)
