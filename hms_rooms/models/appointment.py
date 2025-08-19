from odoo import models, fields, api


class Appointment(models.Model):
    _inherit = 'appointment'

    flag_book_room = fields.Boolean(compute='_computed_show_create_admission', default=True)

    def _check_patient_admission(self):
        """
        Check if the current patient has any active admissions.

        Searches the 'patient.admission' model for an admission record:
            - Linked to the same patient as the current record.
            - With a state different from 'discharged'.

        Returns:
            bool: True if at least one active admission exists, otherwise False.
        """
        PatientAdmission = self.env['patient.admission']
        admission = PatientAdmission.search([
            ('patient_id', '=', self.patient_id.id),
            ('state', '!=', 'discharged')
        ], limit=1)
        return admission

    @api.depends('state')
    def _computed_show_create_admission(self):
        """
        Compute the value of the 'flag_book_room' field based on the patient's admission state and record state.

        This method checks:
          - If the record's state is one of ['draft', 'done', 'cancelled'], OR
          - If the patient currently has an active admission (state != 'discharged')

        In either of these cases, 'flag_book_room' will be set to True; otherwise, it will be set to False.

        Sets:
            flag_book_room (bool): Indicates whether a "create admission" action should be shown/allowed.
        """
        for rec in self:
            admission = rec._check_patient_admission()
            if rec.state in ['draft', 'cancelled'] or admission:
                rec.flag_book_room = True
            else:
                rec.flag_book_room = False

            print(rec.flag_book_room)

    def action_open_patient_admission(self):
        """
        Open the 'Patient Admission' form pre-filled with patient info.
        """
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Patient Admission',
            'res_model': 'patient.admission',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_patient_id': self.patient_id.id,
            }
        }