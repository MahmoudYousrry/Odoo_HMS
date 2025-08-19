from odoo.tests.common import TransactionCase
from datetime import datetime, timedelta

class TestPatientAdmission(TransactionCase):

    def test_admit_and_discharge_patient(self):
        # Create a user for the patient
        user = self.env['res.users'].create({
            'name': 'Patient User',
            'login': 'patient_user',
        })

        # Create patient with required user_id
        patient = self.env['patient'].create({
            'name': 'Test Patient',
            'user_id': user.id,
        })


        # Create clinic
        clinic = self.env['clinic'].create({'name': 'Test Clinic'})

        # Create room
        room = self.env['room'].create({
            'room_type': 'standard',
            'clinic_id': clinic.id,
            'bed_count': 1,
            'base_hourly_price': 50.0,
        })

        # Create optional service
        optional_service = self.env['room.service'].create({
            'service_name': 'Extra Bed',
            'price': 10.0,
            'service_type': 'optional',
        })

        # Admit patient
        admission = self.env['patient.admission'].create({
            'patient_id': patient.id,
            'room_id': room.id,
            'room_type': 'standard',
            'admission_date': datetime.now() - timedelta(hours=5),  # 5 hours stay
            'discharge_date': datetime.now(),
            'optional_room_service_ids': [(6, 0, [optional_service.id])],
        })

        admission._compute_total_price()

        # Check total price (5 hours * (50 base + 10 service))
        expected_price = 5 * (50.0 + 10.0)
        self.assertEqual(admission.total_price, expected_price, "Total price calculation is incorrect")
