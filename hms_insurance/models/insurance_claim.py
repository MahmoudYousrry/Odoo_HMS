from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class InsuranceClaim(models.Model):
    _name = 'insurance.claim'
    _description = 'Insurance Claim'

    # ==========================
    # FIELDS
    # ==========================
    name = fields.Char(
        string="Claim Reference",
        required=True,
        readonly=True,
        default='New',
        help="Unique reference for this discount request."
    )

    patient_user_id = fields.Many2one(
        'res.users',
        string="Patient",
        compute="_compute_patient_user_id",
        store=True,
        readonly=True,
        help="The patient associated with the invoice."
    )

    invoice_id = fields.Many2one(
        'account.move',
        string="Related Invoice",
        required=True,
        domain=[('move_type', '=', 'out_invoice')],
        help="The customer invoice related to this insurance claim."
    )

    insurance_company_id = fields.Many2one(
        'insurance.company',
        string="Insurance Company",
        compute="_compute_insurance_company",
        store=True,
        readonly=True,
        help="The insurance company covering this claim."
    )

    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
        help="The currency of the insurance company.",
    )

    total_invoice_amount = fields.Monetary(
        string="Total Invoice",
        related="invoice_id.amount_total",
        store=True,
        help="The total amount of the related invoice.",
        currency_field='currency_id'
    )


    coverage_percentage = fields.Float(
        related="insurance_company_id.coverage_percentage",
        store=True,
        string="Coverage (%)",
        help="The percentage of coverage provided by the insurance company."
    )

    claim_amount = fields.Monetary(
        string="Claim Amount",
        compute="_compute_claim_amount",
        store=True,
        help="The calculated amount to be claimed from the insurance company.",
        currency_field='currency_id'
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('paid', 'Paid')
    ], string="state", default='draft')

    notes = fields.Text(
        string="Notes",
        help="Any additional notes regarding the claim."
    )

    # ==========================
    # COMPUTE METHODS
    # ==========================
    @api.depends('invoice_id')
    def _compute_patient_user_id(self):
        """
        Computes the patient user ID based on the related invoice's partner.
        It first checks for an 'original_patient_invoice_id' to ensure the correct patient is linked.
        """
        users = self.env['res.users']
        for rec in self:
            patient_invoice = rec.invoice_id.original_patient_invoice_id or rec.invoice_id
            partner_id = patient_invoice.partner_id.id
            rec.patient_user_id = users.search([('partner_id', '=', partner_id)], limit=1).id

    @api.depends('patient_user_id')
    def _compute_insurance_company(self):
        """
        Computes the insurance company based on the patient's record.
        """
        patients = self.env['patient']
        for rec in self:
            patient = patients.search([('user_id', '=', rec.patient_user_id.id)], limit=1)
            rec.insurance_company_id = patient.insurance_company_id.id

    @api.depends('total_invoice_amount', 'coverage_percentage', 'invoice_id')
    def _compute_claim_amount(self):
        """
        Calculates the claim amount.
        If the invoice is an 'original_patient_invoice_id', the claim is the full invoice amount.
        Otherwise, it's based on the coverage percentage.
        """
        for rec in self:
            if rec.invoice_id.original_patient_invoice_id:
                rec.claim_amount = rec.total_invoice_amount
            elif rec.coverage_percentage and rec.total_invoice_amount:
                rec.claim_amount = rec.total_invoice_amount * (rec.coverage_percentage / 100.0)
            else:
                rec.claim_amount = 0.0

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
        Submits the insurance claim.
        Posts the related invoice if it's still in draft state.
        """
        for rec in self:
            rec._check_state_transition(
                expected_state='draft',
                required_group_xml_id='hms_insurance.group_insurance_claim_user',
            )
            if rec.invoice_id and rec.invoice_id.state == 'draft':
                rec.invoice_id.action_post()
            rec.state = 'submitted'

    def action_approve(self):
        """
        Approves the insurance claim.
        """
        for rec in self:
            rec._check_state_transition(
                expected_state='submitted',
                required_group_xml_id='hms_insurance.group_insurance_claim_manager',
            )
            rec.state = 'approved'

    def action_reject(self):
        """
        Rejects the insurance claim.
        """
        for rec in self:
            rec._check_state_transition(
                expected_state='submitted',
                required_group_xml_id='hms_insurance.group_insurance_claim_manager',
            )
            rec.state = 'rejected'

    def action_mark_paid(self):
        """
        Marks the insurance claim as paid by registering a payment.
        """
        for rec in self:
            rec._check_state_transition(
                expected_state='approved',
                required_group_xml_id='hms_insurance.group_insurance_claim_accountant',
            )
            rec._register_payment()
            rec.state = 'paid'

    # ==========================
    # PAYMENT LOGIC
    # ==========================
    def _validate_payment(self):
        """Validate requirements for payment registration"""
        if not self.invoice_id:
            raise ValidationError("No related invoice found for payment.")

        if not self.insurance_company_id.payment_journal_id:
            raise ValidationError("No payment journal set for the insurance company.")

    def _register_payment(self):
        """
        Registers a payment from the insurance company against the related invoice.
        This method is intended to be called internally.
        """
        self.ensure_one()

        self._validate_payment()

        partner = self.insurance_company_id.partner_insurance_id
        journal = self.insurance_company_id.payment_journal_id

        payment_context = {
            'active_model': 'account.move',
            'active_ids': self.invoice_id.ids,
            'default_amount': self.claim_amount,
            'default_journal_id': journal.id,
            'default_partner_id': partner.id,
            'default_payment_type': 'inbound',
            'default_partner_type': 'customer',
            'default_communication': f"Insurance Claim Payment: {self.name}",
        }

        payment_register = self.env['account.payment.register'].with_context(**payment_context).create({})
        payment_register.action_create_payments()

    # ==========================
    # OVERRIDES
    # ==========================
    @api.model
    def create(self, vals):
        """
        Overrides the default create method to generate a sequence number for 'name'
        if it's not provided or is 'New'.
        """
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('insurance.claim') or 'New'
        return super().create(vals)
